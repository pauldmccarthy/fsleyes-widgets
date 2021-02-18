#!/usr/bin/env python
#
# __init__.py - Small utility modules for doing random things.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This package contains a collection of small utility modules for doing
random things. A few functions are also defined at the package level:

.. autosummary::
   :nosignatures:

    wxVersion
    wxFlavour
    wxPlatform
    frozen
    canHaveGui
    haveGui
    inSSHSession
    inVNCSession
    isalive


This package can be imported, and all of its functions called (with the
exception of :func:`isalive`), without ``wx`` being installed.
"""


import functools as ft
import              os
import              sys
import              warnings


WX_PYTHON  = 1
"""Constant returned by the :func:`wxFlavour` function, indicating that
wxPython 3.0.2.0 or older is being used.
"""


WX_PHOENIX = 2
"""Constant returned by the :func:`wxFlavour` function, indicating that
wxPython/Phoenix (>= 3.0.3) is being used.
"""


WX_UNKNOWN = 0
"""Constant returned by the :func:`wxPlatform` function, indicating that an
unknown wx version is being used.
"""


WX_MAC_COCOA = 1
"""Constant returned by the :func:`wxPlatform` function, indicating that an
OSX cocoa wx version is being used.
"""


WX_MAC_CARBON = 2
"""Constant returned by the :func:`wxPlatform` function, indicating that an
OSX carbon wx version is being used.
"""


WX_GTK = 3
"""Constant returned by the :func:`wxPlatform` function, indicating that a
Linux/GTK wx version is being used.
"""


def wxVersion():
    """Return a string containing the "major.minor.patch" version of wxPython
    that is installed, or ``None`` if wxPython is not installed, or its version
    cannot be determined.
    """

    try:
        import wx

        # Only consider the first three components
        # (e.g. ignore the "post2" in "4.0.7.post2")
        version = [int(v) for v in wx.__version__.split('.')[:3]]
        return '.'.join([str(v) for v in version])

    except Exception:
        return None


def wxFlavour():
    """Determines the version of wxPython being used. Returns ``WX_PYTHON``,
    ``WX_PHOENIX``, ``or ``None`` if wxPython does not appear to be installed.
    """

    try:
        import wx
    except ImportError:
        return None

    pi        = [t.lower() for t in wx.PlatformInfo]
    isPhoenix = False

    for tag in pi:
        if 'phoenix' in tag:
            isPhoenix = True
            break

    if isPhoenix: return WX_PHOENIX
    else:         return WX_PYTHON


def wxversion():
    """Deprecated - use ``wxFlavour``instead. """
    warnings.warn('wxversion is deprecated - use wxFlavour instead.',
                  category=DeprecationWarning,
                  stacklevel=1)
    return wxFlavour()


def wxPlatform():
    """Returns one of :data:`WX_UNKNOWN` :data:`WX_MAC_COCOA`,
    :data:`WX_MAC_CARBON`, or :data:`WX_GTK`, indicating the wx platform, or
    ``None`` if wxPython does not appear to be installed.
    """

    try:
        import wx
    except ImportError:
        return None

    pi = [t.lower() for t in wx.PlatformInfo]

    if   any(['cocoa'  in p for p in pi]): plat = WX_MAC_COCOA
    elif any(['carbon' in p for p in pi]): plat = WX_MAC_CARBON
    elif any(['gtk'    in p for p in pi]): plat = WX_GTK
    else:                                  plat = WX_UNKNOWN

    return plat


def frozen():
    """``True`` if we are running in a compiled/frozen application
    (e.g. pyinstaller, py2app), ``False`` otherwise.
    """
    return getattr(sys, 'frozen', False)


@ft.lru_cache()
def canHaveGui():
    """Return ``True`` if a display is available, ``False`` otherwise. """

    # We cache this because calling the
    # IsDisplayAvailable function will cause the
    # application to steal focus under OSX!
    try:
        import wx
        return wx.App.IsDisplayAvailable()
    except ImportError:
        return False


def haveGui():
    """``True`` if we are running with a GUI, ``False`` otherwise.

    This currently equates to testing whether a display is available
    (see :meth:`canHaveGui`) and whether a ``wx.App`` exists. It
    previously also tested whether an event loop was running, but this
    is not compatible with execution from IPython/Jupyter notebook, where
    the event loop is called periodically, and so is not always running.
    """
    try:
        import wx
    except ImportError:
        return False

    app = wx.GetApp()
    # TODO Previously this conditional
    #      also used app.IsMainLoopRunning()
    #      to check that the wx main loop
    #      was running. But this doesn't
    #      suit situations where a non-main
    #      event loop is running, or where
    #      the mainloop is periodically
    #      started and stopped (e.g. when
    #      the event loop is being run by
    #      IPython).
    #
    #      In c++ wx, there is the
    #      wx.App.UsesEventLoop method, but
    #      this is not presently exposed to
    #      Python code (and wouldn't help
    #      to detect the loop start/stop
    #      scenario).
    #
    #      So this constraint has been
    #      (hopefully) temporarily relaxed
    #      until I can think of a better
    #      solution.
    return (canHaveGui() and app is not None)


def inSSHSession():
    """Return ``True`` if this application appears to be running over an SSH
    session, ``False`` otherwise.
    """
    sshVars = ['SSH_CLIENT', 'SSH_TTY']
    return any(s in os.environ for s in sshVars)


def inVNCSession():
    """Returns ``True`` if this application appears to be running over a VNC (or
    similar) session, ``False`` otherwise. Currently, the following remote
    desktop environments are detected:

      - VNC
      - x2go
      - NoMachine
    """
    vncVars = ['VNCDESKTOP', 'X2GO_SESSION', 'NXSESSIONID']
    return any(v in os.environ for v in vncVars)


def isalive(widget):
    """Returns ``True`` if the given ``wx.Window`` object is "alive" (i.e.  has
    not been destroyed), ``False`` otherwise. Works in both wxPython and
    wxPython/Phoenix.

    .. warning:: Don't try to test whether a ``wx.MenuItem`` has been
                 destroyed, as it will probably result in segmentation
                 faults. Check the parent ``wx.Menu`` instead.
    """

    import wx

    wxver = wxFlavour()

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
