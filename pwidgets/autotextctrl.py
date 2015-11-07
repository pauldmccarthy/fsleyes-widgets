#!/usr/bin/env python
#
# autotextctrl.py - The AutoTextCtrl class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import wx.lib.newevent as wxevent


class AutoTextCtrl(wx.Panel):

    def __init__(self, parent, style=0):

        wx.Panel.__init__(self, parent)

        self.__textCtrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.__sizer    = wx.BoxSizer(wx.HORIZONTAL)
        
        self.__sizer.Add(self.__textCtrl, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)
        
        self.__options = []

        self.__textCtrl.Bind(wx.EVT_TEXT,       self.__onText)
        self.__textCtrl.Bind(wx.EVT_TEXT_ENTER, self.__onEnter)

        
    def AutoComplete(self, options):
        self.__options = list(options)


    def GetValue(self):
        return self.__textCtrl.GetValue()

        
    def SetValue(self, value):
        self.__textCtrl.SetValue(value)

        
    def ChangeValue(self, value):
        self.__textCtrl.ChangeValue(value) 


    def __onText(self, ev):

        text = self.__textCtrl.GetValue()
        self.__showPopup(text)


    def __onEnter(self, ev):
        value = self.__textCtrl.GetValue()
        ev = AutoTextCtrlEnterEvent(text=value)
        wx.PostEvent(self, ev)


    def __showPopup(self, text):

        text = text.strip()

        if text != '':
            options = [o for o in self.__options if o.startswith(text)]
        else:
            options = []

        if len(options) == 0:
            return

        width, height = self.__textCtrl.GetSize().Get()
        posx, posy    = self.__textCtrl.GetScreenPosition().Get()

        popup  = AutoCompletePopup(
            self,
            self,
            text,
            self.__options)

        def refocus(ev):
            self.GetTopLevelParent().Raise()
            self.__textCtrl.SetFocus()
            self.__textCtrl.SetInsertionPointEnd()

        popup.Bind(wx.EVT_WINDOW_DESTROY, refocus)

        popup.SetSize((width, -1))
        popup.SetPosition((posx,  posy))
        popup.Show()

        
_AutoTextCtrlEnterEvent, _EVT_ATC_TEXT_ENTER = wxevent.NewEvent()


AutoTextCtrlEnterEvent = _AutoTextCtrlEnterEvent


EVT_ATC_TEXT_ENTER = _EVT_ATC_TEXT_ENTER





class AutoCompletePopup(wx.PopupWindow): 

    def __init__(self, parent, atc, text, options):
        """
        """

        wx.PopupWindow.__init__(self, parent)

        self.__atc      = atc
        self.__options  = options
        self.__textCtrl = wx.TextCtrl(self, style=(wx.TE_PROCESS_ENTER |
                                                   wx.WANTS_CHARS))
        self.__listBox  = wx.ListBox(self,  style=(wx.LB_SINGLE        |
                                                   wx.WANTS_CHARS))
        self.__textCtrl.SetValue(text)
        self.__textCtrl.SetInsertionPointEnd()
        self.__configList(text)

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self.__textCtrl, flag=wx.EXPAND)
        self.__sizer.Add(self.__listBox,  flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)

        self.Layout()
        self.Fit()

        self.__textCtrl.Bind(wx.EVT_TEXT,           self.__onText)
        self.__textCtrl.Bind(wx.EVT_TEXT_ENTER,     self.__onEnter)
        self.__textCtrl.Bind(wx.EVT_CHAR_HOOK,      self.__onChar)
        self.__listBox .Bind(wx.EVT_CHAR_HOOK,      self.__onListChar)
        self.__listBox .Bind(wx.EVT_LISTBOX_DCLICK, self.__onListMouseDblClick)

        
    def __destroy(self):
        """Called by various event handlers. Copies the current value in
        this ``AutoCompletePopup`` to the owning :class:`AutoTextCtrl`,
        and then (asynchronously) destroys this ``AutoCompletePopup``.
        """
        value = self.__textCtrl.GetValue()
        atc   = self.__atc
        atc.ChangeValue(value)
        
        def destroy():
            try:
                self.Close()
                self.Destroy()
                
            except wx.PyDeadObjectError:
                pass

        wx.CallAfter(destroy)


    def __configList(self, prefix):
        
        prefix  = prefix.strip()
        options = [o for o in self.__options if o.startswith(prefix)]

        self.__listBox.Set(options)

        if len(prefix) == 0 or len(options) == 0 or options[0] == prefix:
            return []

        return options


    def __onChar(self, ev):
        """Called on an ``EVT_CHAR_HOOK`` event from the text control. """
        
        down  = wx.WXK_DOWN
        esc   = wx.WXK_ESCAPE
        enter = wx.WXK_RETURN
        key   = ev.GetKeyCode()

        if key not in (down, enter, esc):
            ev.Skip()
            return

        # The user hitting enter/escape will result
        # in this popup being destroyed
        if key in (esc, enter):
            self.__destroy()
            return

        # If the user hits the down 
        # arrow, focus the listbox
        self.__listBox.SetFocus()
        self.__listBox.SetSelection(0)
                

    def __onText(self, ev):
        """Called on an ``EVT_TEXT`` event from the text control."""
        
        text = self.__textCtrl.GetValue()
        
        if len(self.__configList(text)) == 0:
            self.__destroy()


    def __onEnter(self, ev):
        """Called on an ``EVT_TEXT_ENTER`` event from the text control."""
        self.__destroy()


    def __onListChar(self, ev):
        """Called on an ``EVT_CHAR_HOOK`` event from the list box.
        """
        key   = ev.GetKeyCode()
        enter = wx.WXK_RETURN
        esc   = wx.WXK_ESCAPE
        up    = wx.WXK_UP

        if key not in (enter, esc, up):
            ev.Skip()
            return

        sel = self.__listBox.GetSelection()
        val = self.__listBox.GetString(sel)

        # If the user pushed the up arrow,
        # and we're at the top of the list,
        # give the focus to the text control
        if key == up:
            if sel == 0:
                self.__textCtrl.SetFocus()
            else:
                ev.Skip()
            return

        # If the user pushed enter, copy
        # the current list selection to
        # the text control.
        if key == enter:
            self.__textCtrl.SetValue(val)

        # The user hitting enter or escape
        # will result in this popup being
        # destroyed
        self.__destroy()


    def __onListMouseDblClick(self, ev):
        """Called when the user double clicks an item in the list box.
        """
        ev.Skip()
        
        sel = self.__listBox.GetSelection()
        val = self.__listBox.GetString(sel)

        self.__textCtrl.SetValue(val)
        self.__destroy()
