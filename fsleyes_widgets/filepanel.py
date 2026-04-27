#!/usr/bin/env python
#
# filepanel.py - the FilePanel class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`FilePanel` class."""

import            os
import os.path as op

import wx
import wx.lib.newevent as wxevent


class FilePanel(wx.Control):
    """The ``FilePanel`` is a ``wx.Control`` which contains a text label and a
    button.  The text label displays a file path, and the button opens a
    dialog allowing the user to select a new file.
    """

    def __init__(self,
                 parent,
                 filePath='',
                 wildcard='*',
                 buttonText='Load',
                 message='Select file'):
        """Create a new ``FilePanel``.

        :arg parent:     Parent ``wx`` object.
        :arg filePath:   Initial file path to display.
        :arg wildcard:   File path wildcard to use to restrict
                         what is displayed in the file dialog.
        :arg buttonText: Text to display on file dialog button
        :arg message:    Message to display in file dialog.
        """

        super().__init__(parent)

        self.__wildcard   = wildcard
        self.__message    = message
        self.__sizer      = wx.BoxSizer(wx.HORIZONTAL)
        self.__loadButton = wx.Button(self, label=buttonText)
        self.__filePath   = wx.StaticText(self,
                                          label=filePath,
                                          style=(wx.ALIGN_LEFT |
                                                 wx.ST_ELLIPSIZE_START))

        self.SetSizer(self.__sizer)

        self.__sizer.Add(self.__filePath,   flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__loadButton, flag=wx.EXPAND)

        self.__loadButton.Bind(wx.EVT_BUTTON, self.__onLoad)


    @property
    def loadButton(self):
        """Return a reference to the load button (for testing). """
        return self.__loadButton


    def GetFilePath(self):
        """Return the current file path. """
        return self.__filePath.GetLabel()


    def SetFilePath(self, path):
        """Programmatically update the current file path. """
        if path is None:
            path = ''
        self.__filePath.SetLabel(path)


    def __onLoad(self, ev):
        """Called when the user pushes the "load" button. Opens a file dialog
        allowing the user to select a new file. Emits a :attr:`FilePanelEvent`.
        """

        path = self.GetFilePath()

        if path is not None and op.exists(path):
            startdir = op.dirname(path)
        else:
            startdir = os.getcwd()

        path = None
        dlg  = wx.FileDialog(self.GetTopLevelParent(),
                             message=self.__message,
                             defaultDir=startdir,
                             wildcard=self.__wildcard,
                             style=wx.FD_OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()

        dlg.Close()
        dlg.Destroy()

        if path is not None:
            self.SetFilePath(path)
            wx.PostEvent(self, FilePanelEvent(filePath=path))


_FilePanelEvent, _EVT_FILE_PANEL_EVENT = wxevent.NewEvent()


EVT_FILE_PANEL_EVENT = _EVT_FILE_PANEL_EVENT
"""Identifier for the :data:`FilePanelEvent`. """


FilePanelEvent = _FilePanelEvent
"""Event emitted by a :class:`FilePanel` when the user selects a new file.
"""
