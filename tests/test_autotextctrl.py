#!/usr/bin/env python
#
# test_autotextctrl.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from . import run_with_wx, simclick, realYield

import wx
import fsleyes_widgets.autotextctrl as autott


def sendEvent(target, evType, source=None):

    if source is None:
        source = target

    target.ProcessEvent(wx.CommandEvent(evType, source.GetId()))
    wx.Yield()

# Simple test - programmatically
# set, then retrieve the value
def test_getSet():
    run_with_wx( _test_getSet)
def _test_getSet():

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.ChangeValue('a')
    assert atc.GetValue() == 'a'

    atc.SetValue('b')
    assert atc.GetValue() == 'b'


def test_event():
    run_with_wx( _test_event)
def _test_event():

    called = [None]

    def handler(ev):
        called[0] = ev.text

    sim    = wx.UIActionSimulator()
    parent = wx.GetApp().GetTopWindow()
    atc    = autott.AutoTextCtrl(parent)

    atc.Bind(autott.EVT_ATC_TEXT_ENTER, handler)
    atc.SetFocus()
    realYield()
    sim.Char(ord('a'))
    sim.Char(ord('b'))
    sim.Char(ord('c'))
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    assert atc.GetValue() == 'abc'
    assert called[0]      == 'abc'


# Make sure that when the cotrol receives
# focus, its insertion point is at the end
def test_onFocus():
    run_with_wx(_test_onFocus)
def _test_onFocus():

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.ChangeValue('a')
    atc.SetInsertionPoint(0)

    sendEvent(atc, wx.wxEVT_KILL_FOCUS)

    assert atc.GetInsertionPoint() == 0

    sendEvent(atc, wx.wxEVT_SET_FOCUS)
    assert atc.GetInsertionPoint() == 1


# Test showing the popup and selecting a value
def test_popup_select1():
    run_with_wx(_test_popup_select1)
def _test_popup_select1():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])
    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    realYield()
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    assert atc.GetValue() == 'aab'


def test_popup_select2():
    run_with_wx(_test_popup_select2)
def _test_popup_select2():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.Char(ord('b'))
    realYield()
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    assert atc.GetValue() == 'bcc'


def test_popup_select3():
    run_with_wx(_test_popup_select3)
def _test_popup_select3():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.Char(ord('a'))
    sim.Char(ord('b'))
    realYield()
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    assert atc.GetValue() == 'aba'


def test_popup_cancel():
    run_with_wx(_test_popup_cancel)
def _test_popup_cancel():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    realYield()
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_ESCAPE)
    realYield()

    assert atc.GetValue() == ''


def test_popup_focusback():
    run_with_wx(_test_popup_focusback)
def _test_popup_focusback():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    realYield()
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_UP)
    realYield()

    sim.Text('abc')
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    assert atc.GetValue() == 'abc'


def test_popup_dblclick():
    run_with_wx(_test_popup_dblclick)
def _test_popup_dblclick():
    sim    = wx.UIActionSimulator()
    parent = wx.GetApp().GetTopWindow()
    atc    = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    realYield()

    # Sneakily get a ref to the listbox
    # in the AutoCompletePopup
    realYield()
    listbox = None
    for c in atc.GetChildren():
        if isinstance(c, autott.AutoCompletePopup):

            for pc in c.GetChildren():
                if isinstance(pc, wx.ListBox):
                    listbox = pc
                    break

    simclick(sim, listbox, stype=1, pos=[0.5, 0.05])
    realYield()

    assert atc.GetValue() == 'aaa'
