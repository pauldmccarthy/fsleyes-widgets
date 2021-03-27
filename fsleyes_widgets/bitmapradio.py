#!/usr/bin/env python
#
# bitmapradio.py - A radio control with bitmap buttons.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`BitmapRadioBox` class, a radio control
which uses bitmap toggle buttons.
"""

import wx
import wx.lib.newevent as wxevent

from . import bitmaptoggle


# TODO Button tooltips


class BitmapRadioBox(wx.Panel):
    """A radio control which displays a collection of :class:`wx.ToggleButton`
    controls, each of which displays an image.

    Each of these buttons corresponds to a mutually exclusive option - when
    the user clicks on a button, it is toggled *on*, and all of the others are
    toggled *off*.

    For example, here is a ``BitmapRadioBox`` which allows the user to switch
    between *view* mode and *edit* mode:

     .. image:: images/bitmapradiobox.png
        :scale: 50%
        :align: center

    When the user pushes a button, a :data:`EVT_BITMAP_RADIO_EVENT` is
    generated.
    """

    def __init__(self, parent, style=None):
        """Create a ``BitmapRadioBox``.

        :arg parent: A parent window.

        :arg style: A combination of :attr:`BMPRADIO_ALLOW_DESELECTED`, and
                    one of ``wx.HORIZONTAL`` (the default) or
                    ``wx.VERTICAL``, to control the button layout direction
        """
        wx.Panel.__init__(self, parent)

        if style is None:
            style = wx.HORIZONTAL

        if style & wx.VERTICAL: szorient = wx.VERTICAL
        else:                   szorient = wx.HORIZONTAL

        self.__allowDeselected = style & BMPRADIO_ALLOW_DESELECTED
        self.__selection       = -1
        self.__buttons         = []
        self.__clientData      = []
        self.__sizer           = wx.BoxSizer(szorient)

        self.SetSizer(self.__sizer)


    @property
    def buttons(self):
        """Returns a list containing the :class:`.BitmapToggleButton`
        instances. Used for testing.
        """
        return list(self.__buttons)


    def AddChoice(self, selectedBmp, unselectedBmp=None, clientData=None):
        """Add a button to this ``BitmapRadioBox``.

        :arg selectedBmp:   A :class:`wx.Bitmap` to display on the button when
                            it is selected.

        :arg unselectedBmp: Optional. A :class:`wx.Bitmap` to display on the
                            button when it is not selected.

        :arg clientData:    Arbitrary data which is associated with the choice.
        """

        style  = wx.BU_EXACTFIT | wx.ALIGN_CENTRE | wx.BU_NOTEXT
        button = bitmaptoggle.BitmapToggleButton(self,
                                                 trueBmp=selectedBmp,
                                                 falseBmp=unselectedBmp,
                                                 style=style)

        self.__buttons   .append(button)
        self.__clientData.append(clientData)

        self.__sizer.Add(button, flag=wx.EXPAND, proportion=1)
        self.Layout()

        button.Bind(bitmaptoggle.EVT_BITMAP_TOGGLE, self.__onButton)

        if (not self.__allowDeselected) and (self.__selection == -1):
            self.SetSelection(0)


    def Clear(self):
        """Remove all buttons from this ``BitmapRadioBox``."""

        self.__sizer.Clear(True)
        self.__selection  = -1
        self.__buttons    = []
        self.__clientData = []


    def EnableChoice(self, index, enable=True):
        """Enable or disable the button at the specified index. """
        self.__buttons[index].Enable(enable)


    def DisableChoice(self, index=None):
        """Disable the button at the specified index. """
        self.EnableChoice(index, False)


    def Set(self, bitmaps, clientData=None):
        """Set all buttons at once.

        :arg bitmaps:    A list of :class:`wx.Bitmap` objects.

        :arg clientData: A list of arbitrary data to associate with each
                         choice.
        """

        if clientData is None:
            clientData = [None] * len(bitmaps)

        self.Clear()
        for bmp, cd in zip(bitmaps, clientData):
            self.AddChoice(bmp, clientData=cd)


    def GetSelection(self):
        """Returns the index of the curently selected choice."""
        return self.__selection


    def SetSelection(self, index):
        """Sets the current selection."""

        if index < -1 or index >= len(self.__buttons):
            raise IndexError('Invalid index {}'.format(index))

        if (not self.__allowDeselected) and (index == -1):
            raise IndexError('Invalid index {}'.format(index))

        self.__selection = index

        for i, button in enumerate(self.__buttons):

            if i == index: button.SetValue(True)
            else:          button.SetValue(False)


    def __onButton(self, ev):
        """Called when a button is pushed. Updates the selection,
        and emits a :data:`BitmapRadioEvent`.
        """

        button = ev.GetEventObject()
        idx    = self.__buttons.index(button)
        data   = self.__clientData[idx]

        if self.__allowDeselected and (idx == self.GetSelection()):
            value = False
            self.SetSelection(-1)
        else:
            value = True
            self.SetSelection(idx)

        ev = BitmapRadioEvent(index=idx, clientData=data, value=value)
        wx.PostEvent(self, ev)


BMPRADIO_ALLOW_DESELECTED = 1
"""Style flag which allows all buttons to be de-selected. If not specified
(the default), one button must always be selected.
"""


_BitampRadioEvent, _EVT_BITMAP_RADIO_EVENT = wxevent.NewEvent()


EVT_BITMAP_RADIO_EVENT = _EVT_BITMAP_RADIO_EVENT
"""Identifier for the :data:`BitmapRadioEvent`. """


BitmapRadioEvent = _BitampRadioEvent
"""Event emitted when the user changes the radio selection. Contains
the following attributes:

  - ``index``:      The index of the new selection.
  - ``clientData``: Client data associated with the new selection.
  - ``value``:      ``False`` if :attr:`BMPRADIO_ALLOW_DESELECTED` is active,
                    and  the selected button was clicked on (thus deselecting
                    it), ``True`` otherwise.
"""
