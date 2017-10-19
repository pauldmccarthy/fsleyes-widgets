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


class Bounce(wx.ProgressDialog):
    """Display a 'bouncing' progress bar.

    The ``Bounce`` class is a ``wx.ProgressDialog`` for use with tasks with an
    unknown duration. The progress bar 'bounces' back and forth until the
    dialog is destroyed or cancelled.

    Once a ``Bounce`` dialog has been created, the :meth:`StartBounce``
    method can be used to start bouncing.
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
        self.__finish    = False

        wx.ProgressDialog.__init__(self, *args, **kwargs)


    @classmethod
    def runWithBounce(cls, task, *args, **kwargs):
        """Runs the given ``task`` in a separate thread, and creates a
        ``Bounce`` dialog which is displayed while the task is running.

        :arg polltime: Must be passed as a keyword argument.
        """

        dlg = Bounce(*args, **kwargs)

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

        dlg.Show()
        dlg.StartBounce()

        while True:
            wx.Yield()
            thread.join(0.05)
            wx.Yield()

            if not thread.is_alive():
                break
            if dlg.WasCancelled():
                break

        dlg.Destroy()
        dlg = None


    def Close(self):
        """Close the ``Bounce`` dialog. """
        self.__finish = True
        wx.ProgressDialog.Close(self)


    def EndModal(self, code=wx.ID_OK):
        """Close the ``Bounce`` dialog. """
        self.__finish = True
        wx.ProgressDialog.EndModal(self, code)


    def Destroy(self):
        """Destroy the ``Bounce`` dialog. """
        self.__finish = True
        wx.ProgressDialog.Destroy(self)


    def StartBounce(self):
        """Start bouncing. """
        self.__doBounce()


    def __doBounce(self):
        """Update the progress bar. """

        newval = self.__values[self.__index]

        if self.__finish or \
           self.WasCancelled() or \
           not self.Update(newval):
            return

        self.__index += self.__direction

        if self.__index >= len(self.__values):
            self.__index     = len(self.__values) - 2
            self.__direction = -self.__direction
        elif self.__index == 0:
            self.__index     = 0
            self.__direction = -self.__direction

        wx.CallLater(self.__delay, self.__doBounce)
