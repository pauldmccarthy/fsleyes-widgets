#!/usr/bin/env python
#
# test_floatspin.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import time

import wx
import mock

import fsleyes_widgets.floatspin as floatspin

from .test_floatslider import (_test_widget_logic,
                               _test_widget_logic_integer,
                               _test_widget_changeRange)

from . import run_with_wx, simclick, simtext, simkey, simfocus, realYield, addall



def test_FloatSpinCtrl_logic():
    run_with_wx(_test_FloatSpinCtrl_logic)
def _test_FloatSpinCtrl_logic():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame)
    _test_widget_logic(spin)


def test_FloatSpinCtrl_logic_integer():
    run_with_wx(_test_FloatSpinCtrl_logic_integer)
def _test_FloatSpinCtrl_logic_integer():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame, style=floatspin.FSC_INTEGER)
    _test_widget_logic_integer(spin)


def test_FloatSpinCtrl_changeRange():
    run_with_wx(_test_FloatSpinCtrl_changeRange)
def _test_FloatSpinCtrl_changeRange():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame)
    _test_widget_changeRange(spin)


def test_FloatSpinCtrl_nolimit():
    run_with_wx(_test_FloatSpinCtrl_nolimit)
def _test_FloatSpinCtrl_nolimit():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame, style=floatspin.FSC_NO_LIMIT)
    spin.SetRange(0, 100)

    values = [-100, -50, -1, 0, 1, 50, 99, 100, 101, 150, 200]


    for v in values:
        spin.SetValue(v)
        assert spin.GetValue() == v


def test_FloatSpinCtrl_spinButtons():
    run_with_wx(_test_FloatSpinCtrl_spinButtons)
def _test_FloatSpinCtrl_spinButtons():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame,
                                    value=0,
                                    minValue=0,
                                    maxValue=100,
                                    increment=1,
                                    evDelta=0.01)

    ev = mock.MagicMock()

    # The FloatSpinCtrl class throttles the
    # rate at which spin button events are
    # processed, so we have to wait between
    # triggering events.

    time.sleep(0.05)
    spin._FloatSpinCtrl__onSpinDown(ev)
    assert spin.GetValue() == 0
    time.sleep(0.05)
    spin._FloatSpinCtrl__onSpinUp(ev)
    assert spin.GetValue() == 1
    time.sleep(0.05)
    spin._FloatSpinCtrl__onSpinDown(ev)
    assert spin.GetValue() == 0
    spin.SetValue(100)
    time.sleep(0.05)
    spin._FloatSpinCtrl__onSpinUp(ev)
    assert spin.GetValue() == 100

    results = [None]

    def handler(ev):
        results[0] = ev.value

    spin.Bind(floatspin.EVT_FLOATSPIN, handler)

    time.sleep(0.05)
    spin.SetValue(50)
    spin._FloatSpinCtrl__onSpinUp(ev)
    realYield()
    assert results[0] == 51

    results[0] = None
    time.sleep(0.05)
    spin.SetValue(50)
    spin._FloatSpinCtrl__onSpinDown(ev)
    realYield()
    assert results[0] == 49


# Mouse wheel down/up
def test_FloatSpinCtrl_mouseWheel():
    run_with_wx(_test_FloatSpinCtrl_mouseWheel)
def _test_FloatSpinCtrl_mouseWheel():

    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame, style=floatspin.FSC_MOUSEWHEEL)
    spin.SetRange(0, 100)

    ev = mock.MagicMock()

    testcases = [
        ( 1, wx.MOUSE_WHEEL_VERTICAL,    1),
        (-1, wx.MOUSE_WHEEL_VERTICAL,   -1),
        ( 1, wx.MOUSE_WHEEL_HORIZONTAL, -1),
        (-1, wx.MOUSE_WHEEL_HORIZONTAL,  1)]

    results = [None]

    def handler(ev):
        results[0] = ev.value

    spin.Bind(floatspin.EVT_FLOATSPIN, handler)


    for rot, axis, expected in testcases:

        results[0] = None
        time.sleep(0.05)
        spin.SetValue(50)

        ev.GetWheelAxis.return_value     = axis
        ev.GetWheelRotation.return_value = rot

        spin._FloatSpinCtrl__onMouseWheel(ev)
        realYield()

        assert results[0]      == 50 + expected
        assert spin.GetValue() == 50 + expected

def test_FloatSpinCtrl_text():
    run_with_wx(_test_FloatSpinCtrl_text)
def _test_FloatSpinCtrl_text():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame)
    sim   = wx.UIActionSimulator()

    addall(frame, [spin])

    spin.SetRange(0, 100)

    result = [0]

    def handler(ev):
        result[0] = ev.value

    enter = [False]

    def enterHandler(ev):
        enter[0] = True

    spin.Bind(floatspin.EVT_FLOATSPIN, handler)
    spin.Bind(wx.EVT_TEXT_ENTER,       enterHandler)

    # input, expected
    testcases = [
        (   '',          0),
        (   '1',         1),
        (   '5',         5),
        ('Baba',         5),
        (   '0',         0),
        (  '20',        20),
        ('-423',         0),
        (  '99',        99),
        ('1055',       100),
        (  '25',        25),
        (  '25.42',  25.42),
        ('1E2',        100),
        ('0.5e2',       50),
        ('2e-1',       0.2),
        ('0.1e-2',   0.001),
    ]

    realYield()

    for text, expected in testcases:

        oldValue  = spin.GetValue()
        result[0] = None
        enter[0]  = False
        spin.textCtrl.ChangeValue(text)
        spin._FloatSpinCtrl__onText(None)
        realYield()
        assert spin.GetValue() == expected

        try:
            float(text)
            assert enter[0]
        except:
            assert not enter[0]

        if oldValue == expected: assert result[0] is None
        else:                    assert result[0] == expected


def test_FloatSpinCtrl_KeyDownUp():
    run_with_wx(_test_FloatSpinCtrl_KeyDownUp)
def _test_FloatSpinCtrl_KeyDownUp():
    frame = wx.GetApp().GetTopWindow()
    spin  = floatspin.FloatSpinCtrl(frame)
    sim   = wx.UIActionSimulator()

    spin.SetRange(0, 100)

    result = [0]

    def handler(ev):
        result[0] = ev.value

    spin.Bind(floatspin.EVT_FLOATSPIN, handler)

    # initialValue, key, expected
    testcases = [
        (50,  wx.WXK_UP,     51),
        (50,  wx.WXK_DOWN,   49),
        (1,   wx.WXK_UP,      2),
        (1,   wx.WXK_DOWN,    0),
        (0,   wx.WXK_UP,      1),
        (0,   wx.WXK_DOWN,    0),
        (99,  wx.WXK_UP,    100),
        (99,  wx.WXK_DOWN,   98),
        (100, wx.WXK_UP,    100),
        (100, wx.WXK_DOWN,   99),
    ]

    spin.textCtrl.SetFocus()

    realYield()

    for value, key, expected in testcases:
        result[0] = None

        spin.SetValue(value)
        simkey(sim, spin.textCtrl, key)

        assert spin.GetValue() == expected

        if expected != value: assert result[0] == expected
        else:                 assert result[0] is None


def test_FloatSpinCtrl_TextLoseFocus():
    run_with_wx(_test_FloatSpinCtrl_TextLoseFocus)
def _test_FloatSpinCtrl_TextLoseFocus():
    frame = wx.GetApp().GetTopWindow()
    sim   = wx.UIActionSimulator()
    spin  = floatspin.FloatSpinCtrl(frame)
    dummy = wx.TextCtrl(frame)

    spin.SetRange(0, 100)

    result = [None]

    def handler(ev):
        result[0] = ev.value

    spin.Bind(floatspin.EVT_FLOATSPIN, handler)

    testcases = [
        (   '1',         1),
        (   '5',         5),
        ('Baba',         5),
        (   '0',         0),
        (  '20',        20),
        ('-423',         0),
        (  '99',        99),
        ('1055',       100),
        (  '25',        25),
        (  '25.42',  25.42),
    ]

    for text, expected in testcases:

        oldValue = spin.GetValue()

        result[0] = None
        spin.textCtrl.SetFocus()
        simtext(sim, spin.textCtrl, text, enter=False)
        simfocus(spin, dummy)

        assert spin.GetValue() == expected

        if oldValue == expected: assert result[0] is None
        else:                    assert result[0] == expected
