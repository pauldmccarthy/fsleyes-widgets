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


class BitmapToggleButton(wx.ToggleButton):
    """A :class:`wx.ToggleButton` which stores a boolean state
    (``True``/``False``), and displays one of two bitmaps depending on the
    state.

    When the user presses the button, the boolean state and the displayed
    bitmap changes accordingly. A :data:`EVT_BITMAP_TOGGLE` event is generated
    on button presses.
    """

    def __init__(self, parent, *args, **kwargs):
        """Create a ``BitmapToggleButton``.

        :arg parent:   The :mod:`wx` parent window.

        :arg trueBmp:  Required. A :class:`wx.Bitmap` to display when
                       the button state is ``True``.

        :arg falseBmp: Optional. A :class:`wx.Bitmap` to display when the
                       button state is ``False``.

        All other arguemnts are passed through to the
        ``wx.ToggleButton.__init__`` method.
        """

        trueBmp  = kwargs.pop('trueBmp',  None)
        falseBmp = kwargs.pop('falseBmp', None)
        style    = kwargs.get('style',    0)

        # wx.ToggleButton(style=BU_NOTEXT)
        # causes segfault under mac
        if wx.Platform == '__WXMAC__' and (style | wx.BU_NOTEXT):
            kwargs['style'] = style & ~wx.BU_NOTEXT

        wx.ToggleButton.__init__(self, parent, *args, **kwargs)

        self.__trueBmp  = None
        self.__falseBmp = None

        self.Bind(wx.EVT_TOGGLEBUTTON, self.__onToggle)

        self.SetBitmap(trueBmp, falseBmp)


    def SetBitmap(self, trueBmp, falseBmp=None):
        if falseBmp is None:
            falseBmp = trueBmp

        self.__trueBmp  = trueBmp
        self.__falseBmp = falseBmp

        self.__updateBitmap()


    def SetValue(self, state):
        """Sets the current boolean state of this ``BitmapToggleButton``."""
        wx.ToggleButton.SetValue(self, state)
        self.__updateBitmap()


    def __updateBitmap(self):
        """Toggles the state of this ``BitmapToggleButton``."""

        trueBmp  = self.__trueBmp
        falseBmp = self.__falseBmp

        if trueBmp is None:
            return

        if self.GetValue(): wx.ToggleButton.SetBitmapLabel(self, trueBmp)
        else:               wx.ToggleButton.SetBitmapLabel(self, falseBmp)


    def __onToggle(self, ev):
        """Called when this button is pressed.

        Flips the button state, and emits a :data:`BitmapToggleEvent`.
        """
        self.__updateBitmap()

        ev = BitmapToggleEvent(value=self.GetValue())
        ev.SetEventObject(self)

        wx.PostEvent(self, ev)


_BitmapToggleEvent, _EVT_BITMAP_TOGGLE = wxevent.NewEvent()


EVT_BITMAP_TOGGLE = _EVT_BITMAP_TOGGLE
"""Identifier for the :data:`BitmapToggleEvent` event."""


BitmapToggleEvent = _BitmapToggleEvent
"""Event emitted when a :class:`BitmapToggleButton` is pushed.

Contains one attribute, ``value``, which contains the current button state
(``True`` or ``False``).
"""
