#!/usr/bin/env python
#
# test_floatslider.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import wx

import mock
import pytest

from . import run_with_wx, simtext, simclick, simkey, realYield

import fsleyes_widgets.floatslider as floatslider


# Used by test_FloatSlider_logic and test_SliderSpinPanel_logic.
def _test_widget_logic(widget):

    # min, max
    testcases = [
        (     0,      1),
        (    -1,      1),
        (  1e-5,   1e-1),
        (     0,    100),
        (  -100,    100),
        (-2**31,   2**31 - 1),
    ]

    widget.SetMin(0)
    widget.SetMax(1)
    assert np.isclose(widget.GetMin(), 0)
    assert np.isclose(widget.GetMax(), 1)

    # Min > max
    with pytest.raises(ValueError):
        widget.SetRange(1, 0)

    # Min > max
    with pytest.raises(ValueError):
        widget.SetMin(2)

    # Max < min
    with pytest.raises(ValueError):
        widget.SetMax(-1)

    # Min == max
    widget.SetRange(0, 0)
    assert widget.GetRange() == (0, 0)
    assert widget.GetMin() == 0
    assert widget.GetMax() == 0
    widget.SetValue(1)
    assert widget.GetValue() == 0
    widget.SetValue(-1)
    assert widget.GetValue() == 0
    widget.SetValue(0)
    assert widget.GetValue() == 0

    for minv, maxv in testcases:

        widget.SetRange(minv, maxv)
        assert np.all(np.isclose(widget.GetRange(), (minv, maxv)))

        widget.SetValue(minv - 1)
        assert widget.GetValue() == minv
        widget.SetValue(maxv + 1)
        assert widget.GetValue() == maxv

        testvals = np.linspace(minv, maxv, 100)

        for v in testvals:
            widget.SetValue(v)
            assert np.isclose(widget.GetValue(), v)


# Used by test_FloatSlider_logic_integer and
# test_SliderSpinPanel_logic_integer
def _test_widget_logic_integer(widget):

    testcases = [
        (     0,    100),
        (  -100,    100),
        (-2**31,   2**31 - 1),
    ]

    for minv, maxv in testcases:

        widget.SetRange(minv, maxv)

        assert widget.GetRange() == (minv, maxv)

        if minv == -2**31:
            testvals = np.arange(minv, maxv, 2**24)
        else:
            testvals = np.arange(minv, maxv)

        for v in testvals:
            widget.SetValue(v)
            assert widget.GetValue() == v


# You should get it by now
def _test_widget_changeRange(widget):
    widget.SetRange(0, 100)
    widget.SetValue(10)
    widget.SetRange(-100, 100)
    assert np.isclose(widget.GetValue(), 10)
    widget.SetRange(11, 100)
    assert np.isclose(widget.GetValue(), 11)
    widget.SetRange(0, 11)
    assert np.isclose(widget.GetValue(), 11)
    widget.SetRange(0, 5)
    assert np.isclose(widget.GetValue(), 5)


def test_FloatSlider_logic():
    run_with_wx(_test_FloatSlider_logic)
def _test_FloatSlider_logic():
    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame)
    _test_widget_logic(slider)


def test_FloatSlider_logic_integer():
    run_with_wx(_test_FloatSlider_logic_integer)
def _test_FloatSlider_logic_integer():
    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame, style=floatslider.FS_INTEGER)
    _test_widget_logic_integer(slider)


def test_FloatSlider_changeRange():
    run_with_wx(_test_FloatSlider_changeRange)
def _test_FloatSlider_changeRange():
    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame)
    _test_widget_changeRange(slider)


def test_FloatSlider_mouse_non_gtk():
    run_with_wx(_test_FloatSlider_mouse)
def test_FloatSlider_mouse_gtk():
    with mock.patch('fsleyes_widgets.floatslider.wx.Platform', '__WXGTK__'):
        run_with_wx(_test_FloatSlider_mouse)
def _test_FloatSlider_mouse():

    sim    = wx.UIActionSimulator()
    frame  = wx.GetApp().GetTopWindow()
    minval = 0
    init   = 50
    maxval = 100
    slider = floatslider.FloatSlider(frame,
                                     value=init,
                                     minValue=minval,
                                     maxValue=maxval)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(slider, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()
    wx.Yield()

    called = [0]

    def handler(ev):
        called[0] += 1

    slider.Bind(wx.EVT_SLIDER, handler)

    xposes = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]

    for xpos in xposes:

        called[0] = 0

        # Make sure clicking on the same spot
        # doesn't result in multiple events
        simclick(sim, slider, pos=[xpos, 0.5])

        expected = minval + xpos * (maxval - minval)

        # Be tolerant with the slider value,
        # because the above xposes may not
        # take into account widget borders.
        tol = (maxval - minval) * 0.05
        assert called[0] == 1
        assert abs(slider.GetValue() - expected) <= tol



def test_FloatSlider_wheel():
    run_with_wx(_test_FloatSlider_wheel)
def _test_FloatSlider_wheel():

    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame,
                                     value=50,
                                     minValue=0,
                                     maxValue=100,
                                     style=floatslider.FS_MOUSEWHEEL)

    called = [False]

    def handler(ev):
        called[0] = True

    slider.Bind(wx.EVT_SLIDER, handler)

    ev = mock.MagicMock()


    # UIActionSimulator don't do mouse wheel,
    # so we fake a mousewheel event
    val = slider.GetValue()
    ev.GetWheelRotation.return_value = 1
    slider._FloatSlider__onMouseWheel(ev)
    wx.Yield()
    assert called[0]
    assert slider.GetValue() > val


    val = slider.GetValue()

    called[0] = False
    ev.GetWheelRotation.return_value = -1
    slider._FloatSlider__onMouseWheel(ev)
    wx.Yield()
    assert called[0]
    assert slider.GetValue() < val

    val = slider.GetValue()

    called[0] = False
    ev.GetWheelRotation.return_value = 0
    slider._FloatSlider__onMouseWheel(ev)
    wx.Yield()
    assert not called[0]
    assert np.isclose(slider.GetValue(), val)



def test_SliderSpinPanel_logic():
    run_with_wx(_test_SliderSpinPanel_logic)
def _test_SliderSpinPanel_logic():
    frame = wx.GetApp().GetTopWindow()
    panel = floatslider.SliderSpinPanel(frame)
    _test_widget_logic(panel)


def test_SliderSpinPanel_logic_integer():
    run_with_wx(_test_SliderSpinPanel_logic_integer)
def _test_SliderSpinPanel_logic_integer():
    frame  = wx.GetApp().GetTopWindow()
    panel = floatslider.SliderSpinPanel(frame, style=floatslider.SSP_INTEGER)
    _test_widget_logic_integer(panel)


def test_SliderSpinPanel_changeRange():
    run_with_wx(_test_SliderSpinPanel_changeRange)
def _test_SliderSpinPanel_changeRange():
    frame = wx.GetApp().GetTopWindow()
    panel = floatslider.SliderSpinPanel(frame)
    _test_widget_changeRange(panel)


def test_SliderSpinPanel_show_edit_limits():
    run_with_wx(_test_SliderSpinPanel_show_edit_limits)
def _test_SliderSpinPanel_show_edit_limits():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = floatslider.SliderSpinPanel(
        frame,
        style=floatslider.SSP_SHOW_LIMITS | floatslider.SSP_EDIT_LIMITS)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    panel.SetRange(0, 100)

    result = [None]

    def handler(ev):
        result[0] = (ev.min, ev.max)

    panel.Bind(floatslider.EVT_SSP_LIMIT, handler)

    numberdlg = mock.MagicMock()
    numberdlg.ShowModal.return_value = wx.ID_OK
    numberdlg.GetValue .return_value = 9

    minbtn = panel._SliderSpinPanel__minButton
    maxbtn = panel._SliderSpinPanel__maxButton

    # limbutton, value, expectedrange, shouldTriggerEvent
    testcases = [
        (minbtn,   50, (  50, 100),  True),
        (minbtn,  150, (  50, 100), False),
        (minbtn, -100, (-100, 100),  True),
        (maxbtn,   50, (-100,  50),  True),
        (maxbtn, -200, (-100,  50), False),
        (maxbtn,  500, (-100, 500),  True),

    ]

    with mock.patch('fsleyes_widgets.floatslider.numberdialog.NumberDialog',
                    return_value=numberdlg):

        for btn, val, expected, shouldEv in testcases:

            result[0] = None

            numberdlg.GetValue.return_value = val

            simclick(sim, btn)
            assert tuple(panel.GetRange()) == expected

            if shouldEv: assert result[0] == expected
            else:        assert result[0] is None


def test_SliderSpinPanel_events():
    run_with_wx(_test_SliderSpinPanel_events)
def _test_SliderSpinPanel_events():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = floatslider.SliderSpinPanel(frame, label='Value', style=0)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()

    ncalls = [0]
    called = [None]

    def handler(ev):
        ncalls[0] += 1
        called[0] = ev.value

    panel.Bind(floatslider.EVT_SSP_VALUE, handler)

    panel.SetRange(0, 100)

    realYield()
    simclick(sim, panel.slider, pos=[0.5, 0.5])

    assert abs(panel.spinCtrl.GetValue() - 50) < 5
    assert abs(panel.slider  .GetValue() - 50) < 5
    assert abs(panel         .GetValue() - 50) < 5
    assert called[0]                 - 50 < 5
    assert ncalls[0] == 1

    called[0] = None
    ncalls[0] = 0
    simtext(sim, panel.spinCtrl.textCtrl, '75')

    assert np.isclose(panel.spinCtrl.GetValue(), 75)
    assert np.isclose(panel.slider  .GetValue(), 75)
    assert np.isclose(panel         .GetValue(), 75)
    assert np.isclose(called[0],                 75)
    assert ncalls[0] == 1


def test_SliderSpinPanel_nolimit():
    run_with_wx(_test_SliderSpinPanel_nolimit)
def _test_SliderSpinPanel_nolimit():
    frame = wx.GetApp().GetTopWindow()
    panel = floatslider.SliderSpinPanel(frame, style=floatslider.SSP_NO_LIMITS)

    panel.SetRange(0, 100)

    values = [-100, -50, -1, 0, 1, 50, 99, 100, 101, 150, 200]

    for v in values:
        panel.SetValue(v)
        assert panel.GetValue() == v
