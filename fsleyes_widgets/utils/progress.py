#!/usr/bin/env python
#
# progress.py - The Bounce class
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides some classes and functions which use the
``wx.ProgressDialog`` to display the progress of some task.
"""


import threading

import wx

from fsleyes_widgets import isalive


class Bounce(wx.ProgressDialog):
    """Display a 'bouncing' progress bar.

    The ``Bounce`` class is a ``wx.ProgressDialog`` for use with tasks with an
    unknown duration. The progress bar 'bounces' back and forth until the
    dialog is destroyed or cancelled.

    A ``Bounce`` dialog can either be controlled manually via the
    :meth:`DoBounce` method, , or allowed to run automatically via the
    :meth:`StartBounce`. Automatic bouncing can be stopped via
    :meth:`StopBounce`.
    """


    def __init__(self, *args, **kwargs):
        """Create a ``Bounce`` dialog.

        :arg delay:  Must be passed as a keyword argument. Delay in
                     milliseconds between progress bar updates. Defaults to 200
                     milliseconds.

        :arg values: Must be passed as a keyword argument. A sequence of values
                     from 1 to 99 specifying the locations of the progress bar
                     on each update. Deafults to ``[1, 25, 50, 75, 99]``.
        """

        self.__delay     = kwargs.pop('delay',  200)
        self.__values    = kwargs.pop('values', [1, 25, 50, 75, 99])
        self.__direction = 1
        self.__index     = 0
        self.__bouncing  = False

        wx.ProgressDialog.__init__(self, *args, **kwargs)


    @classmethod
    def runWithBounce(cls, task, *args, **kwargs):
        """Runs the given ``task`` in a separate thread, and creates a
        ``Bounce`` dialog which is displayed while the task is running.

        :arg dlg:      Must be passed as a keyword argument. A ``Bounce``
                       dialog to use. If not provided, one is created. If
                       provided, the caller is responsible for destroying
                       it.

        :arg polltime: Must be passed as a keyword argument. Amount of time
                       in seconds to wait while  periodically checking the
                       task state.

        All other arguments are passed through to :meth:`Bounce.__init__`,
        unless a ``dlg`` is provided.

        :returns: ``True`` if the task ended, ``False`` if the progress dialog
                   was cancelled.
        """

        polltime = kwargs.pop('polltime', 0.05)
        dlg      = kwargs.pop('dlg',      None)
        owndlg   = dlg is None

        if dlg is None:
            dlg = Bounce(*args, **kwargs)

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

        dlg.Show()
        dlg.StartBounce()

        finished = False

        while True:
            wx.Yield()
            thread.join(polltime)
            wx.Yield()

            if not thread.is_alive():
                finished = True
                break
            if dlg.WasCancelled():
                break

        if owndlg:
            dlg.Destroy()

        return finished


    def Close(self):
        """Close the ``Bounce`` dialog. """
        self.__bouncing = False
        wx.ProgressDialog.Close(self)


    def EndModal(self, code=wx.ID_OK):
        """Close the ``Bounce`` dialog. """
        self.__bouncing = False
        wx.ProgressDialog.EndModal(self, code)


    def Destroy(self):
        """Destroy the ``Bounce`` dialog. """
        self.__bouncing = False
        wx.ProgressDialog.Destroy(self)


    def StartBounce(self):
        """Start automatic bouncing. """
        self.__bouncing = True
        self.__autoBounce()


    def StopBounce(self):
        """Stop automatic bouncing. """
        self.__bouncing = False


    def Update(self, value, message=None):
        """Overrides ``wx.ProgressDialog.Update``.

        The ``Update`` method in wxPython 3.0.2.0 will raise an error if a
        ``message`` of ``None`` gets passed in. This implementation accepts a
        ``message`` of ``None``.
        """

        if message is None: return super(Bounce, self).Update(value)
        else:               return super(Bounce, self).Update(value, message)


    def UpdateMessage(self, message):
        """Updates the message displayed on the dialog. """
        self.Update(self.__values[self.__index], message)


    def DoBounce(self, message=None):
        """Perform a single bounce update to the progress bar.

        :arg message: New message to show.

        :returns:     ``False`` if the dialog gets cancelled, ``True``
                      otherwise.
        """

        newval = self.__values[self.__index]

        if self.WasCancelled() or \
           not self.Update(newval, message):
            return False

        self.__index += self.__direction

        if self.__index >= len(self.__values):
            self.__index     = len(self.__values) - 2
            self.__direction = -self.__direction
        elif self.__index == 0:
            self.__index     = 0
            self.__direction = -self.__direction

        return True


    def __autoBounce(self):
        """Automatic bouncing.

        If a call to :meth:`StopBounce` has been made, this method does
        nothing.

        Otherwise, calls :meth:`DoBounce` and, if that call returns ``True``,
        schedules a future call to this method.
        """

        # We use a closure, as if this dialog
        # gets destroyed while a call is
        # scheduled, wx segfaults when it tries
        # to call the instance method.
        def realAutoBounce():

            if not isalive(self):
                return

            if not self.__bouncing:
                return

            if self.DoBounce():
                wx.CallLater(self.__delay, realAutoBounce)

        realAutoBounce()
