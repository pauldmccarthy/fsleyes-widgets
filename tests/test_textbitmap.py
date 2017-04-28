#!/usr/bin/env python
#
# test_textbitmap.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path   as op
import itertools as it

import matplotlib.image as mplimg

from . import compare_images

import fsleyes_widgets.utils.textbitmap as textbmp

datadir = op.join(op.dirname(__file__), 'testdata', 'textbitmap')


def test_textbitmap():

    texts     = ['R', 'Label']
    fontsizes = [6, 10, 16]
    bgColours = [(0, 0, 0, 0), (0, 0, 0, 1), (1, 0, 0, 1)]
    fgColours = [(0, 0, 0, 1), (1, 0, 0, 1), (1, 1, 1, 1)]
    alphas    = [0.5, 1.0]

    testcases = it.product(texts, fontsizes, bgColours, fgColours, alphas)

    for text, size, bg, fg, alpha in testcases:

        if bg == fg:
            continue

        bmp = textbmp.textBitmap(text, 75, 50, size, fg, bg, alpha)

        fname = [text, size] + list(bg) + list(fg) + [alpha]
        fname = '{}.png'.format('_'.join(map(str, fname)))
        fname = op.join(datadir, fname)

        benchmark = mplimg.imread(fname) * 255
        assert compare_images(bmp, benchmark, 1)[0]
