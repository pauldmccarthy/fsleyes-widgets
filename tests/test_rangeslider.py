#!/usr/bin/env python
#
# test_rangeslider.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import wx

import fsleyes_widgets.rangeslider as rangeslider

from . import run_with_wx, simclick, simtext, simkey


def _test_RangePanel_logic(panel):
    panel.SetLimits(100, 1000)
    assert panel.GetLimits() == (100, 1000)
    assert panel.GetMin()    == 100
    assert panel.GetMax()    == 1000
    panel.SetMin(0)
    panel.SetMax(100)
    assert panel.GetLimits() == (0, 100)
    assert panel.GetMin()    == 0
    assert panel.GetMax()    == 100
    panel.SetRange(0, 100)
    panel.SetDistance(5)
    assert panel.GetRange()    == (0, 100)
    assert panel.GetLow()      == 0
    assert panel.GetHigh()     == 100
    assert panel.GetDistance() == 5

    panel.SetLimits(80, 50)
    assert panel.GetLimits() == (50, 80)
    assert panel.GetRange()  == (50, 80)
    panel.SetLimits(0, 100)
    panel.SetRange(100, 0)
    assert panel.GetRange() == (0, 100)

    panel.SetLow(5)
    assert np.all(np.isclose(panel.GetRange(), (5, 100)))
    panel.SetHigh(95)
    assert np.all(np.isclose(panel.GetRange(), (5, 95)))
    panel.SetLow(95)
    assert np.all(np.isclose(panel.GetRange(), (92.5, 97.5)))
    panel.SetRange(50, 75)
    panel.SetHigh(51)
    assert np.all(np.isclose(panel.GetRange(), (48, 53)))

    # range, expected
    testcases = [
        ((  0, 100), (    0,   100)),
        ((  5, 100), (    5,   100)),
        ((  5,  95), (    5,    95)),
        (( 95,  95), ( 92.5,  97.5)),
        (( 95, 100), (   95,   100)),
        (( 90,  90), ( 87.5,  92.5)),
        ((100,   0), (    0,   100)),
        ((  0,   0), (    0,     5)),
        ((  0,   5), (    0,     5)),
        ((  0,  10), (    0,    10)),
        ((100, 100), (   95,   100)),
    ]

    for inrange, expected in testcases:
        panel.SetRange(*inrange)
        assert np.all(np.isclose(panel.GetRange(), expected))

    panel.SetRange(0, 100)
    panel.SetLimits(25, 50)
    assert np.all(np.isclose(panel.GetRange(), (25, 50)))

    panel.SetRange(30, 35)
    panel.SetDistance(10)
    assert np.all(np.isclose(panel.GetRange(), (27.5, 37.5)))


import logging
logging.basicConfig()

def test_RangePanel_logic_slider():
    run_with_wx(_test_RangePanel_logic_slider)
def _test_RangePanel_logic_slider():

    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangePanel(frame, style=rangeslider.RP_SLIDER)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()
    _test_RangePanel_logic(panel)


def test_RangePanel_logic_spin():
    run_with_wx(_test_RangePanel_logic_spin)
def _test_RangePanel_logic_spin():
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangePanel(frame,
                                   lowLabel='min',
                                   highLabel='max')
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()
    _test_RangePanel_logic(panel)


def test_RangePanel_events_slider():
    run_with_wx(_test_RangePanel_events_slider)
def _test_RangePanel_events_slider():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangePanel(frame, style=rangeslider.RP_SLIDER)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    panel.SetRange(0, 100)
    panel.SetDistance(5)

    simclick(sim, panel.lowWidget,  pos=[0.25, 0.5])
    assert panel.GetHigh() == 100
    assert (panel.GetLow() - 25) < 5

    simclick(sim, panel.highWidget, pos=[0.75, 0.5])
    assert (panel.GetHigh() - 75) < 5
    assert (panel.GetLow()  - 25) < 5

    simclick(sim, panel.highWidget, pos=[0.25, 0.5])
    assert (panel.GetHigh() - 27.5) < 5
    assert (panel.GetLow()  - 22.5) < 5


def test_RangePanel_events_spin():
    run_with_wx(_test_RangePanel_events_spin)
def _test_RangePanel_events_spin():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangePanel(frame)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    panel.SetRange(0, 100)
    panel.SetDistance(5)

    panel.lowWidget.textCtrl.ChangeValue('25')
    simkey(sim, panel.lowWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (25, 100)))

    panel.highWidget.textCtrl.ChangeValue('75')
    simkey(sim, panel.highWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (25, 75)))

    panel.highWidget.textCtrl.ChangeValue('25')
    simkey(sim, panel.highWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (22.5, 27.5)))
