#!/usr/bin/env python
#
# test_colourbarbitmap.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path   as op
import itertools as it

import numpy as np

import matplotlib        as mpl
import matplotlib.colors as colors
import matplotlib.image  as mplimg

import pytest

import fsleyes_widgets.utils.colourbarbitmap as cbarbmp

from . import compare_images


datadir = op.join(op.dirname(__file__), 'testdata', 'colourbarbitmap')


def gen_file_id(*args):
    """Generate a "safe" string for use in file names. """
    fid = '_'.join(map(str, args))
    for c in '[](){}, !@#$%&*;:=<>|/?\\"\'':
        fid = fid.replace(c, '_')

    while '__' in fid:         fid = fid.replace('__', '_')
    while fid.endswith('_'):   fid = fid[:-1]
    while fid.startswith('_'): fid = fid[1:]
    return fid


def _compare(bmp, fname):

    bmp       = bmp.transpose((1, 0, 2))
    fname     = op.join(datadir, fname)


    if op.exists(fname):
        benchmark = mplimg.imread(fname) * 255
        result = compare_images(bmp, benchmark, 0.05)
    else:
        result = [False]

    if not result[0]:
        basedir = op.join(op.dirname(__file__), '..')
        mplimg.imsave(op.join(basedir, op.basename(fname)), bmp)

    return result[0]


def test_standard_usage():

    cmaps           = ['Greys', 'Blues']
    cmapResolutions = [6, 256]
    orientations    = ['vertical', 'horizontal']
    alphas          = [0.25, 1.0]
    bgColours       = [(0, 0, 0, 0), (0, 0, 0, 1), (1, 0, 0, 1)]
    size            = (100, 25)

    testcases = it.product(cmaps,
                           cmapResolutions,
                           orientations,
                           alphas,
                           bgColours)

    for testcase in testcases:
        cmap, cmapRes, orient, alpha, bgColour = testcase

        if orient == 'vertical': height, width = size
        else:                    width, height = size

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      cmapResolution=cmapRes,
                                      alpha=alpha,
                                      orientation=orient,
                                      bgColour=bgColour)

        fname = gen_file_id('standard_usage', *testcase)
        fname = f'{fname}.png'

        assert _compare(bmp, fname)


def test_negCmap_invert():

    # cmap, negCmap, invert, orientation
    testcases = [
        ('Reds',  None,   False, 'vertical'),
        ('Reds',  None,   False, 'horizontal'),
        ('Reds',  None,   True,  'vertical'),
        ('Reds',  None,   True,  'horizontal'),
        ('Reds', 'Blues', False, 'vertical'),
        ('Reds', 'Blues', False, 'horizontal'),
        ('Reds', 'Blues', True,  'vertical'),
        ('Reds', 'Blues', True,  'horizontal')
    ]

    size = 100, 25

    for cmap, negCmap, invert, orient in testcases:

        fname = gen_file_id('negCmap_invert', cmap, negCmap, invert, orient)
        fname = f'{fname}.png'

        if orient == 'vertical': height, width = size
        else:                    width, height = size

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      negCmap=negCmap,
                                      invert=invert,
                                      orientation=orient)

        assert _compare(bmp, fname)


def test_gamma():

    gammas        = [0.5, 1.0, 2.0, 3.0]
    inverts       = [False, True]
    negCmaps      = [False, True]
    cmaps         = [('Greys', 'Greys'), ('Reds', 'Blues')]
    width, height = 100, 25

    testcases = it.product(gammas, inverts, negCmaps, cmaps)

    for gamma, invert, useNegCmap, cmap in testcases:

        cmap, negCmap = cmap

        if not useNegCmap:
            negCmap = None

        fname = gen_file_id('gamma', gamma, invert, cmap, negCmap)
        fname = f'{fname}.png'

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      invert=invert,
                                      orientation='horizontal',
                                      gamma=gamma,
                                      negCmap=negCmap)

        assert _compare(bmp, fname)


def test_logScaleRange_interp():

    # register a low-res colour map to test interpolation
    rgbs = np.array([[1, 0, 0],
                     [1, 1, 1],
                     [0, 1, 0]])
    cmap = colors.ListedColormap(rgbs, name='MYCMAP')
    mpl.colormaps.register(cmap, name='MYCMAP')


    logScales     = [None, (0, 1), (50, 100)]
    interps       = [False, True]
    reses         = [10, 100]
    cmaps         = ['hot', 'MYCMAP']
    width, height = 100, 25

    testcases = it.product(logScales, interps, reses, cmaps)

    for logScale, interp, res, cmap in testcases:

        fname = gen_file_id('logScaleRange_interp',
                            logScale, interp, res, cmap)
        fname = f'{fname}.png'

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      cmapResolution=res,
                                      interp=interp,
                                      logScaleRange=logScale,
                                      orientation='horizontal')

        assert _compare(bmp, fname)


def test_label():

    orientations = ['horizontal', 'vertical']
    labelsides   = ['top', 'bottom', 'left', 'right']
    fontsizes    = [6, 10, 16]
    textcolours  = [(0, 0, 0, 1), (1, 0, 0, 1)]

    testcases = it.product(orientations, labelsides, fontsizes, textcolours)

    for orient, side, size, colour in testcases:

        if orient[0] == 'v': width, height = 100, 300
        else:                width, height = 300, 100

        bmp = cbarbmp.colourBarBitmap('Reds',
                                      width,
                                      height,
                                      label='Label',
                                      orientation=orient,
                                      labelside=side,
                                      fontsize=size,
                                      textColour=colour)

        fname = gen_file_id('label', orient, side, size, colour)
        fname = f'{fname}.png'

        assert _compare(bmp, fname)


def test_ticks():
    orientations = ['horizontal', 'vertical']
    labelsides   = ['top', 'bottom', 'left', 'right']
    fontsizes    = [6, 10, 16]
    textcolours  = [(0, 0, 0, 1), (1, 0, 0, 1)]

    tickss      = [[0.0, 0.25, 0.75, 1.0],
                   [0.25, 0.75]]

    testcases = it.product(orientations,
                           labelsides,
                           fontsizes,
                           textcolours,
                           tickss)

    for orient, side, size, colour, ticks in testcases:

        labels = [str(t) for t in ticks]

        if orient[0] == 'v': width, height = 100, 300
        else:                width, height = 300, 100

        bmp = cbarbmp.colourBarBitmap('Reds',
                                      width,
                                      height,
                                      ticks=ticks,
                                      ticklabels=labels,
                                      orientation=orient,
                                      labelside=side,
                                      fontsize=size,
                                      textColour=colour)

        fname = gen_file_id('ticks', orient, side, size, colour, labels)
        fname = f'{fname}.png'

        assert _compare(bmp, fname)


def test_tickalign():

    orientations = ['horizontal', 'vertical']
    labelsides   = ['top', 'bottom']

    ticks      = [0.0, 0.25, 0.5, 0.75, 1.0]
    ticklabels = [str(t) for t in ticks]
    tickaligns = [
        ['left'   for t in ticks],
        ['right'  for t in ticks],
        ['center' for t in ticks],
        ['left', 'center', 'center', 'center', 'right']]

    testcases = it.product(orientations, labelsides, tickaligns)

    for orient, side, align in testcases:

        if orient[0] == 'v': width, height = 100, 300
        else:                width, height = 300, 100

        bmp = cbarbmp.colourBarBitmap('Blues',
                                      width,
                                      height,
                                      ticks=ticks,
                                      ticklabels=ticklabels,
                                      tickalign=align,
                                      orientation=orient,
                                      labelside=side,
                                      textColour=(0, 0, 0, 1))


        falign = ''.join([a[0] for a in align])
        fname  = gen_file_id('tickalign', orient, side, falign)
        fname  = f'{fname}.png'

        assert _compare(bmp, fname)


def test_label_and_ticks():

    orientations = ['horizontal', 'vertical']
    labelsides   = ['top', 'bottom']
    fontsizes    = [6, 10, 16]

    testcases = it.product(orientations,
                           labelsides,
                           fontsizes)

    ticks      = [0.2, 0.5, 0.8]
    ticklabels = [str(t) for t in ticks]
    label      = 'Label'

    for orient, side, size, in testcases:

        if orient[0] == 'v': width, height = 100, 300
        else:                width, height = 300, 100

        bmp = cbarbmp.colourBarBitmap('Reds',
                                      width,
                                      height,
                                      ticks=ticks,
                                      ticklabels=ticklabels,
                                      label=label,
                                      orientation=orient,
                                      labelside=side,
                                      fontsize=size,
                                      textColour=(0, 0, 0.2, 1))

        fname = gen_file_id('label_and_ticks', orient, side, size)
        fname = f'{fname}.png'

        assert _compare(bmp, fname)


def test_scale():
    scales       = [0.5, 1.0, 2.0, 3.0]
    orientations = ['horizontal', 'vertical']
    labelsides   = ['top', 'bottom']

    testcases = it.product(scales,
                           orientations,
                           labelsides)

    ticks      = [0.1, 0.9]
    ticklabels = [str(t) for t in ticks]
    label      = 'Label'

    for scale, orient, side in testcases:

        if orient[0] == 'v': width, height = 100, 300
        else:                width, height = 300, 100

        bmp = cbarbmp.colourBarBitmap('Reds',
                                      width,
                                      height,
                                      ticks=ticks,
                                      ticklabels=ticklabels,
                                      label=label,
                                      orientation=orient,
                                      labelside=side,
                                      scale=scale,
                                      textColour=(0, 0, 0.2, 1))

        fname = gen_file_id('scale', scale, orient, side)
        fname = f'{fname}.png'
        assert _compare(bmp, fname)


def test_negCmap_ticks():
    testcases = [
        ('Reds', 'Blues', [0, 1]),
        ('Reds', 'Blues', [0, 0.5, 1]),
        ('Reds', 'Blues', [0, 0.49, 0.51, 1]),
        ('Reds', 'Blues', [0, 0.25, 0.5, 0.75, 1])
    ]

    for cmap, negCmap, ticks in testcases:

        fname = gen_file_id(cmap, negCmap, ticks)
        fname = f'negCmap_invert_ticks_{fname}.png'

        ticklabels = ['{:0.2f}'.format(t) for t in ticks]
        tickalign = ['left'] + ['center'] * (len(ticks) - 2) + ['right']

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      800,
                                      100,
                                      fontsize=30,
                                      negCmap=negCmap,
                                      orientation='horizontal',
                                      ticks=ticks,
                                      tickalign=tickalign,
                                      ticklabels=ticklabels)
        assert _compare(bmp, fname)


def test_modAlpha():

    cmaps         = ['Reds']
    alphas        = [0.5, 1.0]
    bgColours     = [(0, 0, 0, 0), (0, 0, 0, 1), (1, 0, 0, 1)]
    dispRanges    = [(-5, 5)]
    modRanges     = [(-2.5, 2.5), (-5, 5), (-10, -5), (5, 10)]
    invModAlphas  = [False, True]
    width, height = 300, 100


    testcases = it.product(cmaps,
                           alphas,
                           bgColours,
                           dispRanges,
                           modRanges,
                           invModAlphas)

    for testcase in testcases:
        cmap, alpha, bgColour, dispRange, modRange, invModAlpha = testcase

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      alpha=alpha,
                                      bgColour=bgColour,
                                      orientation='horizontal',
                                      modAlpha=True,
                                      invModAlpha=invModAlpha,
                                      displayRange=dispRange,
                                      modRange=modRange)

        fname = gen_file_id('modAlpha', *testcase)
        fname = f'{fname}.png'

        assert _compare(bmp, fname)


def test_modAlpha_negCmap():

    cmaps         = ['Reds']
    negCmaps      = ['Blues']
    alphas        = [0.5, 1.0]
    bgColours     = [(0, 0, 0, 0), (0, 0, 0, 1), (1, 0, 0, 1)]
    dispRanges    = [(0, 5)]
    modRanges     = [(1.25, 3.75), (0, 5), (5, 10)]
    invModAlphas  = [False, True]
    width, height = 300, 100

    testcases = it.product(cmaps,
                           negCmaps,
                           alphas,
                           bgColours,
                           dispRanges,
                           modRanges,
                           invModAlphas)

    for testcase in testcases:
        cmap, negCmap, alpha, bgColour, dispRange, modRange, invModAlpha = testcase

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      negCmap=negCmap,
                                      alpha=alpha,
                                      bgColour=bgColour,
                                      orientation='horizontal',
                                      modAlpha=True,
                                      invModAlpha=invModAlpha,
                                      displayRange=dispRange,
                                      modRange=modRange)

        fname = gen_file_id('modAlpha', *testcase)
        fname = f'{fname}.png'
        assert _compare(bmp, fname)


def test_badargs():

    testcases = [
        dict(cmap='badcmap'),
        dict(orientation='badorient'),
        dict(labelside='badside'),
        dict(ticks=[0, 0.5, 1],
             ticklabels=['l', 'l', 'l'],
             tickalign=['badalign', 'badalign', 'badalign']),
    ]

    # bad colour map
    for t in testcases:
        with pytest.raises(Exception):
            cbarbmp.colourBarBitmap(t.get('cmap', 'Reds'), 50, 50, **t)
