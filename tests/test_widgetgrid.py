#!/usr/bin/env python

import wx

import numpy as np

from . import run_with_wx, simmouse, realYield

import fsleyes_widgets.widgetgrid as widgetgrid


def test_create():
    run_with_wx(_test_create)
def _test_create():
    frame = wx.GetApp().GetTopWindow()
    grid = widgetgrid.WidgetGrid(frame)
    grid.SetGridSize(10, 10)
    grid.ShowRowLabels()
    grid.ShowColLabels()

    for i in range(10):
        grid.SetRowLabel(i, 'row {}'.format(i + 1))
        grid.SetColLabel(i, 'col {}'.format(i + 1))

    for i in range(10):
        for j in range(10):
            grid.SetText(i, j, 'cell [{}, {}]'.format(i + 1, j + 1))

    grid.Refresh()

    for i in range(10):
        assert grid.GetRowLabel(i) == 'row {}'.format(i + 1)
    for i in range(10):
        assert grid.GetColLabel(i) == 'col {}'.format(i + 1)

    for i in range(10):
        for j in range(10):
            exp = 'cell [{}, {}]'.format(i + 1, j + 1)
            assert grid.GetWidget(i, j).GetLabel() == exp



def test_reorder():
    run_with_wx(_test_reorder)
def _test_reorder():
    frame = wx.GetApp().GetTopWindow()
    grid = widgetgrid.WidgetGrid(frame)

    grid.SetGridSize(1, 10)

    labels = ['col {}' .format(i) for i in range(10)]
    cells  = ['cell {}'.format(i) for i in range(10)]

    for i in range(10): grid.SetColLabel(i, labels[i])
    for i in range(10): grid.SetText(0,  i, cells[i])

    grid.Refresh()

    for i in range(5):
        neworder = np.array(range(10))
        np.random.shuffle(neworder)
        grid.ReorderColumns(neworder)
        grid.Refresh()

        for i in range(10):

            assert grid.GetColLabel( i)            == labels[neworder[i]]
            assert grid.GetWidget(0, i).GetLabel() == cells[ neworder[i]]

        labels = [labels[i] for i in neworder]
        cells  = [cells[ i] for i in neworder]


def test_reorder_events():
    run_with_wx(_test_reorder_events)
def _test_reorder_events():
    frame = wx.GetApp().GetTopWindow()
    frame.SetSize((800, 600))
    sim   = wx.UIActionSimulator()
    grid  = widgetgrid.WidgetGrid(frame, style=widgetgrid.WG_DRAGGABLE_COLUMNS)
    sizer = wx.BoxSizer(wx.VERTICAL)
    frame.SetSizer(sizer)
    sizer.Add(grid, flag=wx.EXPAND, proportion=1)

    grid.ShowColLabels()
    grid.SetGridSize(1, 5)

    # (clicked column, drop column, drop pos, expected order)
    tests = [
        (0, 0, 0.25, [0, 1, 2, 3, 4]),
        (0, 0, 0.75, [0, 1, 2, 3, 4]),
        (1, 1, 0.25, [0, 1, 2, 3, 4]),
        (1, 1, 0.75, [0, 1, 2, 3, 4]),
        (0, 1, 0.25, [0, 1, 2, 3, 4]),
        (1, 2, 0.25, [0, 1, 2, 3, 4]),
        (1, 0, 0.75, [0, 1, 2, 3, 4]),
        (2, 1, 0.75, [0, 1, 2, 3, 4]),
        (0, 1, 0.75, [1, 0, 2, 3, 4]),
        (1, 2, 0.75, [0, 2, 1, 3, 4]),
        (1, 0, 0.25, [1, 0, 2, 3, 4]),
        (2, 1, 0.25, [0, 2, 1, 3, 4]),
        (0, 2, 0.25, [1, 0, 2, 3, 4]),
        (0, 2, 0.75, [1, 2, 0, 3, 4]),
        (2, 0, 0.25, [2, 0, 1, 3, 4]),
        (2, 0, 0.75, [0, 2, 1, 3, 4]),
        (1, 3, 0.25, [0, 2, 1, 3, 4]),
        (1, 3, 0.75, [0, 2, 3, 1, 4]),
        (3, 1, 0.25, [0, 3, 1, 2, 4]),
        (3, 1, 0.75, [0, 1, 3, 2, 4]),
    ]

    for clickcol, dropcol, droppos, exporder in tests:

        grid.ClearGrid()
        grid.Refresh()
        grid.SetGridSize(1, 5)

        labels = ['col {}' .format(i) for i in range(5)]
        cells  = ['cell {}'.format(i) for i in range(5)]

        for i in range(5): grid.SetColLabel(i, labels[i])
        for i in range(5): grid.SetText(0,  i, cells[i])

        grid.Refresh()
        frame.Layout()

        cwidget = grid.colLabels[clickcol].GetParent()
        dwidget = grid.colLabels[dropcol].GetParent()

        realYield()
        simmouse(sim, cwidget, 'left', 'down', [0.5,     0.5])
        realYield()
        simmouse(sim, dwidget, 'left', 'up',   [droppos, 0.5])
        realYield()

        explabels = [labels[i] for i in exporder]
        gotlabels = [str(grid.GetColLabel(i)) for i in range(5)]

        assert explabels == gotlabels
