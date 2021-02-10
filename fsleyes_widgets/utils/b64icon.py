#!/usr/bin/env python
#
# b64icon.py - convert base64-encoded bitmaps into wx.Bitmap obje
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains the :func:`loadBitmap` function, which can be used
to create a ``wx.Bitmap`` object from a base64-encoded image.
"""


import base64 as b64

from io import BytesIO

import wx


class IconError(Exception):
    """Custon ``Exception`` raised when :func:`loadBitmap` cannot load
    an icon.
    """
    pass


def loadBitmap(iconb64):
    """Convert the given ``base64``-encoded byte string to a ``wx.Bitmap``
    object.
    """

    iconbytes = b64.b64decode(iconb64)
    success   = False

    image   = wx.Image()
    success = wx.Image.LoadFile(image, BytesIO(iconbytes))

    if not success:
        raise IconError('Error loading image')

    return image.ConvertToBitmap()
