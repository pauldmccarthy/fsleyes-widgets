#!/usr/bin/env python
#
# test_progress.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import time
import wx

import numpy as np

import mock

from . import run_with_wx, simclick, simtext, simkey, realYield

from fsleyes_widgets import isalive
import fsleyes_widgets.utils.progress as progress


def test_Bounce():
    run_with_wx(_test_Bounce)
def _test_Bounce():

    endfuncs = ['Close', 'EndModal', 'Destroy']
    delay    = 200  # msecs
    centis   = delay / 10
    values   = list(np.arange(50))
    passed   = [True]

    for endfunc in endfuncs:

        dlg = progress.Bounce('Title', 'Message', delay=delay, values=values)

        dlg.StartBounce()

        def eval():
            value = dlg.GetValue()

            for i in range(10):

                realYield(centis + 0.5 * centis)
                newval = dlg.GetValue()

                passed[0] = passed[0] and (newval != value)
                value     = newval

            value = dlg.GetValue()
            dlg.StopBounce()
            getattr(dlg, endfunc)()

            realYield((delay * 2) / 10)

            if isalive(dlg):
                passed[0] = passed[0] and (dlg.GetValue() == value)

        if endfunc == 'EndModal':
            wx.CallAfter(eval)
            dlg.ShowModal()
        else:
            dlg.Show()
            eval()
        if endfunc is not 'Destroy':
            dlg.Destroy()
        dlg = None
        assert passed[0]


def test_Bounce_manual():
    run_with_wx(_test_Bounce_manual)
def _test_Bounce_manual():

    dlg = progress.Bounce('Title', 'Message', delay=150)

    # make sure it's not bouncing
    val = dlg.GetValue()
    realYield(20)
    assert dlg.GetValue() == val

    # Make sure a bounce changes the value
    dlg.DoBounce()
    assert dlg.GetValue() != val

    # Make sure we can change the message
    val = dlg.GetValue()
    dlg.DoBounce('New message')
    assert dlg.GetValue()   != val
    assert dlg.GetMessage() == 'New message'

    dlg.Destroy()

def test_Bounce_auto_start_stop():
    run_with_wx(_test_Bounce_auto_start_stop)
def _test_Bounce_auto_start_stop():

    dlg = progress.Bounce('Title', 'Message', delay=100)

    dlg.StartBounce()
    val = dlg.GetValue()
    realYield(15)
    assert dlg.GetValue() != val
    val = dlg.GetValue()
    realYield(15)
    assert dlg.GetValue() != val
    val = dlg.GetValue()
    dlg.StopBounce()

    realYield(15)
    assert dlg.GetValue() == val
    realYield(15)
    assert dlg.GetValue() == val

    dlg.StartBounce()
    val = dlg.GetValue()
    realYield(15)
    assert dlg.GetValue() != val
    val = dlg.GetValue()
    realYield(15)
    assert dlg.GetValue() != val
    val = dlg.GetValue()
    dlg.StopBounce()
    dlg.Destroy()


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

    dlg = progress.Bounce('Title', 'message', style=wx.PD_CAN_ABORT)

    with mock.patch('wx.ProgressDialog.WasCancelled', return_value=True):
        assert not progress.Bounce.runWithBounce(func, dlg=dlg)

    dlg.Destroy()
