#!/usr/bin/env python
#
# test_placeholder_textctrl.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import wx

from . import run_with_wx, realYield

import fsleyes_widgets.placeholder_textctrl as ptc


def test_PlaceholderTextCtrl():
    run_with_wx(_test_PlaceholderTextCtrl)
def _test_PlaceholderTextCtrl():
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    dummy = wx.TextCtrl(frame)
    ctrl  = ptc.PlaceholderTextCtrl(
        frame,
        placeholder='Enter text',
        placeholderColour=(200, 100, 100))
    sizer.Add(dummy, flag=wx.EXPAND)
    sizer.Add(ctrl,  flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()
    realYield()

    assert ctrl.GetPlaceholder()       == 'Enter text'
    assert tuple(ctrl.GetPlaceholderColour()) == (200, 100, 100)
    assert ctrl.GetValue() == ''
    ctrl.SetValue('Bah, humbug')
    assert ctrl.GetValue() == 'Bah, humbug'
    ctrl.SetValue('')

    dummy.SetFocus()
    realYield()
    ctrl.SetFocus()
    realYield()
    dummy.SetFocus()
    realYield()
