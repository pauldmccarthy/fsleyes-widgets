#!/usr/bin/env python
#
# colourbutton.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import wx
import wx.lib.newevent as wxevent


_ColourButtonEvent, _EVT_COLOUR_BUTTON_EVENT = wxevent.NewEvent()


EVT_COLOUR_BUTTON_EVENT = _EVT_COLOUR_BUTTON_EVENT


ColourButtonEvent = _ColourButtonEvent


class ColourButton(wx.Button):

    def __init__(self, parent, size, colour=None):

        # BU_NOTEXT causes crash under OSX
        if wx.Platform == '__WXMAC__': style = wx.BU_EXACTFIT
        else:                          style = wx.BU_EXACTFIT | wx.BU_NOTEXT
        
        wx.Button.__init__(self, parent, style=style)

        self.__size = size
        self.__bmp  = None

        if colour is None:
            colour = (0, 0, 0)

        self.Bind(wx.EVT_BUTTON, self.__onClick)

        self.SetValue(colour)


    def GetValue(self):
        return self.__colour

    
    def SetValue(self, colour):
        
        if len(colour) != 3 or \
           any([v < 0 or v > 255 for v in colour]):
            raise ValueError('Invalid RGB colour: {}'.format(colour))

        self.__updateBitmap(colour)
        self.__colour = colour


    def __updateBitmap(self, colour):
        
        w, h = self.__size
        data = np.zeros((w, h, 3), dtype=np.uint8)

        data[:, :] = colour

        img = wx.ImageFromData(w, h, data.tostring())

        self.__bmp = wx.BitmapFromImage(img)

        self.SetBitmap(self.__bmp)


    def __onClick(self, ev):

        colourData = wx.ColourData()
        colourData.SetColour(self.__colour)

        dlg = wx.ColourDialog(self.GetTopLevelParent(), colourData)

        if dlg.ShowModal() != wx.ID_OK:
            return

        newColour = dlg.GetColourData().GetColour()

        self.SetValue(newColour)
        
        wx.PostEvent(self, ColourButtonEvent(colour=newColour))
