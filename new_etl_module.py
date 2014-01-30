# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import re
import os
class NewEtlModuleCommand(sublime_plugin.WindowCommand):
  fileName = ''
  qvwTemplate = ''
  shebang = ''
  def run(self, commandVariant=None):
    view = self.window.active_view()
    qv_executable = view.settings().get("qv_executable","c:\\Program Files\\QlikView\\qv.exe")
    firstLine = view.substr(view.line(0))
    self.fileName = view.file_name()
    baseName, ext = os.path.splitext(os.path.basename(self.fileName))
    if ext != '.qvs':
      sublime.error_message('New ETL module command shoud be invoked from within QlikView script')
      return
    qvwFile = ''
    testFile = ''
    print (firstLine)
    if re.match(r'\/\/\#\!', firstLine):
      self.shebang = re.sub(r'\/\/\#\!','',firstLine)
      testFile = os.path.abspath(os.path.join(os.path.dirname(self.fileName),self.shebang,'_NewFileTemplate.qvw'))
      if os.path.exists(testFile):
        self.qvwTemplate = testFile
    if self.qvwTemplate == '':
      sublime.error_message('File not found: %s' % self.qvwTemplate)
      return
    self.window.show_input_panel('Enter name for new module:','NewModule',self.createModule,None,None)
  def createModule(self,moduleName):
    targetQvwFile = os.path.abspath(os.path.join(os.path.dirname(self.fileName),self.shebang,moduleName + '.qvw'))
    if os.path.exists(targetQvwFile):
      sublime.error_message('File %s already exists' % targetQvwFile)
      return
    self.window.run_command("exec", { "cmd": ["cmd","/C","copy",self.qvwTemplate,targetQvwFile]})
    targetQvsFile = os.path.join(os.path.dirname(self.fileName),moduleName+'.qvs')
    self.window.run_command("exec", { "cmd": ["cmd","/C","copy",self.fileName,targetQvsFile]})
    self.window.open_file(targetQvsFile)
