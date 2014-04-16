# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import re
class QlikviewReloadCommand(sublime_plugin.WindowCommand):
  def run(self, commandVariant=None):
    view = self.window.active_view()
    qv_executable = view.settings().get("qv_executable","c:\\Program Files\\QlikView\\qv.exe")
    firstLine = view.substr(view.line(0))
    fileName = view.file_name()
    baseName, ext = os.path.splitext(os.path.basename(fileName))
    qvwFile = ''
    testFile = ''
    print (firstLine)
    if re.match(r'\/\/\#\!', firstLine):
      shebang = re.sub(r'\/\/\#\!','',firstLine)
      if shebang.endswith('.qvw'):
        testFile = shebang
        if os.path.exists(shebang):
          qvwFile = shebang
      else: 
        testFile = os.path.abspath(os.path.join(os.path.dirname(fileName),shebang,baseName + '.qvw'))
        if os.path.exists(testFile):
          qvwFile = testFile
    else:
      testFile = os.path.join(os.path.dirname(fileName),baseName +'.qvw') 
      if os.path.exists(testFile):
        qvwFile = testFile
    if qvwFile == '':
      sublime.error_message('File not found: %s' % testFile)
    else:
      sublime.status_message('Reloading file %s' % qvwFile)
      print("commandVariant", commandVariant)
      if commandVariant is None:
        self.window.run_command("exec", { "cmd": [qv_executable,"/R","/nodata","/Nosecurity",qvwFile]})
      else:
        self.window.run_command("exec", { "cmd": ["cmd","/C",qv_executable,qvwFile]})

