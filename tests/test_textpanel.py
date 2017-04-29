#!/usr/bin/env python
#
# test_textpanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

from . import run_with_wx

import fsleyes_widgets.textpanel as tp

def test_TextPanel():
    run_with_wx(_test_TextPanel)
def _test_TextPanel():
    frame = wx.GetApp().GetTopWindow()
    panel = tp.TextPanel(frame)

    panel.SetLabel('')
    wx.Yield()
    panel.SetLabel('Blab')
    wx.Yield()
    panel.SetOrient(wx.HORIZONTAL)
    wx.Yield()
    panel.SetOrient(wx.VERTICAL)
    wx.Yield()
