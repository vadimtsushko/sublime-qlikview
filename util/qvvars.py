# -*- encoding: UTF-8 -*-
import os
import re
import xml.etree.ElementTree as etree
import csv
import sys
import datetime

class QvVarFileReader:
    ALLOWED_TAGS = ('Label','Comment', 'Definition','BackgroundColor','FontColor','TextFormat',
        'Tag','Separator','#define', 'Macro','Description','EnableCondition',
        'ShowCondition','SortBy','VisualCueUpper','VisualCueLower')
    FIELDS_TO_SKIP = ('Definition','Tag','SET','LET','command','name','separator','Macro','Description')
    NAME_MAP = {}

    line_template = re.compile(r'^(?P<key>\w+?):\s*(?P<val>.*)$')
    define_template = re.compile(r'^#define\s*(?P<key>\S+)\s+(?P<val>.*)$')
    param_template = re.compile(r'^\s*\-\s*(?P<val>.*)$')

    linenum = 0
    defs = {}
    macro = []
    output = []
    define_directives = {}
    moduleSettings = None
    def __init__(self,moduleSettings):
        self.linenum = 0
        self.defs = {}
        self.macro = []
        self.output = []
        self.define_directives = {}
        self.moduleSettings = moduleSettings

    def put_row(self, key, value, command, comment, priority):
            self.output.append([command.upper(), key ,value, comment, priority])
    def parse_content(self,text):
        self.NAME_MAP = {}
        mappings = self.moduleSettings.get('mappings',{})
        for tag in self.ALLOWED_TAGS:
            self.NAME_MAP[tag] = mappings.get(tag,tag);
        self.NAME_MAP['separator'] = self.moduleSettings.get('separator','.')
        expression = {}
        defs = {}
        define_directives = {}
        self.linenum = 0
        self.macro = []
        self.output = []
        def expand_macro():
            if defs.get(self.macro[0]) is None:
                raise SyntaxError('Parsing error: definition for macro `%s` is not found' % self.macro[0])
            result = defs[self.macro[0]]
            i = 1
            while i < len(self.macro):
                param = self.macro[i]
                subs = '$%s' % str(i)
                if not subs in result:
                    print('macro',self.macro)
                    raise SyntaxError('Parsing error: definition for macro `%s` does not contain substring %s' % (self.macro[0],subs))    
                result = result.replace(subs,param)
                i = i + 1
            return result
        def init_expression():
            self.macro = []
            expression = {}
        def process_expression(exp):
            if exp == {}:
                return None
            if exp.get('name') is None:
                return'Parsing error: `name` property is absent'
            if exp['name'] in defs:
                return 'Parsing error: duplicate expression with name `%s`' % exp['name']
            if exp.get('Definition') is not None and exp.get('Macro') is not None:
               return 'Parsing error: Expression have defined both `definition` and `macro` property. Something one must be defined'
            if exp.get('Definition') is None:
                if  exp.get('Macro') is None:
                    return 'Parsing error: Expression `%s` have not defined `definition` or `macro` property' % exp['name']
                exp['Definition'] = expand_macro()
            local_def = exp['Definition']
            for k, v in define_directives.items():
                local_def = local_def.replace(k,v)
            exp['Definition'] = local_def
            defs[exp['name']] = exp['Definition']
            comment = exp.get('Description')
            tag = exp.get('Tag')
            command = exp.get('command')
            name = exp.get('name')
            self.put_row(name,expression['Definition'],command, comment, tag)
            for key in exp.keys():
                if key not in self.FIELDS_TO_SKIP:
                    varName = '%s%s%s' % (name,self.NAME_MAP['separator'],self.NAME_MAP[key])
                    self.put_row(varName,expression[key],'SET', '', tag) 
            init_expression()
            return None
        def parse_val(text):
            if text == None:
                return ''
            return text.strip()
        def parse_define_directive(line):
            match = self.define_template.match(line)
            if match is None:
                raise SyntaxError('Invalid define specification')
            m = match.groupdict()
            define_key = m['key'].strip()
            define_val = m['val'].strip()
            if (define_key == '' or define_val == ''):
                print(line)
                raise SyntaxError('Invalid define specification')
            define_directives[define_key] = define_val
        current_field = None
        for line in text.splitlines():
            self.linenum = self.linenum + 1
            if (line.startswith('#')):
                parse_define_directive(line)
                continue
            match = self.line_template.match(line)
            if match is None:
                line = line.strip()
                if line == '---':
                    error = process_expression(expression)
                    if error is not None:
                        raise SyntaxError(error)
                    expression = {}
                    continue
                if current_field is not None:
                    if current_field == 'Macro':
                        if len(self.macro) == 0:
                           self.macro.append(expression['Macro']) 
                        param_match = self.param_template.match(line)
                        if param_match is None:
                            raise SyntaxError('Unexpected macro param format: "%s" for macro "%s"' % (line,self.macro[1]))
                        else:
                            self.macro.append(param_match.groupdict()['val'].strip())
                            continue            
                    else:     
                        expression[current_field] += ' ' + line
                        continue
                raise SyntaxError('Unexpected format')       
            m = match.groupdict()
            m['key'] = m['key'].strip()
            m['val'] = m['val'].strip()
            current_field = m['key']
            if m['key'] == 'SET' or m['key'] == 'LET':
                expression['name'] =  m['val']   
                expression['command'] = m['key']
            elif m['key'] in self.ALLOWED_TAGS:
                expression[m['key']] = m['val']
            else:
                if m['key'] == 'Macro':
                    self.macro.append(m['val'])
                    expression['Macro'] = self.macro
                else:
                    raise SyntaxError('Unexpected QlikView expression property: "%s"' % m['key'])
        error = process_expression(expression)
        if error is not None:
            raise SyntaxError(error)  
        return None
class QlikViewCommandExpander:
    expressions = []
    exp_dict = {}
    output = []
    VAR_PATTERN = re.compile('\\$\\((?P<key>[^=][^)]+)\\)')
    def __init__(self, expressions, expressionsToExpand = None):
        self.expressions = list(expressions)
        if expressionsToExpand is not None:
            self.expressionsToExpand = list(expressionsToExpand)
        for exp in self.expressions:
            if '.' in exp[0]:
                continue
            self.exp_dict[exp[0]] = exp[1]
    def expand(self):
        for exp in self.expressions:
            expanded = exp[1]
            for match in self.VAR_PATTERN.finditer(exp[1]):
                variable = match.groupdict()['key']
                if variable in self.exp_dict:
                    replace_string = self.exp_dict[variable]
                    expanded = expanded.replace('$(%s)' % variable, replace_string) 
                else:
                    print('Cannot find variable: %s for expression %s' % (variable,exp[0]))
            self.output.append((exp[0],expanded))
