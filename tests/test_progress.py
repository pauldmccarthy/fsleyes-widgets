#!/usr/bin/env python
#
# test_progress.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import time
import wx

from . import run_with_wx, simclick, simtext, simkey, realYield

from fsleyes_widgets import isalive
import fsleyes_widgets.utils.progress as progress


def test_Bounce():
    run_with_wx(_test_Bounce)
def _test_Bounce():

    endfuncs = ['Close', 'EndModal', 'Destroy']
    delay    = 200

    for endfunc in endfuncs:

        dlg = progress.Bounce('Title', 'Message', delay=delay)

        dlg.StartBounce()

        def eval():
            value = dlg.GetValue()

            for i in range(10):

                realYield((delay + 10) / 10)

                newval = dlg.GetValue()

                assert newval != value
                value = newval

            value = dlg.GetValue()
            getattr(dlg, endfunc)()

            realYield((delay * 2) / 10)

            if isalive(dlg):
                assert dlg.GetValue() == value

        if endfunc == 'EndModal':
            wx.CallAfter(eval)
            dlg.ShowModal()
        else:
            eval()


def test_runWithBounce():
    run_with_wx(_test_runWithBounce)
def _test_runWithBounce():

    finished = [False]

    def func():
        for i in range(5):
            time.sleep(0.5)
        finished[0] = True

    assert progress.Bounce.runWithBounce(func, 'Title', 'Message', delay=100)
    assert finished[0]


def test_runWithBounce_cancel():
    run_with_wx(_test_runWithBounce_cancel)
def _test_runWithBounce_cancel():

    def func():
        for i in range(10):
            time.sleep(1)

    sim = wx.UIActionSimulator()
    dlg = progress.Bounce('Title', 'message', style=wx.PD_CAN_ABORT)

    def cancel():
        simkey(sim, dlg, ord(' '))

    wx.CallLater(1000, cancel)

    assert not progress.Bounce.runWithBounce(func, dlg=dlg)
