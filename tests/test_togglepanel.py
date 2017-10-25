#!/usr/bin/env python
#
# test_togglepanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import fsleyes_widgets.togglepanel as togglepanel

import wx

from . import run_with_wx, simclick, realYield


def test_usage():
    run_with_wx(_test_usage)
def _test_usage():

    frame = wx.GetApp().GetTopWindow()
    pt = togglepanel.TogglePanel(frame, toggleSide=wx.TOP)
    pb = togglepanel.TogglePanel(frame, toggleSide=wx.BOTTOM)
    pl = togglepanel.TogglePanel(frame, toggleSide=wx.LEFT)
    pr = togglepanel.TogglePanel(frame, toggleSide=wx.RIGHT)

    pe = togglepanel.TogglePanel(frame, initialState=True)
    pc = togglepanel.TogglePanel(frame, initialState=False)

    assert pe.IsExpanded()
    assert not pc.IsExpanded()

    pe.Expand()
    assert pe.IsExpanded()

    pe.Collapse()
    assert not pe.IsExpanded()

    pe.Expand(False)
    assert not pe.IsExpanded()

    pe.Expand()
    assert pe.IsExpanded()

    pe.Toggle()
    assert not pe.IsExpanded()

    pe.Toggle()
    assert pe.IsExpanded()

    pnl = togglepanel.TogglePanel(frame)
    pl  = togglepanel.TogglePanel(frame, label='blag')

    assert pnl.GetLabel() is  None
    assert pl .GetLabel() == 'blag'

    pl.SetLabel('fum')
    assert pl .GetLabel() == 'fum'

    pl.SetLabel(None)
    assert pl .GetLabel() is None


def test_event():
    run_with_wx(_test_event)

def _test_event():

    event = [None]
    def ontog(ev):
        event[0] = (ev.GetEventObject(), ev.newState)

    frame   = wx.GetApp().GetTopWindow()
    fsizer  = wx.BoxSizer(wx.HORIZONTAL)
    tp      = togglepanel.TogglePanel(frame)
    panel   = tp.GetPane()
    tpsizer = wx.BoxSizer(wx.VERTICAL)
    content = wx.Button(panel, label='Hey')

    tpsizer.Add(content, flag=wx.EXPAND)
    panel.SetSizer(tpsizer)

    fsizer.Add(tp)
    frame.SetSizer(fsizer)
    frame.Layout()

    realYield()

    tp.Bind(togglepanel.EVT_TOGGLEPANEL_EVENT, ontog)

    sim = wx.UIActionSimulator()

    assert tp.IsExpanded()

    simclick(sim, tp.button)

    assert not tp.IsExpanded()

    assert event[0] is not None
    assert event[0][0] is tp
    assert not event[0][1]

    event[0] = None
    simclick(sim, tp.button)

    assert tp.IsExpanded()

    assert event[0] is not None
    assert event[0][0] is tp
    assert event[0][1]
