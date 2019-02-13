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

    def __init__(self,
                 parent,
                 image=None,
                 preserveAspect=False):
        """Create an ``ImagePanel``.

        If the ``image`` is not passed in here, it can be set later with the
        :meth:`SetImage` method.

        :arg parent:         The :mod:`wx` parent object.

        :arg image:          The :class:`wx.Image` object to display.

        :arg preserveAspect: Defaults to ``False``. If ``True``, the image
                             aspect ratio is preserved.
        """

        wx.Panel.__init__(self, parent)

        self.Bind(wx.EVT_PAINT, self.Draw)
        self.Bind(wx.EVT_SIZE,  self.__onSize)

        self.SetImage(image)

        self.__preserveAspect = preserveAspect


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

        dwidth, dheight = dc.GetSize().Get()

        if dwidth == 0 or dheight == 0:
            return

        if self.__preserveAspect:
            iwidth, iheight = self.__image.GetSize().Get()
            iratio          = float(iwidth) / iheight
            dratio          = float(dwidth) / dheight

            # canvas is too wide - reduce
            # the display image width
            if dratio > iratio:
                dwidth = dheight * iratio

            # canvas is too tall - reduce
            # the display image height
            elif dratio < iratio:
                dheight = dwidth / iratio

        bitmap = self.__image.Scale(dwidth, dheight).ConvertToBitmap()

        dc.DrawBitmap(bitmap, 0, 0, False)
