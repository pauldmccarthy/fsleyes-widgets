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

from . import run_with_wx, simclick

import fsleyes_widgets.floatslider as floatslider


def test_FloatSlider_logic():
    run_with_wx(_test_FloatSlider_logic)
def _test_FloatSlider_logic():

    frame = wx.GetApp().GetTopWindow()

    # min, max
    testcases = [
        (     0,      1),
        (    -1,      1),
        (  1e-5,   1e-1),
        (     0,    100),
        (  -100,    100),
        (-2**31,   2**31 - 1),
    ]

    slider = floatslider.FloatSlider(frame)

    slider.SetMin(0)
    slider.SetMax(1)
    assert np.isclose(slider.GetMin(), 0)
    assert np.isclose(slider.GetMax(), 1)

    with pytest.raises(ValueError):
        slider.SetRange(1, 0)

    for minv, maxv in testcases:

        slider.SetRange(minv, maxv)
        assert np.all(np.isclose(slider.GetRange(), (minv, maxv)))

        slider.SetValue(minv - 1)
        assert slider.GetValue() == minv
        slider.SetValue(maxv + 1)
        assert slider.GetValue() == maxv

        testvals = np.linspace(minv, maxv, 100)

        for v in testvals:
            slider.SetValue(v)
            assert np.isclose(slider.GetValue(), v)



def test_FloatSlider_logic_integer():
    run_with_wx(_test_FloatSlider_logic_integer)
def _test_FloatSlider_logic_integer():
    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame)

    testcases = [
        (     0,    100),
        (  -100,    100),
        (-2**31,   2**31 - 1),
    ]

    slider = floatslider.FloatSlider(frame, style=floatslider.FS_INTEGER)

    for minv, maxv in testcases:

        slider.SetRange(minv, maxv)

        assert slider.GetRange() == (minv, maxv)

        if minv == -2**31:
            testvals = np.arange(minv, maxv, 2**24)
        else:
            testvals = np.arange(minv, maxv)

        for v in testvals:
            slider.SetValue(v)
            assert slider.GetValue() == v


def test_FloatSlider_changeRange():
    run_with_wx(_test_FloatSlider_changeRange)
def _test_FloatSlider_changeRange():
    frame  = wx.GetApp().GetTopWindow()
    slider = floatslider.FloatSlider(frame, minValue=0, maxValue=100)
    slider.SetValue(10)
    slider.SetRange(-100, 100)
    assert np.isclose(slider.GetValue(), 10)
    slider.SetRange(11, 100)
    assert np.isclose(slider.GetValue(), 11)
    slider.SetRange(11, 100)
    assert np.isclose(slider.GetValue(), 11)
    slider.SetRange(0, 11)
    assert np.isclose(slider.GetValue(), 11)
    slider.SetRange(0, 5)
    assert np.isclose(slider.GetValue(), 5)


def test_FloatSlider_mouse():
    with mock.patch('fsleyes_widgets.floatslider.wx.Platform', '__WXGTK__'):
        run_with_wx(_test_FloatSlider_mouse)
def _test_FloatSlider_mouse():

    sim    = wx.UIActionSimulator()
    frame  = wx.GetApp().GetTopWindow()
    minval = 0
    maxval = 100
    slider = floatslider.FloatSlider(frame, minValue=minval, maxValue=maxval)

    called = [False]

    def handler(ev):
        called[0] = True

    slider.Bind(wx.EVT_SLIDER, handler)

    xposes = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]

    for xpos in xposes:

        called[0] = False
        simclick(sim, slider, pos=[xpos, 0.5], stype=2)

        wx.Yield()

        expected = minval + xpos * (maxval - minval)

        # Be tolerant with the slider value,
        # because the above xposes may not
        # take into account widget borders.
        tol = (maxval - minval) * 0.05
        assert called[0]
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
