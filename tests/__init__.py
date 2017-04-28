#!/usr/bin/env python
#
# __init__.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from __future__ import print_function

import numpy as np

import wx

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


def simclick(sim, target, btn=wx.MOUSE_BTN_LEFT, double=False):

    x, y = target.GetScreenPosition()
    sim.MouseMove(x + 10, y + 10)
    wx.Yield()
    if double: sim.MouseDblClick(btn)
    else:      sim.MouseClick(btn)
    wx.Yield()
