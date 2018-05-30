#!/usr/bin/env python
#
# imagepanel.py - A panel for displaying a wx.Image.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`ImagePanel` class, for displaying a
:class:`wx.Image`.
"""


import wx


class ImagePanel(wx.Panel):
    """A :class:`wx.Panel` which may be used to display a resizeable
    :class:`wx.Image`. The image is scaled to the size of the panel.
    """

    def __init__(self, parent, image=None):
        """Create an ``ImagePanel``.

        If the ``image`` is not passed in here, it can be set later with the
        :meth:`SetImage` method.

        :arg parent: The :mod:`wx` parent object.

        :arg image:  The :class:`wx.Image` object to display.
        """

        wx.Panel.__init__(self, parent)

        self.Bind(wx.EVT_PAINT, self.Draw)
        self.Bind(wx.EVT_SIZE,  self.__onSize)

        self.SetImage(image)


    def SetImage(self, image):
        """Set the image that is displayed on this ``ImagePanel``.

        :arg image: The :class:`wx.Image` object to display.
        """
        self.__image = image

        self.Refresh()


    def __onSize(self, ev):
        """Redraw this panel when it is sized, so the image is scaled
        appropriately - see the :meth:`Draw` method.
        """
        self.Refresh()
        ev.Skip()


    def Draw(self, ev=None):
        """Draws this ``ImagePanel``. The image is scaled to the current panel
        size.
        """

        self.ClearBackground()

        if self.__image is None:
            return

        if ev is None: dc = wx.ClientDC(self)
        else:          dc = wx.PaintDC( self)

        if not dc.IsOk():
            return

        width, height = dc.GetSize().Get()

        if width == 0 or height == 0:
            return

        bitmap = self.__image.Scale(width, height).ConvertToBitmap()

        dc.DrawBitmap(bitmap, 0, 0, False)
