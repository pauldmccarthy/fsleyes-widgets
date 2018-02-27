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
    menuBar = wx.MenuBar()
    menu1   = wx.Menu()
    menu2   = wx.Menu()
    menu3   = wx.Menu()
    sizer   = wx.BoxSizer(wx.VERTICAL)
    panel   = wx.Panel(frame)
    child1  = wx.Panel(panel)
    child2  = wx.Panel(panel)

    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.SetMenuBar(menuBar)

    menuBar        .Append(       menu1, 'menu1')
    menuBar        .Append(       menu2, 'menu2')
    menu3id = menu2.AppendSubMenu(menu3, 'menu3').GetId()

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

    menu2  .Remove(menu3id)
    menuBar.Remove( 1)

    assert     fw.isalive(menu1)
    assert not fw.isalive(menu3)


def test_wxversion():
    run_with_wx(_test_wxversion)
def _test_wxversion():
    fw.wxversion()
