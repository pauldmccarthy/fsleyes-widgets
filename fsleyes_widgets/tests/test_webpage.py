#!/usr/bin/env python
#
# test_webpage.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os
import os.path as op

import unittest.mock as mock

import fsleyes_widgets.utils.webpage as webpage


def test_fileToUrl():

    # fname, expected
    testcases = [
        '/home/blah/file.html'
        'file.html',
        './file.html',
        '../file.html',
    ]

    for fname in testcases:
        expect = op.abspath(fname)
        expect = f'file://{expect}'
        assert webpage.fileToUrl(fname) == expect


def test_openPage():

    opened = [None]

    def mockOpen(page):
        opened[0] = page

    tomock = 'fsleyes_widgets.utils.webpage.webbrowser.open'
    toopen = 'fakeUrl'
    with mock.patch(tomock, side_effect=mockOpen):

        webpage.openPage(toopen)

    assert opened[0] == toopen


def test_openFile():

    opened = [None]

    def mockOpen(page):
        opened[0] = page

    tomock   = 'fsleyes_widgets.utils.webpage.webbrowser.open'
    toopen   = '/path/to/file.html'
    expected = webpage.fileToUrl(toopen)

    with mock.patch(tomock, side_effect=mockOpen):
        webpage.openFile(toopen)

    assert opened[0] == expected
