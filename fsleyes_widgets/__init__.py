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


This file is used to store the current ``fsleyes-widgets`` version, and also
contains a handful of utility functions:

.. autosummary::
   :nosignature::

   wxversion
   isalive
"""


__version__ = '0.1.1.dev'



WX_PYTHON  = 1
"""Constant returned by the ``wxversion`` function, indicating that wxPython
3.0.2.0 or older is being used.
"""


WX_PHOENIX = 2
"""Constant returned by the ``wxversion`` function, indicating that
wxPython/Phoenix (>= 3.0.3) is being used.
"""


def wxversion():
    """Determines the version of wxPython being used. Returns either ``WX_PYTHON``
    or ``WX_PHOENIX``.
    """
    import wx

    pi        = [t.lower() for t in wx.PlatformInfo]
    isPhoenix = False

    for tag in pi:
        if 'phoenix' in tag:
            isPhoenix = True
            break

    if isPhoenix: return WX_PHOENIX
    else:         return WX_PYTHON


def isalive(widget):
    """Returns ``True`` if the given ``wx.Window`` object is "alive" (i.e.  has
    not been destroyed), ``False`` otherwise. Works in both wxPython and
    wxPython/Phoenix.

    .. warning:: Don't try to test whether a ``wx.MenuItem`` has been
                 destroyed, as it will probably result in segmentation
                 faults. Check the parent ``wx.Menu`` instead.
    """

    import wx

    wxver = wxversion()

    if wxver == WX_PHOENIX:
        excType = RuntimeError
    elif wxver == WX_PYTHON:
        excType = wx.PyDeadObjectError

    try:
        widget.GetParent()
        return True

    except excType:
        return False
