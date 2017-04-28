#!/usr/bin/env python
#
# test_autotextctrl.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from . import run_with_wx

import wx
import fsleyes_widgets.autotextctrl as autott


def sendEvent(target, evType, source=None):

    if source is None:
        source = target

    target.ProcessEvent(wx.CommandEvent(evType, source.GetId()))
    wx.Yield()

# Simple test - programmatically
# set, then retrieve the value
def test_AutoTextCtrl_getSet():
    run_with_wx( _test_AutoTextCtrl_getSet)
def _test_AutoTextCtrl_getSet():

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.ChangeValue('a')
    assert atc.GetValue() == 'a'

    atc.SetValue('b')
    assert atc.GetValue() == 'b'


def test_AutoTextCtrl_event():
    run_with_wx( _test_AutoTextCtrl_event)
def _test_AutoTextCtrl_event():

    called = [None]

    def handler(ev):
        called[0] = ev.text

    sim    = wx.UIActionSimulator()
    parent = wx.GetApp().GetTopWindow()
    atc    = autott.AutoTextCtrl(parent)

    atc.Bind(autott.EVT_ATC_TEXT_ENTER, handler)
    atc.SetFocus()
    sim.Char(ord('a'))
    sim.Char(ord('b'))
    sim.Char(ord('c'))
    sim.KeyDown(wx.WXK_RETURN)
    wx.Yield()

    assert atc.GetValue() == 'abc'
    assert called[0]      == 'abc'


# Make sure that when the cotrol receives
# focus, its insertion point is at the end
def test_AutoTextCtrl_onFocus():
    run_with_wx(_test_AutoTextCtrl_onFocus)
def _test_AutoTextCtrl_onFocus():

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
def test_AutoTextCtrl_popup_select1():
    run_with_wx(_test_AutoTextCtrl_popup_select1)
def _test_AutoTextCtrl_popup_select1():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    wx.Yield()

    assert atc.GetValue() == 'aab'


def test_AutoTextCtrl_popup_select2():
    run_with_wx(_test_AutoTextCtrl_popup_select2)
def _test_AutoTextCtrl_popup_select2():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.Char(ord('b'))
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    wx.Yield()

    assert atc.GetValue() == 'bcc'


def test_AutoTextCtrl_popup_select3():
    run_with_wx(_test_AutoTextCtrl_popup_select3)
def _test_AutoTextCtrl_popup_select3():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.Char(ord('a'))
    sim.Char(ord('b'))
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_RETURN)
    wx.Yield()

    assert atc.GetValue() == 'aba'


def test_AutoTextCtrl_popup_cancel():
    run_with_wx(_test_AutoTextCtrl_popup_cancel)
def _test_AutoTextCtrl_popup_cancel():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_ESCAPE)
    wx.Yield()

    assert atc.GetValue() == ''


def test_AutoTextCtrl_popup_focusback():
    run_with_wx(_test_AutoTextCtrl_popup_focusback)
def _test_AutoTextCtrl_popup_focusback():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    atc.SetFocus()
    sim.KeyDown(wx.WXK_RETURN)
    sim.KeyDown(wx.WXK_DOWN)
    sim.KeyDown(wx.WXK_UP)

    sim.Text('abc')
    sim.KeyDown(wx.WXK_RETURN)
    wx.Yield()

    assert atc.GetValue() == 'abc'
