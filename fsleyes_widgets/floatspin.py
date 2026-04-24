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


log = logging.getLogger(__name__)



class SpinButton(wx.Control):
    """Replacement for ``wx.SpinButton``.

    A control which contains up and down buttons, and which emits events
    :attr:`EVT_SPIN_UP`  and :attr:`EVT_SPIN_DOWN` events when they are
    pressed.

    This is used by the :class:`FloatSpinCtrl` instead of the
    ``wx.SpinButton`` because:

      - The``wx.SpinButton`` internally stores the current value as a
        signed 32 bit integer. It is much easier for the ``FloatSpinCtrl``
        to keep track of it sown value and limits.

      - The ``FloatSpinCtrl`` displays its own text area, but on some GTK
        versions, the ``wx.SpinButton`` displays a text area, I think due
        to some latent bugs in wxwidgets - see e.g.
        https://github.com/wxWidgets/wxWidgets/issues/17847
    """


    def __init__(self,
                 parent,
                 style=wx.HORIZONTAL,
                 upLabel='\u002B',
                 downLabel='\u2212'):
        """Create a ``SpinButton``.

        :arg parent:    ``wx`` parent object
        :arg style:     Button orientation - either ``wx.HORIZONTAL`` or
                        ``wx.VERTICAL``
        :arg upLabel:   Up button label
        :arg downLabel: Down button label
        """
        super().__init__(parent)

        if style not in (wx.HORIZONTAL, wx.VERTICAL):
            raise ValueError('Unknown style - must be one of '
                             f'wx.HORIZONTAL or wx.VERTICAL: {style}')

        sizer = wx.BoxSizer(style)
        up    = wx.Button(self, label=upLabel,   style=wx.BU_EXACTFIT)
        down  = wx.Button(self, label=downLabel, style=wx.BU_EXACTFIT)

        self.__sizer = sizer
        self.__up    = up
        self.__down  = down

        self.SetSizer(sizer)
        up  .SetFont(up  .GetFont().Larger())
        down.SetFont(down.GetFont().Larger())

        if style == wx.VERTICAL:
            sizer.Add(up)
            sizer.Add(down)
        else:
            sizer.Add(down)
            sizer.Add(up)

        up  .Bind(wx.EVT_BUTTON, self.__onUp)
        down.Bind(wx.EVT_BUTTON, self.__onDown)


    @property
    def upButton(self):
        """Returns a reference to the up button. """
        return self.__up


    @property
    def downButton(self):
        """Returns a reference to the down button. """
        return self.__down


    def EnableUp(self, enable):
        """Enable/disable the up button. """
        self.__up.Enable(bool(enable))


    def DisableUp(self):
        """Disable the up button. """
        self.__up.Disable()


    def EnableDown(self, enable):
        """Enable/disable the down button. """
        self.__down.Enable(bool(enable))


    def DisableDown(self):
        """Disable the down button. """
        self.__down.Disable()


    def __onUp(self, ev):
        """Called when the up button is pressed. Emits a ``EVT_SPIN_UP``
        event.
        """
        wx.PostEvent(self, SpinUpEvent())


    def __onDown(self, ev):
        """Called when the down button is pressed. Emits a ``EVT_SPIN_DOWN``
        event.
        """
        wx.PostEvent(self, SpinDownEvent())


_SpinUpEvent,   _EVT_SPIN_UP   = wxevent.NewEvent()
_SpinDownEvent, _EVT_SPIN_DOWN = wxevent.NewEvent()


EVT_SPIN_UP = _EVT_SPIN_UP
"""Identifier for the :data:`SpinUpEvent` event. """

EVT_SPIN_DOWN = _EVT_SPIN_DOWN
"""Identifier for the :data:`SpinDownEvent` event. """


SpinUpEvent = _SpinUpEvent
"""Event emitted when by a ``SpinButton`` when its up button is pushed. """


SpinDownEvent = _SpinDownEvent
"""Event emitted when by a ``SpinButton`` when its down button is pushed. """


class FloatSpinCtrl(wx.Control):
    """A ``FloatSpinCtrl`` is a :class:`wx.Control` which contains a
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

        :arg evDelta:   Deprecated, has no effect.

                        This has the side effect that if the user clicks and
                        holds on the spin button, they have to wait <delta>
                        seconds between increments/decrements.

        :arg precision: The desired precision to the right of the decimal
                        value. Ignored if the :attr:`FSC_INTEGER` style is
                        active.
        """
        wx.Control.__init__(self, parent)

        if minValue  is None: minValue  = 0
        if maxValue  is None: maxValue  = 100
        if value     is None: value     = 0
        if increment is None: increment = 1
        if style     is None: style     = 0

        self.__integer = style & FSC_INTEGER
        self.__nolimit = style & FSC_NO_LIMIT

        self.__value     = value
        self.__increment = increment
        self.__min       = float(minValue)
        self.__max       = float(maxValue)
        self.__range     = abs(self.__max - self.__min)

        self.__text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.__spin = SpinButton( self)

        # spinSize = self.__spin.GetSize()
        # spinSize = (spinSize[0] + 20, spinSize[1] + 20)
        # print(spinSize)
        # self.__spin.SetMinSize(spinSize)

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
        self.__spin.Bind(EVT_SPIN_UP,       self.__onSpinUp)
        self.__spin.Bind(EVT_SPIN_DOWN,     self.__onSpinDown)

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
        return float(self.__min)


    def GetMax(self):
        """Returns the current maximum value."""
        return float(self.__max)


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
        return (self.__min, self.__max)


    def SetMin(self, minval):
        """Sets the minimum value."""
        self.SetRange(minval, self.__max)


    def SetMax(self, maxval):
        """Sets the maximum value."""
        self.SetRange(self.__min, maxval)


    def SetRange(self, minval, maxval):
        """Sets the minimum and maximum values."""

        if minval > maxval:
            raise ValueError('Min cannot be greater than '
                             f'max ({minval} > {maxval})')

        if self.__integer:
            minval = int(round(minval))
            maxval = int(round(maxval))

        self.__min   = float(minval)
        self.__max   = float(maxval)
        self.__range = abs(self.__max - self.__min)

        self.SetValue(self.__value)


    def SetValue(self, newValue):
        """Sets the value.

        :returns ``True`` if the value was changed, ``False`` otherwise.
        """

        # Clamp the value so it stays
        # within the min/max, unless the
        # FSC_NO_LIMIT style flag is set.
        if not self.__nolimit:
            if newValue < self.__min: newValue = self.__min
            if newValue > self.__max: newValue = self.__max

        if self.__integer:
            newValue = int(round(newValue))

        oldValue     = self.__value
        self.__value = newValue

        self.__text.ChangeValue(self.__format.format(newValue))

        if not self.__nolimit:
            self.__spin.EnableUp(  newValue < self.__max)
            self.__spin.EnableDown(newValue > self.__min)

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

        log.debug('Key down event: %s (looking for up [%s] or down [%s])',
                  key, up, down)

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
                  'from %s to %s', self.__value, val)

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
        """Called when the *down* button on the ``SpinButton`` is pushed.

        Decrements the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """

        log.debug('Spin down button - attempting to change value from '
                  '%s to %s', self.__value, self.__value - self.__increment)

        if self.SetValue(self.__value - self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))


    def __onSpinUp(self, ev=None):
        """Called when the *up* button on the ``wx.SpinButton`` is pushed.

        Increments the value by the current increment and generates a
        :data:`FloatSpinEvent`.
        """

        log.debug('Spin up button - attempting to change value from '
                  '%s to %s', self.__value, self.__value + self.__increment)

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
