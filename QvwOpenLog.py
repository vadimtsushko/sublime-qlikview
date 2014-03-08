# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import re
class QlikviewOpenLogCommand(sublime_plugin.WindowCommand):
  def run(self, commandVariant=None):
    view = self.window.active_view()
    firstLine = view.substr(view.line(0))
    fileName = view.file_name()
    baseName, ext = os.path.splitext(os.path.basename(fileName))
    logFile = ''
    testFile = ''
    if re.match(r'\/\/\#\!', firstLine):
      shebang = re.sub(r'\/\/\#\!','',firstLine)
      if shebang.endswith('.qvw'):
        testFile = shebang
        if os.path.exists(shebang):
          logFile = shebang
      else: 
        testFile = os.path.abspath(os.path.join(os.path.dirname(fileName),shebang,baseName + '.qvw.log'))
        if os.path.exists(testFile):
          logFile = testFile
    else:
      testFile = os.path.join(os.path.dirname(fileName),baseName +'.qvw.log') 
      if os.path.exists(testFile):
        logFile = testFile
    if logFile == '':
      sublime.error_message('Log file not found: %s' % testFile)
    else:
      self.window.open_file(logFile)
