#!/usr/bin/env python
#
# numberdialog.py - An alternative to wx.NumberEntryDialog.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`NumberDialog` class, a dialog which
allows the user to enter a number.
"""

import wx


from . import floatspin


class NumberDialog(wx.Dialog):
    """A :class:`wx.Dialog` which prompts the user for a number.

    This class differs from the :class:`wx.NumberEntryDialog` in that
    it supports floating point numbers.

    A ``NumberDialog`` contains a :class:`wx.FloatSpinCtrl` and *Ok*/*Cancel*
    buttons, allowing the user to specify a number. If the user pushes the
    *Ok* button, the number they entered will be accessible via the
    :meth:`GetValue` method.
    """

    def __init__(self,
                 parent,
                 real=True,
                 title=None,
                 message=None,
                 initial=None,
                 minValue=None,
                 maxValue=None,
                 okText=None,
                 cancelText=None):
        """Create a :class:`NumberDialog`.

        :arg parent:     The :mod:`wx` parent object.

        :arg real:       If ``True``, a floating point number will
                         be accepted. Otherwise, only integers are
                         accepted.

        :arg title:      Dialog title.

        :arg message:    If not None, a :class:`wx.StaticText` label
                         is added, containing the message.

        :arg initial:    Initial value.

        :arg minValue:   Minimum value.

        :arg maxValue:   Maximum value.

        :arg okText:     Text for OK button. Defaults to "Ok".

        :arg cancelText: Text for Cancel button. Defaults to "Cancel"
        """

        if title      is None: title      = ''
        if initial    is None: initial    = 0
        if okText     is None: okText     = 'Ok'
        if cancelText is None: cancelText = 'Cancel'

        wx.Dialog.__init__(self, parent, title=title)

        self.__value       = None
        self.__cancelled   = False
        self.__sizer       = wx.BoxSizer(wx.VERTICAL)
        self.__buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizer(self.__sizer)

        if message is not None:
            self.__label = wx.StaticText(self, label=message)
        else:
            self.__label = (0, 0)

        style = floatspin.FSC_MOUSEWHEEL
        if not real:
            style |= floatspin.FSC_INTEGER
        if minValue is None and maxValue is None:
            style |= floatspin.FSC_NO_LIMIT

        self.__spinCtrl = floatspin.FloatSpinCtrl(
            self,
            minValue=minValue,
            maxValue=maxValue,
            value=initial,
            style=style)

        self.__okButton     = wx.Button(self, label=okText)
        self.__cancelButton = wx.Button(self, label=cancelText)

        self.__buttonSizer.Add(self.__okButton,
                               flag=wx.EXPAND | wx.ALL,
                               proportion=1,
                               border=2)
        self.__buttonSizer.Add(self.__cancelButton,
                               flag=wx.EXPAND | wx.ALL,
                               proportion=1,
                               border=2)

        self.__sizer.Add(self.__label, flag=wx.EXPAND | wx.ALL, border=10)
        self.__sizer.Add(self.__spinCtrl,
                         flag=(wx.EXPAND | wx.LEFT | wx.RIGHT),
                         border=15)
        self.__sizer.Add(self.__buttonSizer,
                         flag=wx.EXPAND | wx.ALL,
                         border=10)

        self.__spinCtrl    .Bind(wx.EVT_TEXT_ENTER, self.__onEnter)
        self.__okButton    .Bind(wx.EVT_BUTTON,     self.__onOk)
        self.__cancelButton.Bind(wx.EVT_BUTTON,     self.__onCancel)

        self.Layout()
        self.Fit()
        self.CentreOnParent()


    @property
    def floatSpinCtrl(self):
        """Returns a reference to the :class:`.FloatSpinCtrl`. """
        return self.__spinCtrl


    @property
    def okButton(self):
        """Returns a reference to the ok ``Button``. """
        return self.__okButton


    @property
    def cancelButton(self):
        """Returns a reference to the cancel ``Button``. """
        return self.__cancelButton


    def GetValue(self):
        """Return the value that the user entered.

        After a valid value has been entered, and OK button pushed (or
        enter pressed), this method may be used to retrieve the value.
        Returns ``None`` in all other situations.
        """
        if self.__cancelled: return None
        else:                return self.__value


    def __onEnter(self, ev):
        """Called when the enter key is pressed in the ``FloatSpinCtrl``.
        Forwards the event to the :meth:`__onOk` method.
        """
        # If the user typed in a value, and the
        # floatspin changed that value (e.g.
        # clamped it to min/max bounds), don't
        # close the dialog.
        if not ev.changed:
            self.__onOk(ev)


    def __onOk(self, ev):
        """Called when the Ok button is pushed. The entered value is stored
        and the dialog is closed.  The value may be retrieved via the
        :meth:`GetValue` method.
        """

        self.__value = self.__spinCtrl.GetValue()

        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Close()


    def __onCancel(self, ev):
        """Called when the Cancel button is pushed. Closes the dialog."""

        self.__value     = None
        self.__cancelled = True

        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
