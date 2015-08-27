#!/usr/bin/env python
#
# colourbutton.py - A button which allows the user to select a colour.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`ColourButton` class, a button which
allows the user to select a RGBA colour.
"""


import wx
import wx.lib.newevent as wxevent


class ColourButton(wx.Button):
    """A :class:`wx.Button` which allows the user to select a colour.

    The currently selected colour is displayed as a bitmap on the button.
    When the user presses the button, a :class:`wx.ColourDialog` is displayed,
    allowing the user to change the colour. When the user does so, a
    :data:`EVT_COLOUR_BUTTON_EVENT` is generated.

    This class provides an alternative to the :class:`wx.ColourPickerCtrl`,
    which is a bit inflexible w.r.t. sizing/automatic resizing.
    """

    def __init__(self, parent, size=None, colour=None):
        """Create a ``ColourButton``.

        :arg parent: A :mod:`wx` parent window.

        :arg size:   A tuple containing the ``(width, height)`` of the
                     colour bitmap in pixels. Defaults to ``(32, 32)``.
        
        :arg colour: Initial colour. Defaults to black.
        """

        if size   is None: size   = (32, 32)
        if colour is None: colour = (0, 0, 0)

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
        """Return the current colour, as a tuple of ``(r, g, b)`` values, each
        in the range ``[0 - 255]``.
        """
        return self.__colour

    
    def SetValue(self, colour):
        """Sets the current colour to the specified ``colour``."""
        
        if len(colour) != 3 or \
           any([v < 0 or v > 255 for v in colour]):
            raise ValueError('Invalid RGB colour: {}'.format(colour))

        self.__updateBitmap(colour)
        self.__colour = colour


    def __updateBitmap(self, colour):
        """Called when the colour is changed. Updates the bitmap shown
        on the button.
        """

        import numpy as np
        
        w, h = self.__size
        data = np.zeros((w, h, 3), dtype=np.uint8)

        data[:, :] = colour

        img = wx.ImageFromData(w, h, data.tostring())

        self.__bmp = wx.BitmapFromImage(img)

        self.SetBitmap(self.__bmp)


    def __onClick(self, ev):
        """Called when this ``ColourButton`` is pressed.

        Displays a :class:`wx.ColourDialog` allowing the user to select a new
        colour.
        """

        colourData = wx.ColourData()
        colourData.SetColour(self.__colour)

        dlg = wx.ColourDialog(self.GetTopLevelParent(), colourData)

        if dlg.ShowModal() != wx.ID_OK:
            return

        newColour = dlg.GetColourData().GetColour()

        self.SetValue(newColour)
        
        wx.PostEvent(self, ColourButtonEvent(colour=newColour))


_ColourButtonEvent, _EVT_COLOUR_BUTTON_EVENT = wxevent.NewEvent()


EVT_COLOUR_BUTTON_EVENT = _EVT_COLOUR_BUTTON_EVENT
"""Identifier for the :data:`ColourButtonEvent`. """


ColourButtonEvent = _ColourButtonEvent
"""Event emitted by a ``ColourButton`` when the user changes the selected
colour.
"""
