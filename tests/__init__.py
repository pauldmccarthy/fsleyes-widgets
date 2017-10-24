#!/usr/bin/env python
#
# __init__.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from __future__ import print_function

import time

import numpy as np

import wx

from  fsl.utils.platform import platform as fslplatform

def compare_images(img1, img2, threshold):
    """Compares two images using the euclidean distance in RGB space
    between pixels. Returns a tuple containing:

     - A boolean value indicating whether the test passed (the images
       were the same).

     - The sum of the normalised RGB distance between all pixels.
    """

    # Discard alpha values
    img1 = img1[:, :, :3]
    img2 = img2[:, :, :3]

    if img1.shape != img2.shape:
        return False, 0


    flat1   = img1.reshape(-1, 3)
    flat2   = img2.reshape(-1, 3)

    dist    = np.sqrt(np.sum((flat1 - flat2) ** 2, axis=1))
    dist    = dist.reshape(img1.shape[:2])
    dist    = dist / np.sqrt(3 * 255 * 255)

    ttlDiff = np.sum(dist)

    passed = ttlDiff <= threshold

    return passed, ttlDiff


def run_with_wx(func, *args, **kwargs):

    propagateRaise = kwargs.pop('propagateRaise', True)
    startingDelay  = kwargs.pop('startingDelay',  500)
    finishingDelay = kwargs.pop('finishingDelay', 500)
    callAfterApp   = kwargs.pop('callAfterApp',   None)

    result = [None]
    raised = [None]

    app    = wx.App()
    frame  = wx.Frame(None)

    if callAfterApp is not None:
        callAfterApp()

    def wrap():

        try:
            if func is not None:
                result[0] = func(*args, **kwargs)

        except Exception as e:
            print(e)
            raised[0] = e

        finally:
            def finish():
                frame.Destroy()
                app.ExitMainLoop()
            wx.CallLater(finishingDelay, finish)

    frame.Show()

    wx.CallLater(startingDelay, wrap)

    app.MainLoop()

    if raised[0] and propagateRaise:
        raise raised[0]

    return result[0]


def addall(parent, widgets):

    sizer = wx.BoxSizer(wx.VERTICAL)
    for w in widgets:
        sizer.Add(w, flag=wx.EXPAND, proportion=1)
    parent.Layout()
    parent.Refresh()
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

    w, h = target.GetClientSize().Get()
    x, y = target.GetScreenPosition()

    if pos is None:
        pos = [0.5, 0.5]

    x += w * pos[0]
    y += h * pos[1]

    sim.MouseMove(x, y)
    wx.Yield()
    if   stype == 0: sim.MouseClick(btn)
    elif stype == 1: sim.MouseDblClick(btn)
    else:
        sim.MouseDown(btn)
        sim.MouseUp(btn)
    realYield()


def simtext(sim, target, text, enter=True):
    target.SetFocus()
    target.SetValue(text)

    # KeyDown doesn't seem to work
    # under docker/GTK so we have
    # to hack
    if enter and fslplatform.wxPlatform == fslplatform.WX_GTK:
        parent = target.GetParent()
        if type(parent).__name__ == 'FloatSpinCtrl':
            parent._FloatSpinCtrl__onText(None)
        elif type(parent).__name__ == 'AutoTextCtrl':
            parent._AutoTextCtrl__onEnter(None)
        else:
            sim.KeyDown(wx.WXK_RETURN)
    elif enter:
        sim.KeyDown(wx.WXK_RETURN)
    realYield()


def simkey(sim, target, key, down=True, up=False):

    class FakeEv(object):
        def __init__(self, key):
            self.key = key
        def GetKeyCode(self):
            return self.key
        def Skip(self):
            pass
        def ResumePropagation(self, *a):
            pass


    parent = None
    if target is not None:
        target.SetFocus()
        parent = target.GetParent()

    if down and type(parent).__name__ == 'AutoTextCtrl':
        parent._AutoTextCtrl__onKeyDown(FakeEv(key))

    elif down and type(parent).__name__ == 'AutoCompletePopup':
        if type(target).__name__ == 'TextCtrl':
            parent._AutoCompletePopup__onKeyDown(FakeEv(key))
        elif type(target).__name__ == 'ListBox':
            parent._AutoCompletePopup__onListKeyDown(FakeEv(key))
    elif down:
        sim.KeyDown(key)

    if up:
        sim.KeyUp(key)
    realYield()
