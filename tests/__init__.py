#!/usr/bin/env python
#
# __init__.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from __future__ import print_function

import gc
import time
import traceback

import numpy as np

import wx


GTK = any(['gtk' in p.lower() for p in wx.PlatformInfo])


def compare_images(arr1, arr2, threshold):
    """Compares two images using the normalised difference of arr1 with respect
    to arr2. Returns a tuple containing:

     - A boolean value indicating whether the test passed (the difference was
       less than or equal to the threshold).

     - The normalised difference between the two..
    """
    # Discard alpha values
    arr1 = arr1[:, :, :3]
    arr2 = arr2[:, :, :3]

    if arr1.shape != arr2.shape:
        return False, 0

    finite1 = np.isfinite(arr1)
    finite2 = np.isfinite(arr2)

    if not np.all(finite1 == finite2):
        return 1

    a2zero = arr2 == 0
    nzarr1 = arr1[finite1 & ~a2zero]
    nzarr2 = arr2[finite1 & ~a2zero]
    zarr1  = arr1[finite1 &  a2zero]
    zarr2  = arr2[finite1 &  a2zero]

    if nzarr2.size > 0: zdenom = abs(nzarr2.mean())
    else:               zdenom = 1

    normdiff = np.zeros(arr1.shape)
    normdiff[finite1 & ~a2zero] = np.abs((nzarr2 - nzarr1) / nzarr2)
    normdiff[finite1 &  a2zero] = np.abs((zarr2  - zarr1)  / zdenom)

    if normdiff.size > 0:
        result = normdiff.mean()
        return result <= threshold, result
    else:
        return True, 0


def run_with_wx(func, *args, **kwargs):

    gc.collect()

    propagateRaise = kwargs.pop('propagateRaise', True)
    startingDelay  = kwargs.pop('startingDelay',  500)
    finishingDelay = kwargs.pop('finishingDelay', 500)
    callAfterApp   = kwargs.pop('callAfterApp',   None)

    result = [None]
    raised = [None]

    app    = [wx.App()]
    frame  = [wx.Frame(None)]

    if callAfterApp is not None:
        callAfterApp()

    def wrap():

        try:
            if func is not None:
                result[0] = func(*args, **kwargs)

        except Exception as e:
            traceback.print_exc()
            raised[0] = e

        finally:
            def finish():
                frame[0].Destroy()
                app[0].ExitMainLoop()
            wx.CallLater(finishingDelay, finish)

    frame[0].Show()

    wx.CallLater(startingDelay, wrap)

    app[0].MainLoop()

    time.sleep(1)

    if raised[0] and propagateRaise:
        raise raised[0]

    del app[0]
    del frame[0]

    return result[0]


def addall(parent, widgets):

    sizer = wx.BoxSizer(wx.VERTICAL)
    for w in widgets:
        sizer.Add(w, flag=wx.EXPAND, proportion=1)
    parent.SetSizer(sizer)
    parent.Layout()
    parent.Refresh()
    parent.Update()
    realYield()


# Under GTK, a single call to
# yield just doesn't cut it
def realYield(centis=10):
    for i in range(int(centis)):
        wx.YieldIfNeeded()
        time.sleep(0.01)


# stype:
#   0 for single click
#   1 for double click
#   2 for separatemouse down/up events
def simclick(sim, target, btn=wx.MOUSE_BTN_LEFT, pos=None, stype=0):

    class FakeEv(object):
        def __init__(self, evo):
            self.evo = evo
        def GetEventObject(self):
            return self.evo

    parent = target.GetParent()
    if GTK:

        if type(target).__name__ == 'StaticTextTag' and \
           type(parent).__name__ == 'TextTagPanel':
            parent._TextTagPanel__onTagLeftDown(FakeEv(target))
            realYield()
            return

        if type(target).__name__ == 'StaticText' and \
           type(parent).__name__ == 'TogglePanel':
            parent.Toggle(FakeEv(target))
            realYield()
            return

    w, h = target.GetClientSize().Get()
    x, y = target.GetScreenPosition()

    if pos is None:
        pos = [0.5, 0.5]

    x += w * pos[0]
    y += h * pos[1]

    sim.MouseMove(x, y)
    realYield()
    if   stype == 0: sim.MouseClick(btn)
    elif stype == 1: sim.MouseDblClick(btn)
    else:
        sim.MouseDown(btn)
        sim.MouseUp(btn)
    realYield()


def simtext(sim, target, text, enter=True):

    target.SetFocus()
    parent = target.GetParent()

    # The EVT_TEXT_ENTER event
    # does not seem to occur
    # under docker/GTK so we
    # have to hack. EVT_TEXT
    # does work though.
    if GTK and type(parent).__name__ == 'FloatSpinCtrl':
        if enter:
            target.ChangeValue(text)
            parent._FloatSpinCtrl__onText(None)
        else:
            target.SetValue(text)

    elif GTK and type(parent).__name__ == 'AutoTextCtrl':
        if enter:
            target.ChangeValue(text)
            parent._AutoTextCtrl__onEnter(None)
        else:
            target.SetValue(text)
    else:
        target.SetValue(text)

        if enter:
            sim.KeyDown(wx.WXK_RETURN)

    realYield()


def simkey(sim, target, key, down=True, up=False):

    class FakeEv(object):
        def __init__(self, obj, key):
            self.obj = obj
            self.key = key
        def GetKeyCode(self):
            return self.key
        def Skip(self):
            pass
        def GetEventObject(self):
            return self.obj
        def ResumePropagation(self, *a):
            pass


    parent = None
    if target is not None:
        target.SetFocus()
        parent = target.GetParent()

    if GTK:

        if down and type(parent).__name__ == 'AutoTextCtrl':
            parent._AutoTextCtrl__onKeyDown(FakeEv(target, key))

        elif down and type(parent).__name__ == 'FloatSpinCtrl':
            parent._FloatSpinCtrl__onKeyDown(FakeEv(target, key))
        elif down and type(parent).__name__ == 'TextTagPanel':
            if type(target).__name__ == 'AutoTextCtrl':
                parent._TextTagPanel__onNewTagKeyDown(FakeEv(target, key))
            elif type(target).__name__ == 'StaticTextTag':
                parent._TextTagPanel__onTagKeyDown(FakeEv(target, key))

        elif down and type(parent).__name__ == 'AutoCompletePopup':
            if type(target).__name__ == 'TextCtrl':
                parent._AutoCompletePopup__onKeyDown(FakeEv(target, key))
            elif type(target).__name__ == 'ListBox':
                parent._AutoCompletePopup__onListKeyDown(FakeEv(target, key))
        elif down:
            sim.KeyDown(key)

    elif down:
        sim.KeyDown(key)

    if up:
        sim.KeyUp(key)
    realYield()


def simfocus(from_, to):

    class FakeEv(object):
        def __init__(self):
            pass
        def Skip(self):
            pass

    if GTK:
        if type(from_).__name__ == 'FloatSpinCtrl':
            from_._FloatSpinCtrl__onKillFocus(FakeEv())

    to.SetFocus()
    realYield()
