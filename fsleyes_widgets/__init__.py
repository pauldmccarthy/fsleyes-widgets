#!/usr/bin/env python
#
# __init__.py - fsleyes-widgets
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The ``fsleyes_widgets`` package contains various custom :mod:`wx` widgets
and utilities used by FSLeyes.


Some of the controls in ``fsleyes_widgets`` are duplicates of controls which
are already available in ``wx`` or ``wx.lib.agw``. In these instances, I wrote
my own implementations to work around annoying, quirky, and/or downright buggy
behaviour in the existing controls.


This file is used to store the current ``fsleyes-widgets`` version.
"""


__version__ = '0.7.0'


from fsleyes_widgets.utils import (WX_PYTHON,  # noqa
                                   WX_PHOENIX,
                                   wxversion,
                                   isalive)
