#!/usr/bin/env python
#
# test_webpage.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import sys

import six


# python 3
if six.PY3:
    import unittest.mock as mock
# python 2
elif six.PY2:
    import mock

import fsleyes_widgets.utils.webpage as webpage

def test_fileToUrl():

    # fname, expected
    testcases = [
        ('/home/blah/file.html', 'file:///home/blah/file.html'),
        ('file.html',            'file:///file.html'),
        ('./file.html',          'file:///file.html'),
        ('../file.html',         'file:///../file.html'),
    ]

    # urljoin has changed in python3.5 to make paths absolute
    if six.PY3 and sys.version_info.minor >= 5:
        testcases[-1] = ('../file.html', 'file:///file.html')

    for fname, expected in testcases:
        assert webpage.fileToUrl(fname) == expected


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
