import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as etree
import StringIO

EXT_QLIKVIEW_EXPRESSION  = ".qlikview-expression"
EXT_QLIKVIEW_EXPRESSION_TABLE = ".qlikview-expression-table"

line_template = re.compile(r'^(?P<key>.*?):\s*(?P<val>.*)$')
param_template = re.compile(r'^\s*\-\s*(?P<val>.*)$')

linenum = 0


def parse_expression_file(path, name, text, sio):
    global linenum
    expression = {}
    linenum = 0
    def process_expression(exp):
        if exp == {}:
            return {}
        if exp.get('name') == None:
            raise SyntaxError('Parsing error: `name` property is absent')    
        sio.write(exp['name'])
        sio.write('\t')
        sio.write(exp.get('def'))
        sio.write('\t')
        sio.write(exp.get('label'))
        sio.write('\t')
        sio.write(exp.get('title'))
        sio.write('\n')
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
                continue
            if current_field is not None:
               expression[current_field] += line
               continue 
        m = match.groupdict()
        m['key'] = m['key'].strip()
        m['val'] = m['val'].strip()
        current_field = m['key']
        if m['key'] == 'name':
            expression = process_expression(expression)
        if m['key'] in ('name','label','def', 'title', 'macro'):
            expression[m['key']] = m['val']
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
    # header = '// Content generated from file %s \n\n' % path
    # header = header.encode('utf-8') 
    # sio.write(header)
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
            print "SaneSnippet: Unable to read `%s`" % path
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
            print "SaneSnippet: Unable to open `%s`" % path
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
