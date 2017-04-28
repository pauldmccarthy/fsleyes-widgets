#!/usr/bin/env python
#
# test_colourbutton.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import mock
import pytest

from . import run_with_wx, simclick

import fsleyes_widgets.colourbutton as cb


def test_Create():
    run_with_wx(_test_Create)
def _test_Create():

    frame = wx.GetApp().GetTopWindow()
    btn = cb.ColourButton(frame)

    assert list(btn.GetValue()) == [0, 0, 0, 255]
    btn.SetValue((20, 30, 40))
    assert list(btn.GetValue()) == [20, 30, 40, 255]
    btn.SetValue((20, 30, 40, 50))
    assert list(btn.GetValue()) == [20, 30, 40, 50]


    with pytest.raises(ValueError): btn.SetValue([0])
    with pytest.raises(ValueError): btn.SetValue([0, 1])
    with pytest.raises(ValueError): btn.SetValue([0, 1, 2, 3, 4])
    with pytest.raises(ValueError): btn.SetValue([-1, 0, 2])
    with pytest.raises(ValueError): btn.SetValue([256, 20, 6])



class MockColourDialog(object):

    retval = wx.ID_OK
    colour = [0, 0, 0, 255]

    def __init__(self, parent, colourData):
        self.colourData = colourData

    def ShowModal(self):
        self.colourData.SetColour(MockColourDialog.colour)
        return MockColourDialog.retval

    def GetColourData(self):
        return self.colourData


def test_Event():
    run_with_wx(_test_Event)
def _test_Event():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    btn   = cb.ColourButton(frame)

    colours = [(50, 60, 70),
               (90, 100, 150, 200)]

    result = [None]

    def handler(ev):
        result[0] = ev.colour

    btn.Bind(cb.EVT_COLOUR_BUTTON_EVENT, handler)

    for colour in colours:

        MockColourDialog.colour = colour

        with mock.patch('fsleyes_widgets.colourbutton.wx.ColourDialog',
                        side_effect=MockColourDialog):
            simclick(sim, btn)

        if len(colour) == 3:
            colour = list(colour) + [255]

        assert list(result[0])      == list(colour)
        assert list(btn.GetValue()) == list(colour)

    # Test dialog cancel
    MockColourDialog.retval = wx.ID_CANCEL
    MockColourDialog.colour = (20, 20, 20, 10)

    colour = (150, 160, 170)
    result = [None]
    btn.SetValue(colour)

    with mock.patch('fsleyes_widgets.colourbutton.wx.ColourDialog',
                    side_effect=MockColourDialog):
        simclick(sim, btn)

    assert result[0] is None
    assert list(btn.GetValue()) == list(colour) + [255]
