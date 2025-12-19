#!/usr/bin/env python
#
# test_elistbox.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import random

import wx

from . import run_with_wx, simclick, simtext, simkey, realYield

from fsleyes_widgets import isalive
import fsleyes_widgets.elistbox as elistbox


def test_create():
    run_with_wx(_test_create)
def _test_create():
    frame = wx.GetApp().GetTopWindow()

    items    = random.sample(range(100), 5)
    labels   = [str(i)                 for i in items]
    tooltips = ['tip: {}'.format(i)    for i in items]
    listbox  = elistbox.EditableListBox(
        frame,
        labels=labels,
        clientData=items,
        tooltips=tooltips)

    assert listbox.VisibleItemCount() == 5
    assert listbox.GetCount()         == 5

    assert listbox.GetSelection() == wx.NOT_FOUND
    listbox.SetSelection(3)
    assert listbox.GetSelection() == 3

    for idx, i in enumerate(items):
        assert listbox.IndexOf(i) == idx

    assert list(listbox.GetLabels()) == list(labels)
    assert list(listbox.GetData())   == list(items)
    for i in range(len(items)):
        assert listbox.GetItemTooltip(i) == tooltips[i]
        assert listbox.GetItemLabel(  i) == labels[i]
        assert listbox.GetItemData(   i) == items[i]


def test_add_remove():
    run_with_wx(_test_add_remove)
def _test_add_remove():
    frame   = wx.GetApp().GetTopWindow()
    items   = [str(random.randint(1, 100)) for i in range(5)]
    listbox = elistbox.EditableListBox(frame, items)

    # delete
    for i in range(5):
        ridx = random.randint(0, len(items) - 1)
        items.pop(ridx)
        listbox.Delete(ridx)
        assert list(listbox.GetLabels()) == items

    # append
    for i in range(5):
        item = str(random.randint(0, 100))
        items.append(item)
        listbox.Append(item)
        assert list(listbox.GetLabels()) == items

    # insert
    for i in range(5):
        item = str(random.randint(0, 100))
        idx  = random.randint(0, len(items) - 1)
        items.insert(idx, item)
        listbox.Insert(item, idx)
        assert list(listbox.GetLabels()) == items


def test_hidden():
    run_with_wx(_test_hidden)
def _test_hidden():

    class FakeEv(object):
        def __init__(self, key):
            self.key = key
        def GetKeyCode(self):
            return self.key
        def HasModifiers(self):
            return False
        def Skip(self):
            pass

    frame   = wx.GetApp().GetTopWindow()
    items   = list(range(10))
    labels  = [str(i) for i in items]
    listbox = elistbox.EditableListBox(
        frame,
        labels=labels,
        clientData=items)

    def hide(label, data):
        return data % 2 == 0

    listbox.SetSelection(0)
    listbox.MoveItem(5)
    assert listbox.GetSelection() == 5
    assert listbox.GetItemData() == [1, 2, 3, 4, 5, 0, 6, 7, 8, 9]

    listbox.MoveItem(-5)
    assert listbox.GetSelection() == 0
    assert listbox.GetItemData() == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    listbox.ApplyFilter(hide)
    assert listbox.GetVisibleItemData() == [0, 2, 4, 6, 8]
    assert listbox.GetSelection() == 0

    listbox._onKeyboard(FakeEv(wx.WXK_DOWN))
    assert listbox.GetSelection() == 2
    listbox._onKeyboard(FakeEv(wx.WXK_UP))
    assert listbox.GetSelection() == 0

    listbox.MoveItem(1)
    assert listbox.GetSelection() == 2
    assert listbox.GetVisibleItemData() == [2, 0, 4, 6, 8]
    assert listbox.GetItemData() == [1, 2, 0, 3, 4, 5, 6, 7, 8, 9]
