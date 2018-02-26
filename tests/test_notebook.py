#!/usr/bin/env python
#
# test_notebook.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import itertools as it

import pytest

import wx

from . import run_with_wx, simclick, realYield


import fsleyes_widgets.notebook as nb


def nb_run_with_wx(func):
    def wrapper():

        frame = wx.GetApp().GetTopWindow()

        for side, ornt in it.product((wx.HORIZONTAL, wx.VERTICAL),
                                     (wx.LEFT, wx.RIGHT, wx.TOP, wx.BOTTOM)):
            func(side, ornt)
            frame.DestroyChildren()

    run_with_wx(wrapper)


def test_setColours():
    run_with_wx(_test_setColours)
def _test_setColours():
    frame    = wx.GetApp().GetTopWindow()
    notebook = nb.Notebook(frame)

    page1 = wx.Panel(notebook)
    notebook.AddPage(page1, 'page1')

    notebook.SetButtonColours(text='#ffffff',
                              default='#000000',
                              selected='#0000ff')


def test_add_remove():
    nb_run_with_wx(_test_add_remove)
def _test_add_remove(side, ornt):

    frame    = wx.GetApp().GetTopWindow()
    sizer    = wx.BoxSizer(wx.VERTICAL)
    notebook = nb.Notebook(frame, style=side | ornt)

    sizer.Add(notebook)
    frame.SetSizer(sizer)
    frame.Layout()

    # the notebook should reset the page parent
    page1 = wx.Panel(frame)
    page2 = wx.Panel(notebook)
    page3 = wx.Panel(notebook)

    with pytest.raises(IndexError):
        notebook.InsertPage(-1, page1, 'page1')
    with pytest.raises(IndexError):
        notebook.InsertPage(1,  page1, 'page1')

    assert notebook.PageCount() == 0
    notebook.InsertPage(0, page1, 'page1')
    assert notebook.PageCount() == 1
    notebook.AddPage(page3, 'page3')
    assert notebook.PageCount() == 2
    notebook.InsertPage(1, page2, 'page2')
    assert notebook.PageCount() == 3

    realYield()

    with pytest.raises(IndexError):
        notebook.RemovePage(-1)
    with pytest.raises(IndexError):
        notebook.RemovePage(3)

    assert notebook.pages[0] is page1
    assert notebook.pages[1] is page2
    assert notebook.pages[2] is page3

    assert notebook.FindPage(page1) == 0
    assert notebook.FindPage(page2) == 1
    assert notebook.FindPage(page3) == 2
    notebook.RemovePage(0)
    assert notebook.PageCount() == 2
    assert notebook.FindPage(page1) == wx.NOT_FOUND
    assert notebook.FindPage(page2) == 0
    assert notebook.FindPage(page3) == 1
    notebook.DeletePage(1)
    assert notebook.PageCount() == 1
    assert notebook.FindPage(page1) == wx.NOT_FOUND
    assert notebook.FindPage(page2) == 0
    assert notebook.FindPage(page3) == wx.NOT_FOUND
    notebook.RemovePage(0)
    assert notebook.PageCount() == 0
    assert notebook.FindPage(page1) == wx.NOT_FOUND
    assert notebook.FindPage(page2) == wx.NOT_FOUND
    assert notebook.FindPage(page3) == wx.NOT_FOUND

    realYield()


def test_selection():
    nb_run_with_wx(_test_selection)
def _test_selection(side, ornt):
    frame    = wx.GetApp().GetTopWindow()
    notebook = nb.Notebook(frame, style=side | ornt)
    page1 = wx.Panel(notebook)
    page2 = wx.Panel(notebook)
    page3 = wx.Panel(notebook)

    notebook.AddPage(page1, 'page1')
    notebook.AddPage(page2, 'page2')
    notebook.AddPage(page3, 'page3')

    assert notebook.GetSelection() == 0
    notebook.SetSelection(1)
    assert notebook.GetSelection() == 1
    notebook.SetSelection(2)
    assert notebook.GetSelection() == 2
    notebook.SetSelection(0)
    assert notebook.GetSelection() == 0

    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 1
    notebook.AdvanceSelection(False)
    assert notebook.GetSelection() == 0

    with pytest.raises(IndexError):
        notebook.SetSelection(-1)
    with pytest.raises(IndexError):
        notebook.SetSelection(3)

    notebook.DeletePage(0)
    assert notebook.GetSelection() == 0
    notebook.SetSelection(1)
    notebook.DeletePage(0)
    assert notebook.GetSelection() == 0
    notebook.DeletePage(0)
    assert notebook.GetSelection() is None


def test_enable_disable_show_hide():
    nb_run_with_wx(_test_enable_disable_show_hide)
def _test_enable_disable_show_hide(side, ornt):
    frame    = wx.GetApp().GetTopWindow()
    sizer    = wx.BoxSizer(wx.VERTICAL)
    notebook = nb.Notebook(frame, style=side | ornt)
    page1    = wx.Panel(notebook)
    page2    = wx.Panel(notebook)
    page3    = wx.Panel(notebook)

    notebook.AddPage(page1, 'page1')
    notebook.AddPage(page2, 'page2')
    notebook.AddPage(page3, 'page3')

    assert notebook.GetSelection() == 0
    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 1
    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 2
    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 0
    notebook.AdvanceSelection(False)
    assert notebook.GetSelection() == 2
    notebook.SetSelection(0)
    notebook.DisablePage(1)
    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 2
    notebook.AdvanceSelection(False)
    assert notebook.GetSelection() == 0
    notebook.EnablePage(1)

    notebook.SetSelection(1)
    notebook.HidePage(1)
    assert notebook.GetSelection() == 2
    notebook.AdvanceSelection(False)
    assert notebook.GetSelection() == 0
    notebook.ShowPage(1)
    notebook.AdvanceSelection()
    assert notebook.GetSelection() == 1


def test_event():
    nb_run_with_wx(_test_event)
def _test_event(side, ornt):
    sim      = wx.UIActionSimulator()
    frame    = wx.GetApp().GetTopWindow()
    sizer    = wx.BoxSizer(wx.VERTICAL)
    notebook = nb.Notebook(frame, style=side | ornt)
    page1    = wx.Panel(notebook)
    page2    = wx.Panel(notebook)
    page3    = wx.Panel(notebook)

    notebook.AddPage(page1, 'page1')
    notebook.AddPage(page2, 'page2')
    notebook.AddPage(page3, 'page3')

    clicked = [None]

    def onbtn(ev):
        clicked[0] = ev.index

    notebook.Bind(nb.EVT_PAGE_CHANGE, onbtn)

    sizer.Add(notebook, flag=wx.EXPAND, proportion=1)
    frame.SetSizer(sizer)
    frame.Layout()
    realYield()

    btn1, btn2, btn3 = notebook.buttons

    notebook.SetSelection(2)

    simclick(sim, btn1)
    assert clicked[0] == 0
    simclick(sim, btn2)
    assert clicked[0] == 1
    simclick(sim, btn3)
    assert clicked[0] == 2
