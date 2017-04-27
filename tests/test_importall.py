#!/usr/bin/env python
#
# test_importall.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import pkgutil


def test_importall():
    import fsleyes_widgets       as fwidgets
    import fsleyes_widgets.utils as futils

    for _, module, _ in pkgutil.iter_modules(fwidgets.__path__,
                                             'fsleyes_widgets.'):
        __import__(module)

    for _, module, _ in pkgutil.iter_modules(futils.__path__,
                                             'fsleyes_widgets.utils.'):
        __import__(module)
