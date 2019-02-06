#!/usr/bin/env python
#
# test_bitmapradio.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

import pytest

import wx

from . import run_with_wx, simclick, realYield

import fsleyes_widgets.bitmapradio  as bmpradio
import fsleyes_widgets.bitmaptoggle as bmptoggle


datadir = op.join(op.dirname(__file__), 'testdata', 'bitmapbuttons')


def test_Create():
    run_with_wx(_test_Create)
def _test_Create():

    falseicon = op.join(datadir, 'false.png')
    trueicon  = op.join(datadir, 'true.png')
    falseicon = wx.Bitmap(falseicon, wx.BITMAP_TYPE_PNG)
    trueicon  = wx.Bitmap(trueicon,  wx.BITMAP_TYPE_PNG)

    frame = wx.GetApp().GetTopWindow()

    btn1 = bmpradio.BitmapRadioBox(frame)
    btn2 = bmpradio.BitmapRadioBox(frame, style=wx.HORIZONTAL)
    btn3 = bmpradio.BitmapRadioBox(frame, style=wx.VERTICAL)

    for btn in [btn1, btn2, btn3]:

        with pytest.raises(IndexError):
            btn.SetSelection(0)

        btn.Set([trueicon, falseicon])
        btn.SetSelection(0)
        assert btn.GetSelection() == 0
        btn.SetSelection(1)
        assert btn.GetSelection() == 1

        btn.EnableChoice(0)
        btn.EnableChoice(0, False)
        btn.DisableChoice(0)

        with pytest.raises(IndexError):
            btn.EnableChoice(2)

        with pytest.raises(IndexError):
            btn.SetSelection(2)

        btn.Clear()
        with pytest.raises(IndexError):
            btn.SetSelection(0)

        btn.AddChoice(trueicon,  falseicon)
        btn.AddChoice(falseicon, trueicon)

        btn.SetSelection(0)
        assert btn.GetSelection() == 0
        btn.SetSelection(1)
        assert btn.GetSelection() == 1

        with pytest.raises(IndexError):
            btn.SetSelection(2)


def test_Event():
    run_with_wx(_test_Event)
def _test_Event():
    falseicon = wx.Bitmap(op.join(datadir, 'false.png'), wx.BITMAP_TYPE_PNG)
    trueicon  = wx.Bitmap(op.join(datadir, 'true.png'),  wx.BITMAP_TYPE_PNG)

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = wx.Panel(frame)
    rad   = bmpradio.BitmapRadioBox(panel)
    szr   = wx.BoxSizer(wx.HORIZONTAL)
    szr.Add(rad, flag=wx.EXPAND)
    panel.SetSizer(szr)

    result = [None]

    def handler(ev):
        result[0] = (ev.index, ev.clientData)

    rad.Bind(bmpradio.EVT_BITMAP_RADIO_EVENT, handler)

    rad.Set([trueicon, falseicon], ['true', 'false'])

    panel.Layout()
    panel.Fit()
    realYield()

    btns = []
    for c in rad.GetChildren():
        if isinstance(c, bmptoggle.BitmapToggleButton):
            btns.append(c)

    simclick(sim, btns[0])
    assert result[0] == (0, 'true')
    simclick(sim, btns[1])
    assert result[0] == (1, 'false')
