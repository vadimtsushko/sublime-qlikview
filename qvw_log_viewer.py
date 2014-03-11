# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import collections
import sys
import re
class QlikviewTransformLogCommand(sublime_plugin.TextCommand):
    moduleSettings = None
    edit = None
    path = ''
    timer = None
    def run(self, edit):
        self.edit = edit
        self.path = self.view.file_name()
        self.transform()

    def transform(self):
        view = self.view
        edit = self.edit
        view.set_read_only(False)
        view.set_scratch(True)
        txt = view.substr(sublime.Region(0,view.size()))
        view.erase(edit,sublime.Region(0,view.size()))
        trace_mode = False
        for line in txt.splitlines():
            if trace_mode:
               line = re.sub(r'^(\s*\d+\/\d+\/\d{4} \d+:\d+:\d+ (A|P)M: .{4})',r'//-->> \1',line) 
               trace_mode = False
            else: 
                line = re.sub(r'^\s*\d+\/\d+\/\d{4} \d+:\d+:\d+ (A|P)M:\s+\d{4}','',line)
                if re.match(r'^\s*TRACE',line,flags=re.IGNORECASE):
                    trace_mode = True
                    print(line)
                line = re.sub(r'^(\s*\d+\/\d+\/\d{4} \d+:\d+:\d+ (A|P)M:  {4})',r'//>> \1',line)
            self.addLine(line)

    def addLine(self,line):
        self.view.insert(self.edit, self.view.size(), line+'\n')
    def is_enabled(self):
        return sublime.active_window().active_view().file_name().upper().endswith('.QVW.LOG')        