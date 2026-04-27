#!/usr/bin/env python
#
# test_filepanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import fsleyes_widgets as fw

from fsleyes_widgets.tests import (realYield,
                                   run_with_wx,
                                   simclick,
                                   MockFileDialog)


def test_FilePanel():
    run_with_wx(_test_FilePanel)

def _test_FilePanel():

    sim      = wx.UIActionSimulator()
    frame    = wx.GetApp().GetTopWindow()
    sizer    = wx.BoxSizer(wx.VERTICAL)
    fpanel   = fw.FilePanel(frame, 'initial')

    sizer.Add(fpanel)
    frame.SetSizer(sizer)
    frame.Layout()

    realYield()

    assert fpanel.GetFilePath() == 'initial'

    fpanel.SetFilePath('newval')
    realYield()
    assert fpanel.GetFilePath() == 'newval'

    with MockFileDialog() as mockdlg:
        mockdlg.GetPath_retval = 'loadval'
        simclick(sim, fpanel.loadButton)
        assert fpanel.GetFilePath() == 'loadval'

    with MockFileDialog() as mockdlg:
        mockdlg.GetPath_retval = 'loadval2'
        mockdlg.ShowModal_retval = wx.ID_CANCEL
        simclick(sim, fpanel.loadButton)
        assert fpanel.GetFilePath() == 'loadval'
