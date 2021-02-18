#!/usr/bin/env python
#
# test_numberdialog.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import wx

import fsleyes_widgets.numberdialog as numdlg

from . import run_with_wx, simclick, simtext, simkey, realYield


def test_NumberDialog_create():
    run_with_wx(_test_NumberDialog_create)
def _test_NumberDialog_create():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()

    testcases = [
        ({'real' : False, 'initial' :    999}, 'ok',        999),
        ({'real' : False, 'initial' :   -999}, 'ok',       -999),
        ({'real' : True,  'initial' : 0.3443}, 'ok',     0.3443),
        ({'real' : True,  'initial' :  -0.48}, 'ok',      -0.48),
        ({'real' : True,  'initial' : 0.3443}, 'cancel',   None),
    ]

    for kwargs, target, expected in testcases:
        dlg = numdlg.NumberDialog(
            frame,
            title='NumberDialog test',
            message='Enter a number',
            **kwargs)

        if target == 'ok': target = dlg.okButton
        else:              target = dlg.cancelButton

        dlg.Show()
        realYield()

        simclick(sim, target)
        assert dlg.GetValue() == expected


def simtextnd(nd, text, changed):
    class FakeEv:
        def __init__(self, changed):
            self.changed = changed
    nd.floatSpinCtrl.textCtrl.ChangeValue(text)
    nd.floatSpinCtrl._FloatSpinCtrl__onText(None)
    nd._NumberDialog__onEnter(FakeEv(changed))


def test_NumberDialog_limit():
    run_with_wx(_test_NumberDialog_limit)
def _test_NumberDialog_limit():
    frame = wx.GetApp().GetTopWindow()

    # kwargs, input, needClick, expected
    testcases = [
        ({'real'     : False,
          'minValue' : 0,
          'maxValue' : 100}, '50', False, 50),
        ({'real'     : False,
          'minValue' : 0,
          'maxValue' : 100}, '0',  False,  0),
        ({'real'     : False,
          'minValue' : 0,
          'maxValue' : 100}, '-1', True,  0),
        ({'real'     : False,
          'minValue' : 0,
          'maxValue' : 100}, '100', False, 100),
        ({'real'     : False,
          'minValue' : 0,
          'maxValue' : 100}, '101', True, 100),

        ({'real'     : True,
          'minValue' : 0,
          'maxValue' : 1}, '0.745', False, 0.745),
        ({'real'     : True,
          'minValue' : 0,
          'maxValue' : 1}, '0.0', False, 0.0),
        ({'real'     : True,
          'minValue' : 0,
          'maxValue' : 1}, '-25.9', True, 0.0),
        ({'real'     : True,
          'minValue' : 0,
          'maxValue' : 1}, '25.9', True, 1.0),
        ({'real'     : True,
          'minValue' : 0,
          'maxValue' : 1}, '1.0', False, 1.0),
    ]

    for kwargs, text, needClick, expected in testcases:
        dlg = numdlg.NumberDialog(frame, **kwargs)

        dlg.Show()

        simtextnd(dlg, text, needClick)
        if needClick:
            assert dlg.GetValue() is None
            dlg._NumberDialog__onOk(None)

        assert dlg.GetValue() == expected
