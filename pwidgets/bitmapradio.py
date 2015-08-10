#!/usr/bin/env python
#
# bitmapradio.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import wx.lib.newevent as wxevent

_BitampRadioEvent, _EVT_BITMAP_RADIO_EVENT = wxevent.NewEvent()


EVT_BITMAP_RADIO_EVENT = _EVT_BITMAP_RADIO_EVENT


BitmapRadioEvent = _BitampRadioEvent


class BitmapRadioBox(wx.PyPanel):

    def __init__(self, parent, style=None):
        """
        :arg style: ``wx.HORIZONTAL`` or ``wx.VERTICAL``.
        """
        wx.PyPanel.__init__(self, parent)

        if style is None:
            style = wx.HORIZONTAL

        if style & wx.VERTICAL: szorient = wx.VERTICAL
        else:                   szorient = wx.HORIZONTAL

        self.__selection  = -1
        self.__buttons    = []
        self.__clientData = []
        self.__sizer      = wx.BoxSizer(szorient)

        self.SetSizer(self.__sizer)


    def AddChoice(self, bitmap, clientData=None):

        # BU_NOTEXT causes a segfault under OSX
        if wx.Platform == '__WXMAC__':
            style = wx.BU_EXACTFIT | wx.ALIGN_CENTRE
            
        else:
            style = wx.BU_EXACTFIT | wx.ALIGN_CENTRE | wx.BU_NOTEXT
        
        button = wx.ToggleButton(self, style=style)
        button.SetBitmap(bitmap)

        self.__buttons   .append(button)
        self.__clientData.append(clientData)

        self.__sizer.Add(button)
        self.Layout()

        button.Bind(wx.EVT_TOGGLEBUTTON, self.__onButton)

        
    def Clear(self):

        self.__sizer.Clear(True)
        self.__selection  = -1
        self.__buttons    = []
        self.__clientData = []

        
    def Set(self, bitmaps, clientData=None):

        if clientData is None:
            clientData = [None] * len(bitmaps)

        self.Clear()
        map(self.AddChoice, bitmaps, clientData)


    def GetSelection(self):
        return self.__selection

    
    def SetSelection(self, index):

        if index < 0 or index >= len(self.__buttons):
            raise ValueError('Invalid index {}'.format(index))

        self.__selection = index
        
        for i, button in enumerate(self.__buttons):

            if i == index: button.SetValue(True)
            else:          button.SetValue(False)


    def __onButton(self, ev):

        idx  = self.__buttons.index(ev.GetEventObject())
        data = self.__clientData[idx]

        self.SetSelection(idx)
        
        wx.PostEvent(self, BitmapRadioEvent(index=idx, clientData=data))
