# -*- encoding: UTF-8 -*-
import sublime
import sublime_plugin
import os
import collections
from xml.dom import minidom
import sys

class QvdField:
    fieldName = ''
    uniqValues = 0
    memoryUsage = 0
class QvdTable:
    noOfRecords = 0
    tableName = ''
    creatorDoc = ''
    createdTime = ''
    fields = []

class QlikviewQvdFileListener(sublime_plugin.EventListener):

    EXT_QLIKVIEW_QVD  = ".QVD"
    def on_activated(self,view):
        if not self.is_ST3():
            return
        fn = view.file_name()
        if (fn is None):
            return
        if (fn.upper().endswith(self.EXT_QLIKVIEW_QVD)):
            view.run_command('qvd_viewer',{'cmd':''})
    def is_ST3(self):
        ''' check if ST3 based on python version '''
        version = sys.version_info
        if isinstance(version, tuple):
            version = version[0]
        elif getattr(version, 'major', None):
            version = version.major
        return (version >= 3)

class QvdViewerCommand(sublime_plugin.TextCommand):
    moduleSettings = None
    edit = None
    path = ''
    def run(self, edit, cmd=''):
            self.edit = edit
            self.path = self.view.file_name()
            sublime.active_window().run_command('close')
            # view.run_command('close')
            self.view = sublime.active_window().new_file()
            view = self.view
            view.set_scratch(True)
            token = collections.deque()
            tokenMarker = collections.deque([b'<',b'/',b'Q',b'v',b'd',b'T',b'a',b'b',b'l',b'e',b'H',b'e',b'a',b'd',b'e',b'r',b'>'])
            token = collections.deque(tokenMarker)
            tokenStr = collections.deque()
            buff = collections.deque()
            n = 0
            headerFound = False
            with open(self.path, 'rb') as f:
                while True:
                    char = f.read(1)
                    n = n + 1
                    if n > 100000:
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
            buffString = b''.join(buff)
            xml = minidom.parseString(buffString)
            self.parseHeader(xml)
    def parseHeader(self, xml):
        table = QvdTable()
        table.fields = []
        table.tableName = self.getValue(xml,"TableName")
        table.noOfRecords = self.getValue(xml,"NoOfRecords")
        table.createdTime = self.getValue(xml,"CreateUtcTime")
        for fieldXml in xml.getElementsByTagName("QvdFieldHeader"):
            field = QvdField()
            field.fieldName = self.getValue(fieldXml,"FieldName")
            field.uniqValues =  self.getValue(fieldXml,"NoOfSymbols")
            field.memoryUsage = self.getValue(fieldXml,"Length")
            field.fieldType = 'Number'
            if self.getValue(fieldXml,"NumberFormat/Type") == "UNKNOWN":
                field.fieldType = "String"
            table.fields.append(field)
        viewHeader =  table.tableName + '.MD'
        self.addLine(viewHeader)
        self.addLine('---')
        self.addLine('')
        line = '%s records. QVD created at %s' % (table.noOfRecords,table.createdTime)
        self.addLine(line)
        self.addLine('')
        self.addLine('###Fields:')
        self.addLine('')
        for field in table.fields:
            line = "- **%s**. Unique values: %s, Memory usage: %s" % (field.fieldName, field.uniqValues, field.memoryUsage)
            self.addLine(line)
        self.addLine('')
        self.addLine('####Sample load statement:')
        self.addLine('')
        self.addLine('```QlikView')
        self.addLine('')
        self.addLine('LOAD')
        comma = ','
        for field in table.fields:
            if field.fieldName == table.fields[-1].fieldName:
                comma = ''
            self.addLine('  ' + field.fieldName + comma)
        self.addLine('    FROM [' + self.path+'] (QVD);')
        self.addLine('')
        self.addLine('```')
        self.closeOthers(viewHeader)
    def addLine(self,line):
        self.view.insert(self.edit, self.view.size(), line + '\n')
    def getValue(self,xml,tagName):
        nodeList = xml.getElementsByTagName(tagName)
        if len(nodeList) == 0:
            return ''
        tag = nodeList[0].toxml()
        xmlData=tag.replace('<'+tagName+'>','').replace('</'+tagName+'>','')
        return xmlData
    def closeOthers(self,viewHeader):
        window = self.view.window()
        myId = self.view.id()
        for v in window.views():
            if v.id() == myId:
                continue
            l = v.line(sublime.Region(0,0))
            line = v.substr(l)
            if (line == viewHeader):
                window.focus_view(v)
                window.run_command('close')
                window.focus_view(self.view)
