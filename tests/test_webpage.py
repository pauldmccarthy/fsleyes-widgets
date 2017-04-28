#!/usr/bin/env python
#
# test_webpage.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


# python 3
try:
    import unittest.mock as mock
# python 2
except:
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
