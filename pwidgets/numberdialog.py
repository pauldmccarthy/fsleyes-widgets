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


class NumberDialog(wx.Dialog):
    """A :class:`wx.Dialog` which prompts the user for a number.

    This class differs from the :class:`wx.NumberEntryDialog` in that
    it supports floating point numbers.
    
    A ``NumberDialog`` contains a :class:`wx.TextCtrl` and *Ok*/*Cancel*
    buttons, allowing the user to specify a number. If the user pushes the
    *Ok* button, the number they entered will be accessible via the
    :meth:`GetValue` method.

    If the user enters an invalid value (i.e. not a number, or outside
    of the minimum/maximum range if specifed), an error message is
    displayed, and the user is prompted to enter a new value.

     .. note::
        I've specifically not used the :class:`wx.SpinCtrl` or
        :class:`wx.SpinCtrlDouble`, because they are too limited in their
        flexibility with regard to validation and events.

        This class was written before I wrote the :class:`.FloatSpinCtrl`
        class - I may update this class at some stage in the future to
        use ``FloatSpinCtrl``.
    """

    def __init__(self,
                 parent,
                 real=True,
                 title=None,
                 message=None,
                 initial=None,
                 minValue=None,
                 maxValue=None):
        """Create a :class:`NumberDialog`.

        :arg parent:   The :mod:`wx` parent object.

        :arg real:     If ``True``, a floating point number will 
                       be accepted. Otherwise, only integers are
                       accepted.

        :arg title:    Dialog title.
        
        :arg message:  If not None, a :class:`wx.StaticText` label 
                       is added, containing the message.

        :arg initial:  Initial value.
        
        :arg minValue: Minimum value.
        
        :arg maxValue: Maximum value.
        """

        if title   is None: title   = ''
        if initial is None: initial = 0

        wx.Dialog.__init__(self, parent, title=title)

        self.__value    = None
        self.__real     = real
        self.__minValue = minValue
        self.__maxValue = maxValue

        if self.__real: initial = float(initial)
        else:          initial = int(  initial)

        self.__panel = wx.Panel(self)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__panel.SetSizer(self.__sizer)

        self.__buttonPanel = wx.Panel(self.__panel)
        self.__buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__buttonPanel.SetSizer(self.__buttonSizer)

        if message is not None:
            self.__label = wx.StaticText(self.__panel, label=message)
            self.__sizer.Add(self.__label, flag=wx.EXPAND)

        self.__textctrl = wx.TextCtrl(self.__panel, style=wx.TE_PROCESS_ENTER)
        self.__textctrl.SetValue('{}'.format(initial))

        self.__sizer.Add(self.__textctrl, flag=wx.EXPAND)

        self.__errorLabel = wx.StaticText(self.__panel)
        self.__errorLabel.SetForegroundColour('#992222')
        
        self.__sizer.Add(self.__errorLabel)
        self.__sizer.Show(self.__errorLabel, False)

        self.__okButton     = wx.Button(self.__buttonPanel, label='Ok')
        self.__cancelButton = wx.Button(self.__buttonPanel, label='Cancel')

        self.__buttonSizer.Add(self.__okButton,
                               flag=wx.EXPAND,
                               proportion=1)
        self.__buttonSizer.Add(self.__cancelButton,
                               flag=wx.EXPAND,
                               proportion=1)

        self.__sizer.Add(self.__buttonPanel, flag=wx.EXPAND)

        self.__textctrl    .Bind(wx.EVT_TEXT_ENTER, self.__onOk)
        self.__okButton    .Bind(wx.EVT_BUTTON,     self.__onOk)
        self.__cancelButton.Bind(wx.EVT_BUTTON,     self.__onCancel)
        
        self.__panel.Layout()
        self.__panel.Fit()

        self.Fit()

        
    def GetValue(self):
        """Return the value that the user entered.
        
        After a valid value has been entered, and OK button pushed (or
        enter pressed), this method may be used to retrieve the value.
        Returns ``None`` in all other situations.
        """
        return self.__value


    def __validate(self):
        """Validates the current value.

        If the value is valid, returns it.  Otherwise a :exc:`ValueError`
        is raised with an appropriate message.
        """
        
        value = self.__textctrl.GetValue()

        if self.__real: cast = float
        else:           cast = int
        
        try:
            value = cast(value)
        except:
            if self.__real: err = ' floating point'
            else:           err = 'n integer'
            raise ValueError('The value must be a{}'.format(err))

        if self.__minValue is not None and value < self.__minValue:
            raise ValueError('The value must be at '
                             'least {}'.format(self.__minValue))
            
        if self.__maxValue is not None and value > self.__maxValue:
            raise ValueError('The value must be at '
                             'most {}'.format(self.__maxValue))

        return value


    def __onOk(self, ev):
        """Called when the Ok button is pushed, or enter is pressed.

        If the entered value is valid, it is stored and the dialog is closed.
        The value may be retrieved via the :meth:`GetValue` method. If the
        value is not valid, the dialog remains open.
        """
        
        try:
            value = self.__validate()
            
        except ValueError as e:
            self.__errorLabel.SetLabel(e.message)
            self.__sizer.Show(self.__errorLabel, True)
            self.__panel.Layout()
            self.__panel.Fit()
            self.Fit()
            return
            
        self.__value = value
        self.EndModal(wx.ID_OK)
        self.Destroy()

        
    def __onCancel(self, ev):
        """Called when the Cancel button is pushed. Closes the dialog."""
        self.__value = None
        self.EndModal(wx.ID_CANCEL)
        self.Destroy() 
