#!/usr/bin/env python
#
# test_isalive.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from unittest import mock

import wx

import fsleyes_widgets as fw

from . import run_with_wx, run_without_wx, realYield


def test_isalive():
    run_with_wx(_test_isalive)

def _test_isalive():
    frame   = wx.GetApp().GetTopWindow()
    sizer   = wx.BoxSizer(wx.VERTICAL)
    panel   = wx.Panel(frame)
    child1  = wx.Panel(panel)
    child2  = wx.Panel(panel)

    sizer.Add(panel, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(child1, flag=wx.EXPAND, proportion=1)
    sizer.Add(child2, flag=wx.EXPAND, proportion=1)
    panel.SetSizer(sizer)

    assert fw.isalive(child1)
    assert fw.isalive(child2)

    sizer.Detach(child1)
    child1.Destroy()

    sizer.Layout()
    frame.Refresh()

    realYield(100)

    assert not fw.isalive(child1)
    assert     fw.isalive(child2)


def test_wxversion():
    fw.wxversion()
    with run_without_wx():
        assert fw.wxversion is None


def test_wxVersion():
    with mock.patch('wx.__version__', '4.0.0'):
        assert fw.wxVersion() == '4.0.0'
    with mock.patch('wx.__version__', '4.1.1'):
        assert fw.wxVersion() == '4.1.1'
    with mock.patch('wx.__version__', '4.0.7.post2'):
        assert fw.wxVersion() == '4.0.7'
    with mock.patch('wx.__version__', 'invalid'):
        assert fw.wxVersion() is None
    with run_without_wx():
        assert fw.wxVersion() is None


def test_wxFlavour():
    with run_without_wx():
        assert fw.wxFlavour() is None
    with mock.patch('wx.PlatformInfo', ['phoenix']):
        assert fw.wxFlavour()  == fw.WX_PHOENIX
    with mock.patch('wx.PlatformInfo', ['oldversion']):
        assert fw.wxFlavour()  == fw.WX_PYTHON


def test_wxPlatform():
    with run_without_wx():
        assert fw.wxPlatforn() is None
    with mock.patch('wx.PlatformInfo', ['cocoa']):
        assert fw.wxPlatform()  == fw.WX_MAC_COCOCA
    with mock.patch('wx.PlatformInfo', ['carbon']):
        assert fw.wxPlatform()  == fw.WX_MAC_CARBON
    with mock.patch('wx.PlatformInfo', ['gtk']):
        assert fw.wxPlatform()  == fw.WX_GTK


def test_frozen():
    assert not fw.frozen()
    with mock.patch('sys.frozen', True):
        assert fw.frozen()


def test_canHaveGui():
    with run_without_wx():
        assert not fw.canHaveGui()
    with mock.patch('wx.App.IsDisplayAvailable', return_value=False):
        assert not fw.canHaveGui()
    with mock.patch('wx.App.IsDisplayAvailable', return_value=True):
        assert fw.canHaveGui()


@run_with_wx
def test_haveGui1():
    assert fw.haveGui()

def test_haveGui2():
    with run_without_wx():
        assert not fw.haveGui()

    assert not fw.haveGui()


def test_inSSHSession():

    sshVars = ['SSH_CLIENT', 'SSH_TTY']

    for sv in sshVars:
        with mock.patch.dict('os.environ', **{sv : '1'}):
            assert fw.inSSHSession()

    with mock.patch('os.environ', {}):
        assert not fw.inSSHSession()


def test_inVNCSession():
    vncVars = ['VNCDESKTOP', 'X2GO_SESSION', 'NXSESSIONID']

    for vv in vncVars:
        with mock.patch.dict('os.environ', **{vv : '1'}):
            assert fw.inVNCSession()

    with mock.patch('os.environ', {}):
        assert not fw.inVNCSession()


def test_glRenderer():
    assert fw.glVersion() is None
    fw.glVersion.version  = '2.1'
    assert fw.glVersion() == '2.1'
    fw.glVersion.version = None


def test_glRenderer():
    assert fw.glRenderer() is None
    fw.glRenderer.renderer  = 'llvmpipe'
    assert fw.glRenderer() == 'llvmpipe'
    fw.glRenderer.renderer = None


def test_glIsSoftwareRenderer():
    assert fw.glRenderer() is None
    assert fw.glIsSoftwareRenderer() is None
    fw.glRenderer.renderer = 'nvidia'
    assert not fw.glIsSoftwareRenderer()
    fw.glRenderer.renderer = 'software'
    assert fw.glIsSoftwareRenderer()
    fw.glRenderer.renderer = None
