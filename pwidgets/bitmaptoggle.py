#!/usr/bin/env python
#
# bitmaptoggle.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import wx
import wx.lib.newevent as wxevent


_BitmapToggleEvent, _EVT_BITMAP_TOGGLE_EVENT = wxevent.NewEvent()


EVT_BITMAP_TOGGLE_EVENT = _EVT_BITMAP_TOGGLE_EVENT


BitmapToggleEvent = _BitmapToggleEvent


class BitmapToggleButton(wx.Button):

    def __init__(self, parent, trueBitmap, falseBitmap):

        # BU_NOTEXT causes crash under OSX
        if wx.Platform == '__WXMAC__': style = wx.BU_EXACTFIT
        else:                          style = wx.BU_EXACTFIT | wx.BU_NOTEXT

        wx.Button.__init__(self, parent, style=style)

        self.__trueBmp  = trueBitmap
        self.__falseBmp = falseBitmap
        self.__state    = False

        self.Bind(wx.EVT_BUTTON, self.__onClick)
        
        self.__toggle()


    def GetValue(self):
        return self.__state

    
    def SetValue(self, state):
        if state != self.__state:
            self.__toggle()


    def __toggle(self):
        
        self.__state = not self.__state
        
        if self.__state: self.SetBitmap(self.__trueBmp)
        else:            self.SetBitmap(self.__falseBmp)


    def __onClick(self, ev):
        self.__toggle()
        wx.PostEvent(self, BitmapToggleEvent(value=self.__state))
