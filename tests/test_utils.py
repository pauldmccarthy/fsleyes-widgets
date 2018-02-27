#!/usr/bin/env python
#
# test_isalive.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import fsleyes_widgets as fw

from . import run_with_wx, realYield


def test_isalive():
    run_with_wx(_test_isalive)

def _test_isalive():
    frame   = wx.GetApp().GetTopWindow()
    sizer   = wx.BoxSizer(wx.VERTICAL)
    panel   = wx.Panel(frame)
    child1  = wx.Panel(panel)
    child2  = wx.Panel(panel)

    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(child1, flag=wx.EXPAND, proportion=1)
    sizer.Add(child2, flag=wx.EXPAND, proportion=1)
    panel.SetSizer(sizer)

    assert fw.isalive(child1)
    assert fw.isalive(child2)

    sizer.Detach(child1)
    child1.Destroy()

    sizer.Layout()
    frame.Refresh()

    realYield(100)

    assert not fw.isalive(child1)
    assert     fw.isalive(child2)


def test_wxversion():
    run_with_wx(_test_wxversion)
def _test_wxversion():
    fw.wxversion()
