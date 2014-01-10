import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as etree
import StringIO
import csv

EXT_QLIKVIEW_VARS  = ".qlikview-vars"
EXT_QLIKVIEW_VARS_TABLE = ".csv"
ALLOWED_TAGS = ('label','comment', 'definition','background','condition',
    'search_tag','totals_label','separator','#define')
FIELDS_TO_SKIP = ('definition','tag','set','let','command','name', 'separator')
NAME_MAP = {}

line_template = re.compile(r'^(?P<key>\w+?):\s+(?P<val>.+)$')
define_template = re.compile(r'^#define\s*(?P<key>\w*)\s*(?P<val>.*)$')
param_template = re.compile(r'^\s*\-\s*(?P<val>.*)$')

linenum = 0
defs = {}
macro = []
output = []
define_directives = {}
def parse_expression_file(path, name, text):
    global linenum
    global defs
    global define_directives
    global macro
    global output
    global NAME_MAP
    NAME_MAP = {}
    for tag in ALLOWED_TAGS:
        NAME_MAP[tag] = tag
        NAME_MAP['separator'] = '.'
    expression = {}
    defs = {}
    define_directives = {}
    linenum = 0
    macro = []
    output = []
    def expand_macro():
        if defs.get(macro[0]) is None:
            raise SyntaxError('Parsing error: definition for macro `%s` is not found' % macro[0])
        result = defs[macro[0]]
        i = 1
        while i < len(macro):
            param = macro[i]
            subs = '$%s' % str(i)
            if not subs in result:
                raise SyntaxError('Parsing error: definition for macro `%s` does not contain substring %s' % (macro[0],subs))    
            result = result.replace(subs,param)
            i = i + 1
        return result
    def init_expression():
        global macro
        macro = []
        expression = {}
    def process_expression(exp):
        global macro
        global defs
        if exp == {}:
            return None
        if exp.get('name') is None:
            return'Parsing error: `name` property is absent'
        if exp['name'] in defs:
            return 'Parsing error: duplicate expression with name `%s`' % unicode(exp['name'])
        if exp.get('definition') is not None and exp.get('macro') is not None:
           return 'Parsing error: Expression have defined both `definition` and `macro` property. Something one must be defined'
        if exp.get('definition') is None:
            if  exp.get('macro') is None:
                return 'Parsing error: Expression `%s` have not defined `definition` or `macro` property' % unicode(exp['name'])
            exp['definition'] = expand_macro()
        local_def = exp['definition']
        for k, v in define_directives.items():
            local_def = local_def.replace(k,v)
        exp['definition'] = local_def
        defs[exp['name']] = exp['definition']
        comment = exp.get('comment')
        tag = exp.get('search_tag')
        command = exp.get('command')
        name = exp.get('name')
        if name == '__NAME_MAP__':
            for key in exp.keys():
               NAME_MAP[key] = exp[key]
        else:    
            putRow(name,expression['definition'],command, comment, tag)
            for key in exp.keys():
                if key not in FIELDS_TO_SKIP:
                    varName = '%s%s%s' % (name,NAME_MAP['separator'],NAME_MAP[key]) 
                    putRow(varName,expression[key],'SET', '', tag) 
        init_expression()
        return None
    def putRow(key, value, command, comment, priority):
        output.append(['%s %s' % (command.upper(), key) ,value, comment, priority])
    def parse_val(text):
        return text.strip()
    def parse_define_directive(line):
        match = define_template.match(line)
        if match is None:
            raise SyntaxError('Invalid define specification')
        m = match.groupdict()
        define_key = m['key'].strip()
        define_val = m['val'].strip()
        if (define_key == '' or define_val == ''):
            raise SyntaxError('Invalid define specification')
        define_directives[define_key] = define_val
    current_field = None
    for line in text.splitlines():
        linenum = linenum + 1
        if (line.startswith('#')):
            parse_define_directive(line)
            continue
        match = line_template.match(line)
        if match is None:
            line = line.strip()
            if line == '---':
                error = process_expression(expression)
                if error is not None:
                    raise SyntaxError(error)
                expression = {}
                continue
            if current_field is not None:
                if current_field == 'macro':
                    param_match = param_template.match(line)
                    if param_match is None:
                        raise SyntaxError('Unexpected macro param format: "%s" for macro "%s"' % (line,macro[1]))
                    else:
                        macro.append(param_match.groupdict()['val'].strip())
                        continue            
                else:     
                    expression[current_field] += ' ' + line
                    continue
            SyntaxError('Unexpected format')       
        m = match.groupdict()
        m['key'] = m['key'].strip()
        m['val'] = m['val'].strip()
        current_field = m['key']
        if m['key'] == 'set' or m['key'] == 'let':
            expression['name'] =  m['val']   
            expression['command'] = m['key']
        elif m['key'] in ALLOWED_TAGS:
            expression[m['key']] = m['val']
        else:
            if m['key'] == 'macro':
                macro.append(m['val'])
                expression['macro'] = macro
            else:
                raise SyntaxError('Unexpected QlikView expression property: "%s"' % m['key'])
    error = process_expression(expression)
    if error is not None:
        raise SyntaxError(error)  
    return None


def regenerate_tab_file_content(path, onload=False):
    global linenum
    (name, ext) = os.path.splitext(os.path.basename(path))
    try:
        f = open(path, 'r')
    except:
        print "QlikViewExpression: Unable to read `%s`" % path
        return None
    else:
        read = f.read()
        f.close()
    try:
        parse_expression_file(path, name, read)
    except Exception as e:
        msg  = isinstance(e, SyntaxError) and str(e) or "Error parsing QlikView expression "
        msg += " in file `%s` line: %d" % (path, linenum)
        if onload:
            # Sublime Text likes "hanging" itself when an error_message is pushed at initialization
            print "Error: " + msg
        else:
            sublime.error_message(msg)
        if not isinstance(e, SyntaxError):
            print e  # print the error only if it's not raised intentionally
        return None

def regenerate_expression_tab_file(path, onload=False, force=False):

    (sane_path, path) = (path, swap_extension(path))
    # Generate XML
    regenerate_tab_file_content(sane_path, onload=onload)

    write = True
 
    if write:
        try:
            f = open(path, 'wb')
        except:
            print "QlikView expression: Unable to open `%s`" % path
        else:
            writer = csv.writer(f)
            writer.writerow(['VariableName','VariableValue','Comments','Priority'])
            for row in output:
                writer.writerow(row)
            f.close()


def swap_extension(path):
    "Swaps `path`'s extension between `EXT_QLIKVIEW_VARS` and `EXT_QLIKVIEW_VARS_TABLE`"

    if path.endswith(EXT_QLIKVIEW_VARS):
        return path.replace(EXT_QLIKVIEW_VARS, EXT_QLIKVIEW_VARS_TABLE)
    else:
        return path.replace(EXT_QLIKVIEW_VARS_TABLE, EXT_QLIKVIEW_VARS)


class QlikViewExpression(sublime_plugin.EventListener):
    """Save expressions in tabular format with extension EXT_QLIKVIEW_VARS_TABLE 
    along with current expression file in YAML like format (extentsion EXT_QLIKVIEW_VARS)

    Implements:
        on_post_save"""

    def on_post_save(self, view):
        fn = view.file_name()
        if (fn.endswith(EXT_QLIKVIEW_VARS)):
            regenerate_expression_tab_file(view.file_name())
