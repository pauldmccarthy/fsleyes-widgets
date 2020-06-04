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


import time
import logging

import                    wx
import wx.lib.newevent as wxevent

import fsleyes_widgets as fw


log = logging.getLogger(__name__)


if fw.wxversion() == fw.WX_PHOENIX: FloatSpinBase = wx.Panel
else:                               FloatSpinBase = wx.PyPanel


class FloatSpinCtrl(FloatSpinBase):
    """A ``FloatSpinCtrl`` is a :class:`wx.Panel` which contains a
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
                 minValue=None,
                 maxValue=None,
                 increment=None,
                 value=None,
                 style=None,
                 width=None,
                 evDelta=None,
                 precision=None):
        """Create a ``FloatSpinCtrl``.

        The following style flags are available:
          .. autosummary::
             FSC_MOUSEWHEEL
             FSC_INTEGER
             FSC_NO_LIMIT

        :arg parent:    The parent of this control (e.g. a :class:`wx.Panel`).

        :arg minValue:  Initial minimum value.

        :arg maxValue:  Initial maximum value.

        :arg increment: Default increment to apply when the user changes the
                        value via the spin button or mouse wheel.

        :arg value:     Initial value.

        :arg style:     Style flags - a combination of :data:`FSC_MOUSEWHEEL`,
                        :data:`FSC_INTEGER`, and :data:`FSC_NO_LIMIT`.

        :arg width:     If provided, desired text control width (in
                        characters).

        :arg evDelta:   Minimum time between consecutive ``wx.SpinButton``
                        events. On Linux/GTK, the wx.SpinButton is badly
                        behaved - if, while clicking on the mouse button, the
                        user moves the mouse even a tiny bit, more than one
                        spin event will be generated. To work around this
                        (without having to write my own ``wx.SpinButton``
                        implementation), the ``evDelta`` parameter allows me
                        to throttle the maximum rate at which events received
                        from the spin button can be processed. This is
                        implemented in the :meth:`__onSpinDown` and
                        :meth:`__onSpinUp` methods.

                        This has the side effect that if the user clicks and
                        holds on the spin button, they have to wait <delta>
                        seconds between increments/decrements.

        :arg precision: The desired precision to the right of the decimal
                        value. Ignored if the :attr:`FSC_INTEGER` style is
                        active.
        """
        FloatSpinBase.__init__(self, parent)

        if minValue  is None: minValue  = 0
        if maxValue  is None: maxValue  = 100
        if value     is None: value     = 0
        if increment is None: increment = 1
        if style     is None: style     = 0
        if evDelta   is None: evDelta   = 0.5

        self.__integer = style & FSC_INTEGER
        self.__nolimit = style & FSC_NO_LIMIT

        self.__value     = value
        self.__increment = increment
        self.__realMin   = float(minValue)
        self.__realMax   = float(maxValue)
        self.__realRange = abs(self.__realMax - self.__realMin)

        # Attributes used in spin
        # button event rate throttling
        self.__lastEvent  = time.time()
        self.__eventDelta = evDelta

        # We use the full signed 32 bit integer
        # range offered by the wx.SpinButton class.
        self.__realSpinMin = -2 ** 31
        self.__realSpinMax =  2 ** 31 - 1

        # Unless the no limit style has been
        # specified, in which case we map the
        # real data range to 16 bits, and
        # allow the rest of the 32 bit range
        # to account for overflow. In either
        # case, the spin button is configured
        # to use the full 32 bit range.
        if  self.__nolimit:
            self.__spinMin = -2 ** 15
            self.__spinMax =  2 ** 15 - 1
        else:
            self.__spinMin = self.__realSpinMin
            self.__spinMax = self.__realSpinMax

        self.__spinRange = abs(self.__spinMax - self.__spinMin)

        self.__text = wx.TextCtrl(  self,
                                    style=wx.TE_PROCESS_ENTER)
        self.__spin = wx.SpinButton(self,
                                    style=wx.SP_VERTICAL | wx.SP_ARROW_KEYS)

        self.__spin.SetRange(self.__realSpinMin, self.__realSpinMax)

        if width is not None:
            width = self.__text.GetTextExtent('0' * width)[0]
            self.__text.SetMinSize((width + 10, -1))
            self.__text.SetMaxSize((width + 10, -1))

        if self.__integer: self.__format = '{:d}'
        else:              self.__format = '{:.7G}'

        if   self.__integer:    self.__format = '{:d}'
        elif precision is None: self.__format = '{:.7G}'
        else:                   self.__format = '{:.' + str(precision) + 'f}'

        # Events on key down, enter, focus
        # lost, and on the spin control
        self.__text.Bind(wx.EVT_KEY_DOWN,   self.__onKeyDown)
        self.__text.Bind(wx.EVT_TEXT_ENTER, self.__onText)
        self.__text.Bind(wx.EVT_KILL_FOCUS, self.__onKillFocus)
        self.__spin.Bind(wx.EVT_SPIN_UP,    self.__onSpinUp)
        self.__spin.Bind(wx.EVT_SPIN_DOWN,  self.__onSpinDown)

        # Event on mousewheel
        # if style enabled
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

        # Under linux/GTK, double-clicking the
        # textctrl selects the word underneath
        # the cursor, whereas we want it to
        # select the entire textctrl contents.
        # Mouse event behaviour cannot be overridden
        # under OSX, but its behaviour is more
        # sensible, so a hack is not necessary.
        if wx.Platform == '__WXGTK__':
            self.__text.Bind(wx.EVT_LEFT_DCLICK, self.__onDoubleClick)

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.__sizer.Add(self.__text, flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__spin)

        self.Layout()

        self.SetSizer(  self.__sizer)
        self.SetMinSize(self.__sizer.GetMinSize())

        self.SetRange(minValue, maxValue)
        self.SetIncrement(increment)


    @property
    def textCtrl(self):
        """Returns a reference to the ``TextCtrl`` contained in this
        ``FloatSpinCtrl``.
        """
        return self.__text


    @property
    def spinButton(self):
        """Returns a reference to the ``SpinButton`` contained in this
        ``FloatSpinCtrl``.
        """
        return self.__spin


    def DoGetBestClientSize(self):
        """Returns the best size for this ``FloatSpinCtrl``.
        """
        return self.__sizer.GetMinSize()


    def GetValue(self):
        """Returns the current value."""
        return self.__value


    def GetMin(self):
        """Returns the current minimum value."""
        return float(self.__realMin)


    def GetMax(self):
        """Returns the current maximum value."""
        return float(self.__realMax)


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

        if minval > maxval:
            raise ValueError('Min cannot be greater than max '
                             '({} > {})'.format(minval, maxval))

        if self.__integer:
            minval = int(round(minval))
            maxval = int(round(maxval))

        self.__realMin   = float(minval)
        self.__realMax   = float(maxval)
        self.__realRange = abs(self.__realMax - self.__realMin)

        self.SetValue(self.__value)


    def SetValue(self, newValue):
        """Sets the value.

        :returns ``True`` if the value was changed, ``False`` otherwise.
        """

        # Clamp the value so it stays
        # within the min/max, unless the
        # FSC_NO_LIMIT style flag is set.
        if not self.__nolimit:
            if newValue < self.__realMin: newValue = self.__realMin
            if newValue > self.__realMax: newValue = self.__realMax

        if self.__integer:
            newValue = int(round(newValue))

        oldValue     = self.__value
        self.__value = newValue

        self.__text.ChangeValue(self.__format.format(newValue))

        # The wx.SpinButton is badly behaved. It doesn't have
        # a ChangeValue method (which would explicitly allow
        # us to update the stored spin button value without
        # triggering an event), and under GTK, when the
        # SetValue method is called from a SPIN_UP/SPIN_DOWN
        # event, it will trigger another event. So we disable
        # events from the spin button when setting the value.
        self.__spin.SetEvtHandlerEnabled(False)
        self.__spin.SetValue(self.__realToSpin(newValue))

        # We have to re-enable event processing
        # asynchronously, otherwise the SpinButton
        # will keep generating events.  We check
        # the state of this control before doing
        # so, as the control may get deleted before
        # this function gets called.
        def reset():
            if self and self.__spin:
                self.__spin.SetEvtHandlerEnabled(True)

        wx.CallAfter(reset)

        return newValue != oldValue


    def __onKillFocus(self, ev):
        """Called when the text field of this ``FloatSpinCtrl`` loses focus.
        Generates an :attr:`.EVT_FLOATSPIN` event.
        """
        ev.Skip()

        log.debug('Spin lost focus - simulating text event')
        self.__onText(ev)


    def __onKeyDown(self, ev):
        """Called on ``wx.EVT_KEY_DOWN`` events. If the user pushes the up or
        down arrow keys, the value is changed (using the :meth:`__onSpinUp`
        and :meth:`__onSpinDown` methods).
        """
        up   = wx.WXK_UP
        down = wx.WXK_DOWN
        key  = ev.GetKeyCode()

        log.debug('Key down event: {} (looking for up [{}] '
                  'or down [{}])'.format(key, up, down))

        if   key == up:   self.__onSpinUp()
        elif key == down: self.__onSpinDown()
        else:             ev.Skip()


    def __onText(self, ev):
        """Called when the user changes the value via the text control.

        This method is called when the enter key is pressed.

        If the entered value is a valid number, a ``wx.EVT_TEXT_ENTER``
        event is generated. This event will have a boolean attribute,
        ``changed``, which is ``True`` if the value that was stored was
        different to that entered by the user (e.g. if it was clamped
        to the min/max bounds).

        If the value was changed from its previous value, a
        :data:`FloatSpinEvent` is also generated.
        """

        val = self.__text.GetValue().strip()

        log.debug('Spin text - attempting to change value '
                  'from {} to {}'.format(self.__value, val))

        try:
            if self.__integer: val = int(  val)
            else:              val = float(val)
        except ValueError:
            self.SetValue(self.__value)
            return
        valset = self.SetValue(val)

        # Add a 'changed' attribute so
        # users can tell if the value
        # that was entered was not the
        # value that ended up getting
        # stored
        ev         = wx.PyCommandEvent(wx.EVT_TEXT_ENTER.typeId, self.GetId())
        ev.changed = val != self.__value
        wx.PostEvent(self.GetEventHandler(), ev)

        # Emit a spin event if the value
        # changed from its previous value
        if valset:
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))


    def __onSpinDown(self, ev=None):
        """Called when the *down* button on the ``wx.SpinButton`` is pushed.

        Decrements the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """

        # See comments in __init__
        if ev is not None:

            lastEv = self.__lastEvent
            thisEv = time.time()

            if thisEv - lastEv < self.__eventDelta:
                return

            self.__lastEvent = thisEv

        log.debug('Spin down button - attempting to change value '
                  'from {} to {}'.format(self.__value,
                                         self.__value - self.__increment))

        if self.SetValue(self.__value - self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))


    def __onSpinUp(self, ev=None):
        """Called when the *up* button on the ``wx.SpinButton`` is pushed.

        Increments the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """

        # See comments in __init__
        if ev is not None:
            lastEv = self.__lastEvent
            thisEv = time.time()

            if thisEv - lastEv < self.__eventDelta:
                return
            self.__lastEvent = thisEv

        log.debug('Spin up button - attempting to change value '
                  'from {} to {}'.format(self.__value,
                                         self.__value + self.__increment))

        if self.SetValue(self.__value + self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))


    def __onMouseWheel(self, ev):
        """If the :data:`FSC_MOUSEWHEEL` style flag is set, this method is
        called on mouse wheel events.

        Calls :meth:`__onSpinUp` on an upwards rotation, and
        :meth:`__onSpinDown` on a downwards rotation.
        """

        log.debug('Mouse wheel - delegating to spin event handlers')

        rot = ev.GetWheelRotation()

        if ev.GetWheelAxis() == wx.MOUSE_WHEEL_HORIZONTAL:
            rot = -rot

        if   rot > 0: self.__onSpinUp()
        elif rot < 0: self.__onSpinDown()


    def __onDoubleClick(self, ev):
        """Called when the user double clicks in the ``TextCtrl``. Selects
        the entire contents of the ``TextCtrl``.
        """
        self.__text.SelectAll()


    def __realToSpin(self, value):
        """Converts the given value from real space to spin button space."""

        if self.__realRange == 0:
            return 0

        if self.__integer:
            value = int(round(value))

        value     = float(value)
        spinMin   = float(self.__spinMin)
        realMin   = float(self.__realMin)
        realRange = float(self.__realRange)
        spinRange = float(self.__spinRange)

        value     = spinMin + (value - realMin) * (spinRange / realRange)

        # Don't allow the value to flow over
        # the real wx.SpinButton range.
        if   value < self.__realSpinMin: value = self.__realSpinMin
        elif value > self.__realSpinMax: value = self.__realSpinMax

        return int(round(value))


_FloatSpinEvent,      _EVT_FLOATSPIN       = wxevent.NewEvent()
_FloatSpinEnterEvent, _EVT_FLOATSPIN_ENTER = wxevent.NewEvent()


EVT_FLOATSPIN = _EVT_FLOATSPIN
"""Identifier for the :data:`FloatSpinEvent` event. """


FloatSpinEvent = _FloatSpinEvent
"""Event emitted when the floating point value is changed by the user. A
``FloatSpinEvent`` has the following attributes:

  - ``value``: The new value.
"""


FSC_MOUSEWHEEL = 1
"""If set, mouse wheel events on the control will change the value. """


FSC_INTEGER = 2
"""If set, the control stores an integer value, rather than a floating point
value.
"""

FSC_NO_LIMIT = 4
"""If set, the control will allow the user to enter values that are outside
of the current minimum/maximum limits.
"""
