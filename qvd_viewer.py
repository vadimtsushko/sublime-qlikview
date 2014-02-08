# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import re
import xml.etree.ElementTree as etree
import csv
import sys
import collections

def is_ST3():
    ''' check if ST3 based on python version '''
    version = sys.version_info
    if isinstance(version, tuple):
        version = version[0]
    elif getattr(version, 'major', None):
        version = version.major
    return (version >= 3)

class QlikviewQvdFileListener(sublime_plugin.EventListener):
    """Save variables in tabular format with extension EXT_QLIKVIEW_VARS_TABLE 
    along with current expression file in YAML like format (extentsion EXT_QLIKVIEW_VARS)

    Implements:
        on_post_save"""

    EXT_QLIKVIEW_QVD  = ".QVD"
    def on_activated(self,view):
        fn = view.file_name()
        if (fn is None):
            return
        if (fn.endswith(self.EXT_QLIKVIEW_QVD)):
            pos = view.find('^\\s+</QvdTableHeader>', 0)
            pos = pos.b
            print(pos)
            view.run_command('qvd_viewer')
class QvdViewerCommand(sublime_plugin.TextCommand):
    moduleSettings = None
    edit = None
    def run(self, edit):
            self.edit = edit
            view = self.view
            # self.moduleSettings = view.settings()
            view.set_scratch(True)
            # view.set_read_only(True)
            all_region = sublime.Region(0,view.size())
            view.erase(edit,all_region)
            path = view.file_name()
            token = collections.deque()
            tokenMarker = collections.deque([b'<',b'/',b'Q',b'v',b'd',b'T',b'a',b'b',b'l',b'e',b'H',b'e',b'a',b'd',b'e',b'r',b'>'])
            token = collections.deque(tokenMarker)
            tokenStr = collections.deque()
            buff = collections.deque()
            n = 0
            headerFound = False
            with open(path, 'rb') as f:
                while True:
                    char = f.read(1)
                    n = n + 1
                    if n > 10000:
                        break
                    if char =='':
                        break
                    buff.append(char)
                    token.append(char)
                    token.popleft()
                    if token == tokenMarker:
                        headerFound = True
                        break
            if not headerFound:
                self.addLine('ERROR: QvdFile header have not been recognized')
                return
            
            # self.view.insert(edit, 0, 'TOKEN: ' + str(token))
            # self.view.insert(edit, view.size(), '\n')
            #self.view.insert(edit, view.size(), str(buff))
            buffString = b''.join(buff)
            from xml.dom import minidom
            xml = minidom.parseString(buffString)
            #print(xmldoc)
            t = self.getValue(xml,"TableName")
            records = self.getValue(xml,"NoOfRecords")
            line = "Table %s. %s records" % (t,records)
            self.view.insert(edit, view.size(), line)

    def addLine(self,line):
        self.view.insert(self.edit, self.view.size(), line)
    def getValue(self,xml,tagName):
        nodeList = xml.getElementsByTagName(tagName)
        if len(nodeList) == 0:
            return ''
        tag = nodeList[0].toxml()
        xmlData=tag.replace('<'+tagName+'>','').replace('</'+tagName+'>','')
        return xmlData
