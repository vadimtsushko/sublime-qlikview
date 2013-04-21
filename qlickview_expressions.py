import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as etree
import StringIO

EXT_QLIKVIEW_EXPRESSION  = ".qlikview-expression"
EXT_QLIKVIEW_EXPRESSION_TABLE = ".qlikview-expression-table"

line_template = re.compile(r'^\s*(?P<key>\w*?):\s*(?P<val>.*)$')
param_template = re.compile(r'^\s*\-\s*(?P<val>.*)$')

linenum = 0
defs = {}
macro = []

def parse_expression_file(path, name, text, sio):
    global linenum
    global defs
    global macro
    expression = {}
    defs = {}
    linenum = 0
    macro = []
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
    def process_expression(exp):
        global macro
        global defs
        if exp == {}:
            return {}
        if exp.get('name') is None:
            raise SyntaxError('Parsing error: `name` property is absent')
        if exp['name'] in defs:
            raise SyntaxError('Parsing error: duplicate expression with name `%s`' % unicode(exp['name']))
        if exp.get('def') is not None and exp.get('macro') is not None:
           raise SyntaxError('Parsing error: Expression have defined both `def` and `macro` property. Something one must be defined')
        if exp.get('def') is None:
            if  exp.get('macro') is None:
                raise SyntaxError('Parsing error: Expression `%s` have not defined `def` or `macro` property' % unicode(exp['name']))
            exp['def'] = expand_macro()
        defs[exp['name']] = exp['def']
        label = exp.get('label')
        if label is None or label.strip() == '':
            label = exp['name']
        title = exp.get('title')
        if title is None or title.strip() == '':
            title = exp['name']    
        sio.write(exp['name'])
        sio.write('\t')
        sio.write(exp['def'])
        sio.write('\t')
        sio.write(label)
        sio.write('\t')
        sio.write(title)
        sio.write('\n')
        init_expression()
        return {}
    def parse_val(text):
        return text.strip()
    current_field = None
    for line in text.splitlines():
        linenum = linenum + 1
        match = line_template.match(line)
        if match is None:
            line = line.strip()
            if line == '---':
                expression = process_expression(expression)
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
                    expression[current_field] += line
                    continue        
        m = match.groupdict()
        m['key'] = m['key'].strip()
        m['val'] = m['val'].strip()
        current_field = m['key']
        if m['key'] == 'name':
            expression = process_expression(expression)
        if m['key'] in ('name','label','def', 'title'):
            expression[m['key']] = m['val']
        else:
            if m['key'] == 'macro':
                macro.append(m['val'])
                expression['macro'] = macro
            else:
                raise SyntaxError('Unexpected QlikView expression property: "%s"' % m['key'])
    process_expression(expression)    
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
    sio = StringIO.StringIO()
    try:
        parse_expression_file(path, name, read, sio)
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
    else:
        return sio.getvalue()
    finally: sio.close()

def regenerate_expression_tab_file(path, onload=False, force=False):

    (sane_path, path) = (path, swap_extension(path))
    # Generate XML
    generated = regenerate_tab_file_content(sane_path, onload=onload)
 
    if generated is None:
        return  # errors already printed
    # Check if snippet should be written
 
    write = False
    if force or not os.path.exists(path):
        write = True
    else:
        try:
            f = open(path, 'r')
        except:
            print "QlikView expression: Unable to read `%s`" % path
            return
        else:
            read = f.read()
            f.close()
        if read != generated:
            write = True
    # Write the file
    if write:
        try:
            f = open(path, 'w')
        except:
            print "QlikView expression: Unable to open `%s`" % path
        else:
            read = f.write(generated)
            f.close()


def swap_extension(path):
    "Swaps `path`'s extension between `EXT_QLIKVIEW_EXPRESSION` and `EXT_QLIKVIEW_EXPRESSION_TABLE`"

    if path.endswith(EXT_QLIKVIEW_EXPRESSION):
        return path.replace(EXT_QLIKVIEW_EXPRESSION, EXT_QLIKVIEW_EXPRESSION_TABLE)
    else:
        return path.replace(EXT_QLIKVIEW_EXPRESSION_TABLE, EXT_QLIKVIEW_EXPRESSION)


class QlikViewExpression(sublime_plugin.EventListener):
    """Save expressions in tabular format with extension EXT_QLIKVIEW_EXPRESSION_TABLE 
    along with current expression file in YAML like format (extentsion EXT_QLIKVIEW_EXPRESSION)

    Implements:
        on_post_save"""

    def on_post_save(self, view):
        fn = view.file_name()
        if (fn.endswith(EXT_QLIKVIEW_EXPRESSION)):
            regenerate_expression_tab_file(view.file_name())
