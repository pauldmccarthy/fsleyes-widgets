#!/usr/bin/env python
#
# test_rangeslider.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import wx

import mock
import pytest

import fsleyes_widgets.rangeslider as rangeslider

from . import run_with_wx, simclick, simtext, simkey, realYield


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

    panel.SetLow(5)
    assert np.all(np.isclose(panel.GetRange(), (5, 100)))
    panel.SetHigh(95)
    assert np.all(np.isclose(panel.GetRange(), (5, 95)))
    panel.SetLow(95)
    assert np.all(np.isclose(panel.GetRange(), (92.5, 97.5)))
    panel.SetRange(50, 75)
    panel.SetHigh(51)
    assert np.all(np.isclose(panel.GetRange(), (48, 53)))

    with pytest.raises(ValueError): panel.SetRange( 100, 0)
    with pytest.raises(ValueError): panel.SetLimits(100, 0)
    with pytest.raises(ValueError): panel.SetDistance(101)
    with pytest.raises(ValueError): panel.SetLimits(0, 3)

    # range, expected
    testcases = [
        ((  0, 100), (    0,   100)),
        ((  5, 100), (    5,   100)),
        ((  5,  95), (    5,    95)),
        (( 95,  95), ( 92.5,  97.5)),
        (( 95, 100), (   95,   100)),
        (( 90,  90), ( 87.5,  92.5)),
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
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()

    handlersCalled = [False] * 3

    def lowHandler(  ev): handlersCalled[0] = True
    def highHandler( ev): handlersCalled[1] = True
    def rangeHandler(ev): handlersCalled[2] = True

    def reset():
        handlersCalled[0] = False
        handlersCalled[1] = False
        handlersCalled[2] = False

    panel.Bind(rangeslider.EVT_LOW_RANGE,  lowHandler)
    panel.Bind(rangeslider.EVT_HIGH_RANGE, highHandler)
    panel.Bind(rangeslider.EVT_RANGE,      rangeHandler)
    panel.SetRange(0, 100)
    panel.SetDistance(5)

    simclick(sim, panel.lowWidget,  pos=[0.25, 0.5])
    assert abs(panel.GetLow() - 25) < 5
    assert  panel.GetHigh() == 100
    assert handlersCalled == [True, False, False]

    reset()
    simclick(sim, panel.highWidget, pos=[0.75, 0.5])
    assert abs(panel.GetLow()  - 25) < 5
    assert abs(panel.GetHigh() - 75) < 5
    assert handlersCalled == [False, True, False]

    reset()
    simclick(sim, panel.highWidget, pos=[0.25, 0.5])
    assert abs(panel.GetLow()  - 20) < 5
    assert abs(panel.GetHigh() - 25) < 5
    assert handlersCalled == [False, False, True]

    reset()
    panel.SetRange(25, 75)
    simclick(sim, panel.lowWidget,  pos=[0.75, 0.5])
    assert abs(panel.GetLow()  - 75) < 5
    assert abs(panel.GetHigh() - 80) < 5
    assert handlersCalled == [False, False, True]

    reset()
    panel.SetRange(25, 75)
    simclick(sim, panel.lowWidget, pos=[0.90, 0.5])
    assert abs(panel.GetLow()  - 90) < 5
    assert abs(panel.GetHigh() - 95) < 5
    assert handlersCalled == [False, False, True]

    reset()
    panel.SetRange(25, 75)
    simclick(sim, panel.highWidget, pos=[0.1, 0.5])
    assert abs(panel.GetLow()  -  5)  < 5
    assert abs(panel.GetHigh() -  10) < 5
    assert handlersCalled == [False, False, True]


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

    handlersCalled = [False] * 3

    def lowHandler(  ev): handlersCalled[0] = True
    def highHandler( ev): handlersCalled[1] = True
    def rangeHandler(ev): handlersCalled[2] = True

    def reset():
        handlersCalled[0] = False
        handlersCalled[1] = False
        handlersCalled[2] = False

    panel.SetRange(0, 100)
    panel.SetDistance(5)

    realYield()

    panel.lowWidget.textCtrl.ChangeValue('25')
    simkey(sim, panel.lowWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (25, 100)))

    panel.highWidget.textCtrl.ChangeValue('75')
    simkey(sim, panel.highWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (25, 75)))

    panel.highWidget.textCtrl.ChangeValue('25')
    simkey(sim, panel.highWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (22.5, 27.5)))

    panel.SetRange(25, 75)
    panel.lowWidget.textCtrl.ChangeValue('75')
    simkey(sim, panel.lowWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (72.5, 77.5)))

    panel.SetRange(25, 75)
    panel.lowWidget.textCtrl.ChangeValue('90')
    simkey(sim, panel.lowWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (90, 95)))

    panel.SetRange(25, 75)
    panel.highWidget.textCtrl.ChangeValue('10')
    simkey(sim, panel.highWidget, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (5, 10)))



def test_RangeSliderSpinPanel_logic():
    run_with_wx(_test_RangeSliderSpinPanel_logic)
def _test_RangeSliderSpinPanel_logic():
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangeSliderSpinPanel(frame,
                                             lowLabel='Low',
                                             highLabel='High')
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()
    _test_RangePanel_logic(panel)


def test_RangeSliderSpinPanel_onchange():
    run_with_wx(_test_RangeSliderSpinPanel_onchange)
def _test_RangeSliderSpinPanel_onchange():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangeSliderSpinPanel(frame,
                                             lowLabel='Low',
                                             highLabel='High',
                                             style=0)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()

    called = [False]

    def handler(ev):
        called[0] = True

    panel.Bind(rangeslider.EVT_LOW_RANGE,  handler)
    panel.Bind(rangeslider.EVT_HIGH_RANGE, handler)
    panel.Bind(rangeslider.EVT_RANGE,      handler)

    panel.SetRange(0, 100)
    panel.SetDistance(5)

    realYield()

    panel.lowSpin.textCtrl.ChangeValue('75')
    simkey(sim, panel.lowSpin.textCtrl, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (75, 100)))
    assert np.isclose(panel.lowSpin.GetValue(),   75)
    assert np.isclose(panel.lowSlider.GetValue(), 75)
    assert called[0]

    called[0] = False
    panel.highSpin.textCtrl.ChangeValue('60')
    simkey(sim, panel.highSpin.textCtrl, wx.WXK_RETURN)
    assert np.all(np.isclose(panel.GetRange(), (55, 60)))
    assert np.isclose(panel.highSpin.GetValue(),   60)
    assert np.isclose(panel.highSlider.GetValue(), 60)
    assert called[0]

    called[0] = False
    simclick(sim, panel.lowSlider, pos=[0.25, 0.5])
    assert abs(panel          .GetLow()   - 25) < 5
    assert abs(panel.lowSpin  .GetValue() - 25) < 5
    assert abs(panel.lowSlider.GetValue() - 25) < 5
    assert called[0]

    called[0] = False
    simclick(sim, panel.highSlider, pos=[0.90, 0.5])
    assert abs(panel           .GetHigh()  - 90) < 5
    assert abs(panel.highSpin  .GetValue() - 90) < 5
    assert abs(panel.highSlider.GetValue() - 90) < 5
    assert called[0]

def test_RangeSliderSpinPanel_onlimit():
    run_with_wx(_test_RangeSliderSpinPanel_onlimit)
def _test_RangeSliderSpinPanel_onlimit():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = rangeslider.RangeSliderSpinPanel(
        frame,
        style=rangeslider.RSSP_SHOW_LIMITS | rangeslider.RSSP_EDIT_LIMITS)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()

    panel.SetLimits(0, 100)
    panel.SetRange( 0, 100)

    called = [False]

    def handler(ev):
        called[0] = True

    panel.Bind(rangeslider.EVT_RANGE_LIMIT, handler)

    numberdlg = mock.MagicMock()
    numberdlg.ShowModal.return_value = wx.ID_OK
    numberdlg.GetValue .return_value = 9

    minbtn = panel.minButton
    maxbtn = panel.maxButton

    # limbutton, value, expectedrange, shouldTriggerEvent
    testcases = [
        (minbtn,   50, (  50, 100),  True),
        (minbtn,  150, (  50, 100), False),
        (minbtn, -100, (-100, 100),  True),
        (maxbtn,   50, (-100,  50),  True),
        (maxbtn, -200, (-100,  50), False),
        (maxbtn,  500, (-100, 500),  True),
    ]

    with mock.patch('fsleyes_widgets.rangeslider.numberdialog.NumberDialog',
                    return_value=numberdlg):

        for btn, val, expected, shouldEv in testcases:

            called[0] = None

            numberdlg.GetValue.return_value = val

            simclick(sim, btn)
            assert tuple(panel.GetLimits()) == expected

            if shouldEv: assert     called[0]
            else:        assert not called[0]
