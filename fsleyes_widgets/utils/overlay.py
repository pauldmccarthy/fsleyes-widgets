#!/usr/bin/env python
#
# overlay.py - Functions for painting things on top of wx widgets.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains convenience functions for drawing arbitrary things
on top of ``wx`` widgets.

.. autosummary::
   :nosignatures:

   textOverlay
"""


import wx


def textOverlay(target,
                text,
                box=True,
                bgColour=(205, 205, 255),
                fgColour=(0, 0, 0)):
    """Shows the given ``text`` on the given ``target``.

    :arg target:   ``wx.Window`` object

    :arg text:     Text to display

    :arg box:      If ``True`` (the default), the text is displayed in a
                   box.

    :arg bgColour: If ``box is True``, the box is filled with this colour.

    :arg fgColour: Colour to draw the text in
    """

    dc     = wx.ClientDC(target)
    w, h   = dc.GetSize().Get()
    w      = dc.DeviceToLogicalX(w)
    h      = dc.DeviceToLogicalY(h)
    tw, th = dc.GetTextExtent(text).Get()
    x      = int((w - tw) / 2)
    y      = int((h - th) / 2)

    if box:
        dc.SetBrush(wx.Brush(wx.Colour(bgColour)))
        dc.DrawRoundedRectangle(x - 5, y - 5, tw + 10, th + 10, 2)

    dc.SetTextForeground(wx.Colour(fgColour))
    dc.DrawText(text, x, y)
