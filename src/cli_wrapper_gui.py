
import ctypes
import os
import subprocess
import sys
from enum import Enum
from sys import flags

import wx


class FileDropToObject(wx.FileDropTarget):
    def __init__(self, target):
        wx.FileDropTarget.__init__(self)
        self.target = target

    def OnDropFiles(self, x, y, filenames):
        for file in filenames:
            self.target.SetValue(file)
        return True


class RadioType(Enum):
    A = 'Aaa'
    B = 'Python'
    C = 'Folder'


class ActionPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, wx.ID_ANY)
        path_field_label = wx.StaticText(self, id=wx.ID_ANY, label='Terget File: ')
        self.path_field = wx.TextCtrl(self, id=wx.ID_ANY, size=(400, -1))
        self.path_field.SetDropTarget(FileDropToObject(self.path_field))
        self.path_field.Bind(wx.EVT_TEXT, self.onChangePathField)
        self.filePicker = wx.FilePickerCtrl(self, id=wx.ID_ANY, style=wx.FLP_OPEN)
        self.filePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFileSelected)
        text_layout = wx.BoxSizer(wx.HORIZONTAL)
        text_layout.Add(path_field_label, proportion=0, flag=wx.GROW | wx.ALL, border=5)
        text_layout.Add(self.path_field, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        text_layout.Add(self.filePicker, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(text_layout, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        self.action_radiobox = wx.RadioBox(self, wx.ID_ANY, label='RadioType', choices=[e.value for e in RadioType], style=wx.RA_HORIZONTAL)

        layout.Add(self.action_radiobox, flag=wx.LEFT | wx.RIGHT, border=10)

        start_btn = wx.Button(self, wx.ID_ANY, label='Start')
        self.Bind(wx.EVT_BUTTON, self.onStartButtonClick, start_btn)
        button_layout = wx.BoxSizer(wx.HORIZONTAL)
        button_layout.Add(start_btn, proportion=0, flag=wx.LEFT | wx.RIGHT, border=5)

        layout.Add(button_layout, proportion=0, flag=wx.ALL | wx.ALIGN_RIGHT, border=5)

        self.SetSizer(layout)

    def onFileSelected(self, event):
        self.path_field.SetValue(self.filePicker.GetPath())

    def onChangePathField(self, event):
        path = self.path_field.GetValue()
        self.filePicker.SetPath(path)
        if os.path.isdir(path):
            self.action_radiobox.SetStringSelection(RadioType.C.value)
        elif os.path.isfile(path):
            _, ext = os.path.splitext(path)
            if ext == '.py':
                self.action_radiobox.SetStringSelection(RadioType.B.value)

    def onStartButtonClick(self, event):
        print('Start')
        selected = self.action_radiobox.GetStringSelection()
        command = None
        if selected == RadioType.A.value:
            print('**Aaa')
            command = ['bin/CLI-Mock.exe', '-f', 'Ccc - ' + self.path_field.GetValue()]
        elif selected == RadioType.B.value:
            print('** Bbb')
            command = ['bin/CLI-Mock.exe', '-f', 'Bbb - ' + self.path_field.GetValue()]
        elif selected == RadioType.C.value:
            print('** Ccc')
            command = ['bin/CLI-Mock.exe', '-b', '-f', 'Ccc - ' + self.path_field.GetValue()]

        if command and self.path_field.GetValue():
            for line in self.exec_command(command):
                sys.stdout.write(line)

    def exec_command(self, command):
        print(command)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline()
            wx.Yield()
            if line:
                yield line
            elif not line and proc.poll() is not None:
                break


class StdoutPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, wx.ID_ANY)
        std_field_label = wx.StaticText(self, id=wx.ID_ANY, label='Console output')
        self.std_field = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        sys.stdout = self
        layout = wx.BoxSizer(wx.VERTICAL)
        # layout.Add(wx.StaticLine(self), flag=wx.ALL | wx.EXPAND, border=15)
        layout.Add(std_field_label, proportion=0, flag=wx.LEFT | wx.RIGHT, border=10)
        layout.Add(self.std_field, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(layout)


    def write(self, msg):
        self.std_field.AppendText(msg)

    def flush(self):
        pass


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="ApplicationTitle", size=(600, 300))
        self.__set_layout()

    def __set_layout(self):
        action_panel = ActionPanel(self)
        stdout_panel = StdoutPanel(self)
        root_layout = wx.BoxSizer(wx.VERTICAL)
        root_layout.Add(action_panel, proportion=0, flag=wx.ALL | wx.EXPAND)
        root_layout.Add(stdout_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(root_layout)


class Application(wx.App):
    def OnInit(self):
        frame = MainFrame()
        
        frame.SetBackgroundColour(wx.NullColour)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


if __name__ == '__main__':
    print('Main')
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass
    app = Application()
    app.MainLoop()
