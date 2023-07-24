#!/usr/bin/env python
#
# test_imagepanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path as op

import wx

from . import run_with_wx, realYield

import fsleyes_widgets.imagepanel as ip


datadir = op.join(op.dirname(__file__), 'testdata', 'bitmapbuttons')


def test_ImagePanel():
    run_with_wx(_test_ImagePanel)
def _test_ImagePanel():

    icon = op.join(datadir, 'true.png')
    icon = wx.Bitmap(icon,  wx.BITMAP_TYPE_PNG)
    icon = icon.ConvertToImage()

    frame  = wx.GetApp().GetTopWindow()
    panel1 = ip.ImagePanel(frame)
    realYield()
    panel1.SetImage(icon)
    realYield()
    panel2 = ip.ImagePanel(frame, preserveAspect=True)
    realYield()
    panel2.SetImage(icon)
    realYield()
