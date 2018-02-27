#!/usr/bin/env python
#
# __init__.py - Small utility modules for doing random things.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This package contains a collection of small utility modules for doing random
things. A few functions are also defined at the package level:

.. autosummary::
   :nosignatures:

    wxversion
    isalive
"""



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
        excTypes = (RuntimeError,)
    else:
        excTypes = (wx.PyDeadObjectError,)

    try:
        if hasattr(widget, 'IsBeingDeleted'):
            return not widget.IsBeingDeleted()
        else:
            widget.GetParent()
            return True

    except excTypes:
        return False
