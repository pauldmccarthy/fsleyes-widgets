#!/usr/bin/env python
#
# test_runwindow.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os
import time
import signal
import tempfile

import fsleyes_widgets.utils.runwindow as runwindow

from . import run_with_wx, realYield


def _gen_dummy_script():

    script = """#!/bin/bash
    for ((i=0;i<10;i++)); do
        echo "$i"
        echo "err$i" 1>&2
    done
    """

    hd, path = tempfile.mkstemp()

    hd = os.fdopen(hd, 'w')
    hd.write(script)
    hd.close()

    expected   = '\n'.join('{0}\nerr{0}'.format(i) for i in range(10))

    return path, expected


# import logging
# logging.basicConfig()
# logging.getLogger('fsleyes_widgets').setLevel(logging.DEBUG)
def test_ProcessManager_run():

    path, expected = _gen_dummy_script()
    cmd            = ['bash', path]
    result         = [None]
    finishArgs     = [None]

    def runTest():
        import wx

        def onFinish(parent, retcode):
            finishArgs[0] = (parent, retcode)
            result[    0] = rp.text.GetValue()

        frame = wx.GetApp().GetTopWindow()
        rp    = runwindow.RunPanel(frame)
        pm    = runwindow.ProcessManager(cmd, frame, rp, onFinish)

        pm.start()

    run_with_wx(runTest)

    os.remove(path)

    assert expected in result[0]
    assert finishArgs[0][1] == 0



def test_ProcessManager_termProc():

    cmd        = 'sleep 10'.split()
    finishArgs = [None]

    def runTest():
        import wx

        def onFinish(parent, retcode):
            finishArgs[0] = (parent, retcode)

        frame = wx.GetApp().GetTopWindow()
        rp    = runwindow.RunPanel(frame)
        pm    = runwindow.ProcessManager(cmd, frame, rp, onFinish)

        pm.start()

        for i in range(2):
            realYield()
            time.sleep(1)

        pm.termProc()

    run_with_wx(runTest)

    assert finishArgs[0][1] == -signal.SIGTERM


def test_run():

    import wx

    path, expected = _gen_dummy_script()
    cmd            = ['bash', path]
    finishArgs     = [None]

    def runTest():

        frame = wx.GetApp().GetTopWindow()

        def onFinish(parent, retcode):
            finishArgs[0] = (parent, retcode)

        runwindow.run('Tool', cmd, frame, onFinish, modal=False)

    run_with_wx(runTest)

    os.remove(path)

    assert finishArgs[0][1] == 0
