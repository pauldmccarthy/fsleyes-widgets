#!/usr/bin/env python
#
# bitmaptoggle.py - A button which toggles between two bitmaps.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`BitmapToggleButton` class, a button
which toggles between two bitmaps.
"""


import wx
import wx.lib.newevent as wxevent


class BitmapToggleButton(wx.Button):
    """A :class:`wx.Button` which stores a boolean state (``True``/``False``),
    and displays one of two bitmaps depending on the state.

    When the user presses the button, the boolean state and the displayed
    bitmap changes accordingly. A :data:`EVT_BITMAP_TOGGLE_EVENT` is generated
    on button presses.
    """

    def __init__(self, parent, trueBitmap, falseBitmap):
        """Create a ``BitmapToggleButton``.

        :arg parent:      The :mod:`wx` parent window.

        :arg trueBitmap:  :class:`wx.Bitmap` to display when the button state
                          is ``True``. 

        :arg falseBitmap: :class:`wx.Bitmap` to display when the button state
                          is ``False``.
        """

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
        """Returns the current boolean state of this ``BitmapToggleButton``."""
        return self.__state

    
    def SetValue(self, state):
        """Sets the current boolean state of this ``BitmapToggleButton``."""
        if state != self.__state:
            self.__toggle()


    def __toggle(self):
        """Toggles the state of this ``BitmapToggleButton``."""
        
        self.__state = not self.__state
        
        if self.__state: self.SetBitmap(self.__trueBmp)
        else:            self.SetBitmap(self.__falseBmp)


    def __onClick(self, ev):
        """Called when this button is pressed.

        Flips the button state, and emits a :data:`BitmapToggleEvent`.
        """
        self.__toggle()
        wx.PostEvent(self, BitmapToggleEvent(value=self.__state))


_BitmapToggleEvent, _EVT_BITMAP_TOGGLE_EVENT = wxevent.NewEvent()


EVT_BITMAP_TOGGLE_EVENT = _EVT_BITMAP_TOGGLE_EVENT
"""Identifier for the :data:`BitmapToggleEvent` event."""


BitmapToggleEvent = _BitmapToggleEvent
"""Event emitted when a :class:`BitmapToggleButton` is pushed.

Contains one attribute, ``value``, which contains the current button state
(``True`` or ``False``).
"""
