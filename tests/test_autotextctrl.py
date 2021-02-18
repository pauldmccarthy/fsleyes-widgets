#!/usr/bin/env python
#
# test_autotextctrl.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


from . import run_with_wx, simclick, simtext, simkey, realYield, addall

import wx
import fsleyes_widgets.autotextctrl as autott


def sendEvent(target, evType, source=None):

    if source is None:
        source = target

    target.ProcessEvent(wx.CommandEvent(evType, source.GetId()))
    realYield()

# Simple test - programmatically
# set, then retrieve the value
def test_getSet():
    run_with_wx( _test_getSet)
def _test_getSet():

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

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
    atc    = autott.AutoTextCtrl(parent, modal=False)

    atc.Bind(autott.EVT_ATC_TEXT_ENTER, handler)

    addall(parent, [atc])

    simtext(sim, atc.textCtrl, 'abc')

    assert atc.GetValue() == 'abc'
    assert called[0]      == 'abc'


# Make sure that when the cotrol receives
# focus, its insertion point is at the end
def test_onFocus():
    run_with_wx(_test_onFocus)
def _test_onFocus():

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

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
    atc = autott.AutoTextCtrl(parent, modal=False)

    addall(parent, [atc])

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    simkey(sim, atc.textCtrl,       wx.WXK_RETURN)
    simkey(sim, atc.popup.textCtrl, wx.WXK_DOWN)
    atc.popup.listBox.SetSelection(1)
    simkey(sim, atc.popup.listBox,  wx.WXK_RETURN)

    assert atc.GetValue() == 'aab'


def test_popup_select2():
    run_with_wx(_test_popup_select2)
def _test_popup_select2():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

    addall(parent, [atc])

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])
    simtext(sim, atc.textCtrl, 'b', enter=False)
    simkey( sim, atc.popup.textCtrl, wx.WXK_DOWN)
    simkey( sim, atc.popup.listBox, wx.WXK_RETURN)

    assert atc.GetValue() == 'bcc'


def test_popup_select3():
    run_with_wx(_test_popup_select3)
def _test_popup_select3():

    sim = wx.UIActionSimulator()
    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

    addall(parent, [atc])

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    simtext(sim, atc, 'ab', enter=False)

    simkey(sim, atc.popup.textCtrl, wx.WXK_DOWN)
    simkey(sim, atc.popup.listBox,  wx.WXK_RETURN)

    assert atc.GetValue() == 'aba'


def test_popup_cancel():
    run_with_wx(_test_popup_cancel)
def _test_popup_cancel():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

    addall(parent, [atc])

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    simkey(sim, atc.textCtrl,       wx.WXK_RETURN)
    simkey(sim, atc.popup.textCtrl, wx.WXK_DOWN)
    simkey(sim, atc.popup.listBox,  wx.WXK_DOWN)
    simkey(sim, atc.popup.listBox,  wx.WXK_ESCAPE)

    assert atc.GetValue() == ''


def test_popup_focusback():
    run_with_wx(_test_popup_focusback)
def _test_popup_focusback():

    sim = wx.UIActionSimulator()

    parent = wx.GetApp().GetTopWindow()
    atc = autott.AutoTextCtrl(parent, modal=False)

    addall(parent, [atc])

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    simkey(sim,  atc.textCtrl, wx.WXK_RETURN)
    simkey(sim,  atc.popup.textCtrl, wx.WXK_DOWN)
    simkey(sim,  atc.popup.listBox,  wx.WXK_UP)
    simtext(sim, atc.popup.textCtrl, 'abc')

    assert atc.GetValue() == 'abc'


def test_popup_dblclick():
    run_with_wx(_test_popup_dblclick)
def _test_popup_dblclick():

    class FakeEv:
        def __init__(self, keycode=None):
            self.keycode = keycode
        def GetKeyCode(self):
            return self.keycode
        def Skip(self):
            pass
        def ResumePropagation(self, a):
            pass

    parent = wx.GetApp().GetTopWindow()
    atc    = autott.AutoTextCtrl(parent, modal=False)

    atc.AutoComplete(['aaa', 'aab', 'aba', 'bcc'])

    addall(parent, [atc])

    atc._AutoTextCtrl__onKeyDown(FakeEv(wx.WXK_RETURN))
    atc.popup.listBox.SetSelection(0)
    atc.popup._AutoCompletePopup__onListMouseDblClick(FakeEv())
    realYield()

    assert atc.GetValue() == 'aaa'
