#!/usr/bin/env python
#
# webpage.py - Convenience functions for opening a URL in a web browser.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides convenience functions for opening a URL in a web
browser.

The following functions are provided:

.. autosummary::
   :nosignatures:

   fileToUrl
   openPage
   openFile
"""

import os.path        as op
import                   webbrowser
import urllib.parse   as urlparse
import urllib.request as urlrequest


def fileToUrl(fileName):
    """Converts a file path to a URL. """
    fileName = op.abspath(fileName)
    fileName = urlrequest.pathname2url(fileName)
    return urlparse.urljoin('file://', fileName)


def openPage(url):
    """Opens the given URL in the system-default web browser."""
    webbrowser.open(url)


def openFile(fileName):
    """Opens the given file in the system-default web browser."""
    openPage(fileToUrl(fileName))
