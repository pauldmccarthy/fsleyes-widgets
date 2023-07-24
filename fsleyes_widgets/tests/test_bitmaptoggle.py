#!/usr/bin/env python
#
# test_bitmaptoggle.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

import wx

import fsleyes_widgets.bitmaptoggle as bmptoggle

from . import run_with_wx, simclick

datadir = op.join(op.dirname(__file__), 'testdata', 'bitmapbuttons')


def test_Create():
    run_with_wx(_test_Create)
def _test_Create():

    frame = wx.GetApp().GetTopWindow()


    falseicon = op.join(datadir, 'false.png')
    trueicon  = op.join(datadir, 'true.png')

    falseicon = wx.Bitmap(falseicon, wx.BITMAP_TYPE_PNG)
    trueicon  = wx.Bitmap(trueicon,  wx.BITMAP_TYPE_PNG)

    btn = bmptoggle.BitmapToggleButton(frame)
    btn = bmptoggle.BitmapToggleButton(frame,
                                       trueBmp=trueicon)
    btn = bmptoggle.BitmapToggleButton(frame,
                                       trueBmp=trueicon,
                                       falseBmp=falseicon)

    btn = bmptoggle.BitmapToggleButton(frame)
    btn.SetBitmap(trueicon)
    btn.SetBitmap(trueicon, falseicon)


def test_SetGet():
    run_with_wx(_test_SetGet)
def _test_SetGet():

    frame = wx.GetApp().GetTopWindow()
    btn = bmptoggle.BitmapToggleButton(frame)

    btn.SetValue(True)
    assert btn.GetValue()

    btn.SetValue(False)
    assert not btn.GetValue()


def test_Toggle():
    run_with_wx(_test_Toggle)
def _test_Toggle():
    falseicon = op.join(datadir, 'false.png')
    trueicon  = op.join(datadir, 'true.png')

    falseicon = wx.Bitmap(falseicon, wx.BITMAP_TYPE_PNG)
    trueicon  = wx.Bitmap(trueicon,  wx.BITMAP_TYPE_PNG)

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    btn   = bmptoggle.BitmapToggleButton(frame)
    btn.SetBitmap(trueicon, falseicon)

    assert not btn.GetValue()
    simclick(sim, btn)
    assert btn.GetValue()


def test_Event():
    run_with_wx(_test_Event)
def _test_Event():
    trueicon = op.join(datadir, 'true.png')
    trueicon = wx.Bitmap(trueicon,  wx.BITMAP_TYPE_PNG)

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    btn   = bmptoggle.BitmapToggleButton(frame)
    btn.SetBitmap(trueicon)

    result = [None]

    def handler(ev):
        result[0] = ev.value

    btn.Bind(bmptoggle.EVT_BITMAP_TOGGLE, handler)

    simclick(sim, btn)
    assert result[0]
    simclick(sim, btn)
    assert not result[0]
