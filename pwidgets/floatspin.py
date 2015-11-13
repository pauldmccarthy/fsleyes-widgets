#!/usr/bin/env python
#
# floatspin.py - Alternate implementation to wx.SpinCtrlDouble and
#                wx.lib.agw.floatspin.FloatSpin.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`FloatSpinCtrl` class, a spin control for
modifying a floating point value.
"""


import                    logging

import                    wx
import wx.lib.newevent as wxevent

import re


log = logging.getLogger(__name__)


class FloatSpinCtrl(wx.PyPanel):
    """A ``FloatSpinCtrl`` is a :class:`wx.PyPanel` which contains a
    :class:`wx.TextCtrl` and a :class:`wx.SpinButton`, allowing the user to
    modify a floating point (or integer) value.

    The ``FloatSpinCtrl`` is an alternative to :class:`wx.SpinCtrl`,
    :class:`wx.SpinCtrlDouble`, and :class:`wx.lib.agw.floatspin.FloatSpin`.

     - :class:`wx.SpinCtrlDouble`: Under Linux/GTK, this widget does not allow
        the user to enter values that are not a multiple of the increment.

     - :class:`wx.lib.agw.floatspin.FloatSpin`. Differs from the
       :class:`wx.SpinCtrl` API in various annoying ways, and formatting is a
       pain.
    """

    def __init__(self,
                 parent,
                 minValue=0,
                 maxValue=100,
                 increment=1,
                 value=0,
                 style=0):
        """Create a ``FloatSpinCtrl``.

        The following style flags are available:
          .. autosummary::
             FSC_MOUSEWHEEL
             FSC_EVENT_ON_TEXT
             FSC_INTEGER

        :arg parent:    The parent of this control (e.g. a :class:`wx.Panel`).

        :arg minValue:  Initial minimum value.

        :arg maxValue:  Initial maximum value.

        :arg increment: Default increment to apply when the user changes the
                        value via the spin button or mouse wheel.

        :arg value:     Initial value.

        :arg style:     Style flags - a combination of :data:`FSC_MOUSEWHEEL`,
                        :data:`FSC_EVENT_ON_TEXT`, and :data:`FSC_INTEGER`.

        """
        wx.PyPanel.__init__(self, parent)

        self.__value     = value
        self.__increment = increment
        self.__realMin   = float(minValue)
        self.__realMax   = float(maxValue)
        self.__realRange = abs(self.__realMax - self.__realMin)
        
        self.__integer   = style & FSC_INTEGER > 0

        self.__spinMin   = -2 ** 31
        self.__spinMax   =  2 ** 31 - 1
        self.__spinRange = abs(self.__spinMax - self.__spinMin)

        self.__text = wx.TextCtrl(  self,
                                    style=wx.TE_PROCESS_ENTER)
        self.__spin = wx.SpinButton(self,
                                    style=wx.SP_VERTICAL | wx.SP_ARROW_KEYS)

        self.__spin.SetRange(self.__spinMin, self.__spinMax)

        if self.__integer:
            self.__format      = '{:d}'
            self.__textPattern = re.compile('^-?[0-9]*$')
        else:
            self.__format      = '{:.7G}'
            self.__textPattern = re.compile('^-?[0-9]*\.?[0-9]*$')

        # Event whenever the text changes
        if style & FSC_EVENT_ON_TEXT:
            self.__text.Bind(wx.EVT_TEXT, self.__onText)

        # Event on enter or lose focus
        else:
            self.__text.Bind(wx.EVT_TEXT_ENTER, self.__onText)
            self.__text.Bind(wx.EVT_KILL_FOCUS, self.__onText)
            
        self.__spin.Bind(wx.EVT_SPIN_UP,   self.__onSpinUp)
        self.__spin.Bind(wx.EVT_SPIN_DOWN, self.__onSpinDown)

        if style & FSC_MOUSEWHEEL:
            self.__spin.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)
            self.__text.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        # Under linux/GTK, text controls absorb
        # mousewheel events, so we bind our own
        # handler to prevent this.
        elif wx.Platform == '__WXGTK__':
            def wheel(ev):
                self.GetParent().GetEventHandler().ProcessEvent(ev)
            self.__spin.Bind(wx.EVT_MOUSEWHEEL, wheel)
            self.__text.Bind(wx.EVT_MOUSEWHEEL, wheel)

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.__sizer.Add(self.__text, flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__spin)
        
        self.SetSizer(self.__sizer)

        # Under wx/GTK, calling spin.SetValue() from
        # within an EVT_SPIN event handler seems to
        # generate another EVT_SPIN event, which
        # triggers an infinite recursive loop. The
        # skipSpin attribute  is used as an internal
        # semaphore in the SetValue method, telling
        # it not to update the spin button value.
        self.__skipSpin = False

        self.SetRange(minValue, maxValue)
        self.SetValue(value)
        self.SetIncrement(increment)

    
    def GetValue(self):
        """Returns the current value."""
        return self.__value
    

    def GetMin(self):
        """Returns the current minimum value."""
        return self.__realMin

    
    def GetMax(self):
        """Returns the current maximum value."""
        return self.__realMax


    def GetIncrement(self):
        """Returns the current inrement."""
        return self.__increment


    def SetIncrement(self, inc):
        """Sets the inrement."""
        if self.__integer: self.__increment = int(round(inc))
        else:              self.__increment =           inc

        
    def GetRange(self):
        """Returns the current data range, a tuple containing the
        ``(min, max)`` values.
        """
        return (self.__realMin, self.__realMax)


    def SetMin(self, minval):
        """Sets the minimum value."""
        self.SetRange(minval, self.__realMax)

    
    def SetMax(self, maxval):
        """Sets the maximum value."""
        self.SetRange(self.__realMin, maxval)

    
    def SetRange(self, minval, maxval):
        """Sets the minimum and maximum values."""
        
        inc = (maxval - minval) / 100.0

        if self.__integer:
            minval = int(round(minval))
            maxval = int(round(maxval))
            inc    = 1

        if minval >= maxval:
            maxval = minval + 1

        self.__realMin   = minval
        self.__realMax   = maxval
        self.__realRange = abs(maxval - minval)
        self.__increment = inc

        self.SetValue(self.__value)

    
    def SetValue(self, value):
        """Sets the value.

        :returns ``True`` if the value was changed, ``False`` otherwise.
        """

        if self.__integer:
            value = int(round(value))

        if value < self.__realMin: value = self.__realMin
        if value > self.__realMax: value = self.__realMax

        oldValue     = self.__value
        self.__value = value

        self.__text.ChangeValue(self.__format.format(value))

        if not self.__skipSpin:
            self.__spin.SetValue(self.__realToSpin(value))

        return value != oldValue
    

    def __onText(self, ev):
        """Called when the user changes the value via the text control.

        If the :data:`FSC_EVENT_ON_TEXT` style is set, this method is called
        on every text event. Otherwise, this method is called when the enter
        key is pressed, or when the text control loses focus.

        If the value has changed, a :data:`FloatSpinEvent` is generated.
        """

        val = self.__text.GetValue().strip()
        
        if self.__textPattern.match(val) is None:
            self.SetValue(self.__value)
            return

        log.debug('Spin text - attempting to change value '
                  'from {} to {}'.format(self.__value, val))

        try:
            if self.__integer: val = int(  val)
            else:              val = float(val)
        except:
            self.SetValue(self.__value)
            return

        if self.SetValue(val):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value)) 


    def __onSpinDown(self, ev=None):
        """Called when the *down* button on the ``wx.SpinButton`` is pushed.

        Decrements the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """
        
        log.debug('Spin down button - attempting to change value '
                  'from {} to {}'.format(self.__value,
                                         self.__value - self.__increment))

        self.__skipSpin = True
        
        if self.SetValue(self.__value - self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))
            
        self.__skipSpin = False

        
    def __onSpinUp(self, ev=None):
        """Called when the *up* button on the ``wx.SpinButton`` is pushed.

        Increments the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """
        
        log.debug('Spin up button - attempting to change value '
                  'from {} to {}'.format(self.__value,
                                         self.__value + self.__increment))

        self.__skipSpin = True

        try:
            if self.SetValue(self.__value + self.__increment):
                wx.PostEvent(self, FloatSpinEvent(value=self.__value))
        finally:
            self.__skipSpin = False


    def __onMouseWheel(self, ev):
        """If the :data:`FSC_MOUSEWHEEL` style flag is set, this method is
        called on mouse wheel events.

        Calls :meth:`__onSpinUp` on an upwards rotation, and
        :meth:`__onSpinDown` on a downwards rotation.
        """

        log.debug('Mouse wheel - delegating to spin event handlers')

        rot = ev.GetWheelRotation()
        
        if   rot > 0: self.__onSpinUp()
        elif rot < 0: self.__onSpinDown()
    
        
    def __spinToReal(self, value):
        """Converts the given value from spin button space to real space."""
        
        value = self.__realMin + (value - self.__spinMin) * \
            (float(self.__realRange) / self.__spinRange)

        if self.__integer: return int(round(value))
        else:              return value

        
    def __realToSpin(self, value):
        """Converts the given value from real space to spin button space."""

        if self.__integer:
            value = int(round(value))
        
        value = self.__spinMin + (value - self.__realMin) * \
            (self.__spinRange / float(self.__realRange))
        return int(round(value))        


_FloatSpinEvent, _EVT_FLOATSPIN = wxevent.NewEvent()


EVT_FLOATSPIN = _EVT_FLOATSPIN
"""Identifier for the :data:`FloatSpinEvent` event. """


FloatSpinEvent = _FloatSpinEvent
"""Event emitted when the floating point value is changed by the user. A
``FloatSpinEvent`` has the following attributes:

  - ``value``: The new value.
"""


FSC_MOUSEWHEEL = 1
"""If set, mouse wheel events on the control will change the value. """


FSC_EVENT_ON_TEXT = 2
"""If set, a ``FloatSpinEvent`` is emitted on every text event. If not set, a
``FloatSpinEvent`` is only emitted when the enter key is pressed, or the
control loses focus.
"""


FSC_INTEGER = 4
"""If set, the control stores an integer value, rather than a floating point
value.
"""
