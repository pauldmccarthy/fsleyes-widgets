#!/usr/bin/env python
#
# test_progress.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

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
