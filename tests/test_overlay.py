#!/usr/bin/env python


import wx

import fsleyes_widgets.utils.overlay as overlay

from . import run_with_wx


def test_textOverlay():
    run_with_wx(_test_textOverlay)


def _test_textOverlay():

    frame = wx.GetTopWindow()
    overlay.textOverlay(frame, '1 2 3')
