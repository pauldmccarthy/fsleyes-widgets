#!/usr/bin/env python
#
# test_layout.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import fsleyes_widgets.utils.layout as fsllayout


def test_padBitmap():

    bmp       = np.zeros((10, 10, 4))
    expectedh = np.ones( (10, 20, 4))
    expectedv = np.ones( (20, 10, 4))

    expectedh[ :,   5:15, :] = 0
    expectedv[5:15,  :,   :] = 0

    resulth = fsllayout.padBitmap(bmp, 20, 20, True,  (1, 1, 1, 1))
    resultv = fsllayout.padBitmap(bmp, 20, 20, False, (1, 1, 1, 1))

    assert np.all(resulth == expectedh)
    assert np.all(resultv == expectedv)


def test_buildCanvasBox_withLabels():

    labelbmps = {
        'left'   : np.zeros((5, 5, 4)),
        'right'  : np.zeros((5, 5, 4)),
        'top'    : np.zeros((5, 5, 4)),
        'bottom' : np.zeros((5, 5, 4))
    }

    canvasbmp               = np.ones((20, 20, 4))
    expected                = np.zeros((30, 30, 4))
    expected[5:25, 5:25, :] = canvasbmp

    box = fsllayout.buildCanvasBox(canvasbmp, labelbmps, True, 0)
    bmp = fsllayout.layoutToBitmap(box)

    assert np.all(bmp == expected)


def test_buildCanvasBox_noLabels():

    canvasbmp = np.ones((5, 5, 4))

    box = fsllayout.buildCanvasBox(canvasbmp, None, False, 0)

    bmp = fsllayout.layoutToBitmap(box)

    assert np.all(bmp == canvasbmp)


def test_buildOrthoLayout_vertical():

    canvasbmps = [
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4))]

    canvasbmps[0][:] = 1
    canvasbmps[1][:] = 2
    canvasbmps[2][:] = 3

    expected = np.vstack(canvasbmps)

    result = fsllayout.buildOrthoLayout(canvasbmps, None, 'vertical', False, 0)
    result = fsllayout.layoutToBitmap(result)

    assert np.all(result == expected)


def test_buildOrthoLayout_horizontal():

    canvasbmps = [
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4))]

    canvasbmps[0][:] = 1
    canvasbmps[1][:] = 2
    canvasbmps[2][:] = 3

    expected = np.hstack(canvasbmps)

    result = fsllayout.buildOrthoLayout(
        canvasbmps, None, 'horizontal', False, 0)
    result = fsllayout.layoutToBitmap(result)

    assert np.all(result == expected)


def test_buildOrthoLayout_grid():

    canvasbmps = [
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4)),
        np.zeros((10, 10, 4))]

    canvasbmps[0][:] = 1
    canvasbmps[1][:] = 2
    canvasbmps[2][:] = 3

    expected = np.zeros((20, 20, 4))
    expected[:10,  :10,  :] = canvasbmps[0]
    expected[:10,   10:, :] = canvasbmps[1]
    expected[ 10:, :10,  :] = canvasbmps[2]

    result = fsllayout.buildOrthoLayout(
        canvasbmps, None, 'grid', False, 0)
    result = fsllayout.layoutToBitmap(result)

    assert np.all(result == expected)


def test_calcSizes():

    # calcSizes  is just a wrapper around the
    # calcGrid/Horizontal/VerticalSizes functions

    # For grid layout, canvas edges have
    # to line up - see calcGridSizes docs
    gaxes = [(0, 2), (1, 2), (0, 1)]
    axes  = [(0, 1), (0, 2), (1, 2)]

    # bounds, width, height
    testcases = [
        ([1.0, 1.0, 1.0], 200, 200),
        ([1.0, 1.0, 1.0], 100, 200),
        ([1.0, 1.0, 1.0], 200, 100),
        ([1.0, 2.0, 3.0], 200, 200)]

    for testcase in testcases:

        bounds, width, height = testcase

        hexp = fsllayout.calcHorizontalSizes(    axes,  bounds, width, height)
        vexp = fsllayout.calcVerticalSizes(      axes,  bounds, width, height)
        gexp = fsllayout.calcGridSizes(          gaxes, bounds, width, height)
        hres = fsllayout.calcSizes('horizontal', axes,  bounds, width, height)
        vres = fsllayout.calcSizes('vertical',   axes,  bounds, width, height)
        gres = fsllayout.calcSizes('grid',       gaxes, bounds, width, height)

        assert np.all(np.isclose(hexp, hres))
        assert np.all(np.isclose(vexp, vres))
        assert np.all(np.isclose(gexp, gres))


def test_calcGridSizes():

    axes = [(0, 2), (1, 2), (0, 1)]

    # bounds, width, height, expected
    testcases = [
        ([1.0, 1.0, 1.0], 200, 200, [(100, 100),
                                     (100, 100),
                                     (100, 100)]),

        ([1.0, 1.0, 1.0], 100, 200, [(50, 100),
                                     (50, 100),
                                     (50, 100)]),

        ([1.0, 1.0, 1.0], 200, 100, [(100, 50),
                                     (100, 50),
                                     (100, 50)]),

        ([1.0, 2.0, 3.0], 200, 200, [(200 * 1 / 3.0, 200 * 3 / 5.0),
                                     (200 * 2 / 3.0, 200 * 3 / 5.0),
                                     (200 * 1 / 3.0, 200 * 2 / 5.0)]),
    ]

    for testcase in testcases:
        bounds, width, height = testcase[:3]
        expected              = testcase[ 3]

        result = fsllayout.calcGridSizes(axes, bounds, width, height)

        assert np.all(np.isclose(result, expected))

        # Passing less than three canvases should be
        # equivalent to calcHorizontalSizes
        for ncanvases in [1, 2]:
            naxes = axes[:ncanvases]

            gres = fsllayout.calcGridSizes(      naxes, bounds, width, height)
            hres = fsllayout.calcHorizontalSizes(naxes, bounds, width, height)

            assert np.all(np.isclose(gres, hres))


def test_calcHorizontalSizes():
    axes = [(0, 1), (0, 2), (1, 2)]

    # bonds, width, height, expected
    testcases = [
        ([1.0, 1.0, 1.0], 300, 100, [(100, 100),
                                     (100, 100),
                                     (100, 100)]),

        ([1.0, 1.0, 1.0], 100, 100, [(100 / 3.0, 100),
                                     (100 / 3.0, 100),
                                     (100 / 3.0, 100)]),

        ([1.0, 1.0, 1.0], 100, 200, [(100 / 3.0, 200),
                                     (100 / 3.0, 200),
                                     (100 / 3.0, 200)]),

        ([1.0, 2.0, 3.0], 100, 100, [(100 * 1 / 4.0, 100 * 2 / 3.0),
                                     (100 * 1 / 4.0, 100),
                                     (100 * 2 / 4.0, 100)])
    ]

    for testcase in testcases:
        bounds, width, height = testcase[:3]
        expected              = testcase[ 3]

        result = fsllayout.calcHorizontalSizes(axes, bounds, width, height)

        assert np.all(np.isclose(result, expected))


def test_calcVerticalSizes():

    axes = [(0, 1), (0, 2), (1, 2)]

    # bonds, width, height, expected
    testcases = [
        ([1.0, 1.0, 1.0], 100, 300, [(100, 100),
                                     (100, 100),
                                     (100, 100)]),

        ([1.0, 1.0, 1.0], 100, 100, [(100, 100 / 3.0),
                                     (100, 100 / 3.0),
                                     (100, 100 / 3.0)]),


        ([1.0, 1.0, 1.0], 200, 100, [(200, 100 / 3.0),
                                     (200, 100 / 3.0),
                                     (200, 100 / 3.0)]),

        ([1.0, 2.0, 3.0], 100, 100, [(50,  100 * 2.0 / 8),
                                     (50,  100 * 3.0 / 8),
                                     (100, 100 * 3.0 / 8)]),
    ]

    for testcase in testcases:
        bounds, width, height = testcase[:3]
        expected              = testcase[ 3]

        result = fsllayout.calcVerticalSizes(axes, bounds, width, height)

        assert np.all(np.isclose(result, expected))



def test_calcPixWidth():

    # (wldWidth, wldHeight, pixHeight, expected)
    testcases = [
        (1.0, 1.0, 100, 100),
        (1.0, 2.0, 100,  50),
        (2.0, 1.0,  50, 100)]

    for wldWidth, wldHeight, pixHeight, exp in testcases:
        assert fsllayout.calcPixWidth(wldWidth, wldHeight, pixHeight) == exp


def test_calcPixHeight():

    # (wldWidth, wldHeight, pixWidth, expected)
    testcases = [
        (1.0, 1.0, 100, 100),
        (1.0, 2.0,  50, 100),
        (2.0, 1.0, 100,  50)]

    for wldWidth, wldHeight, pixHeight, exp in testcases:
        assert fsllayout.calcPixHeight(wldWidth, wldHeight, pixHeight) == exp
