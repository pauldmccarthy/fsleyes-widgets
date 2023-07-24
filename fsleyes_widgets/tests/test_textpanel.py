#!/usr/bin/env python
#
# test_textpanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

from . import run_with_wx, realYield

import fsleyes_widgets.textpanel as tp

def test_TextPanel():
    run_with_wx(_test_TextPanel)
def _test_TextPanel():
    frame = wx.GetApp().GetTopWindow()
    panel = tp.TextPanel(frame)

    panel.SetLabel('')
    realYield()
    panel.SetLabel('Blab')
    realYield()
    panel.SetOrient(wx.HORIZONTAL)
    realYield()
    panel.SetOrient(wx.VERTICAL)
    realYield()
