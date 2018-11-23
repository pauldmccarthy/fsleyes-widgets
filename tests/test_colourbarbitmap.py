#!/usr/bin/env python
#
# test_colourbarbitmap.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path   as op
import itertools as it

import matplotlib.image as mplimg

import pytest

import fsleyes_widgets.utils.colourbarbitmap as cbarbmp

from . import compare_images


datadir = op.join(op.dirname(__file__), 'testdata', 'colourbarbitmap')


def _compare(bmp, fname):

    bmp       = bmp.transpose((1, 0, 2))
    fname     = op.join(datadir, fname)
    benchmark = mplimg.imread(fname) * 255

    result = compare_images(bmp, benchmark, 0.05)

    if not result[0]:
        print(result)

    return result[0]


def test_standard_usage():

    cmaps           = ['Greys', 'Blues']
    sizes           = [(100, 25)]
    cmapResolutions = [6, 256]
    orientations    = ['vertical', 'horizontal']
    alphas          = [0.25, 1.0]
    bgColours       = [(0, 0, 0, 0), (0, 0, 0, 1), (1, 0, 0, 1)]

    testcases = it.product(cmaps,
                           sizes,
                           cmapResolutions,
                           orientations,
                           alphas,
                           bgColours)

    for testcase in testcases:
        cmap, size, cmapRes, orient, alpha, bgColour = testcase

        if orient == 'vertical': height, width = size
        else:                    width, height = size

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      cmapResolution=cmapRes,
                                      alpha=alpha,
                                      orientation=orient,
                                      bgColour=bgColour)

        fname = '_'.join(map(str, [
            cmap,
            cmapRes,
            orient,
            alpha] + list(bgColour)))

        fname = 'standard_usage_{}.png'.format(fname)

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

        fname = '_'.join(map(str, [cmap, negCmap, invert, orient]))
        fname = 'negCmap_invert_{}.png'.format(fname)

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

        fname = '_'.join(map(str, [gamma, invert, cmap, negCmap]))
        fname = 'gamma_{}.png'.format(fname)

        bmp = cbarbmp.colourBarBitmap(cmap,
                                      width,
                                      height,
                                      invert=invert,
                                      orientation='horizontal',
                                      gamma=gamma,
                                      negCmap=negCmap)

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

        fname = '_'.join(map(str, [orient, side, size] + list(colour)))
        fname = 'label_{}.png'.format(fname)

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

        fname = [orient, side, size] + list(colour) + labels
        fname = '_'.join(map(str, fname))
        fname = 'ticks_{}.png'.format(fname)

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
        fname  = '_'.join([orient, side, falign])
        fname  = 'tickalign_{}.png'.format(fname)

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

        fname = '_'.join([orient, side, str(size)])
        fname = 'label_and_ticks_{}.png'.format(fname)

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

        fname = '_'.join([str(scale), orient, side])
        fname = 'scale_{}.png'.format(fname)
        assert _compare(bmp, fname)


def test_negCmap_ticks():
    testcases = [
        ('Reds', 'Blues', [0, 1]),
        ('Reds', 'Blues', [0, 0.5, 1]),
        ('Reds', 'Blues', [0, 0.49, 0.51, 1]),
        ('Reds', 'Blues', [0, 0.25, 0.5, 0.75, 1])
    ]

    for cmap, negCmap, ticks in testcases:

        fname = '_'.join(map(str, [cmap, negCmap] + ticks))
        fname = 'negCmap_invert_ticks_{}.png'.format(fname)

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
