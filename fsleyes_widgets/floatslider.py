#!/usr/bin/env python
#
# floatslider.py - Floating point slider widgets.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides two classes, the :class:`FloatSlider` and
:class:`SliderSpinPanel`, which allow the user to modify floating point
values.
"""


import numpy as np

import wx
import wx.lib.newevent as wxevent

from . import floatspin
from . import numberdialog


class FloatSlider(wx.Panel):
    """Floating point slider widget.

    This class is an alternative to :class:`wx.Slider`, which supports
    floating point numbers of any range. The desired range is transformed into
    the internal range :math:`[-2^{31}, 2^{31-1}]`.

    A :class:`EVT_SLIDER` event is emitted whenever the user changes the
    value.
    """

    def __init__(self,
                 parent,
                 value=None,
                 minValue=None,
                 maxValue=None,
                 style=0):
        """Create a ``FloatSlider``.

        The following style flags are available:

         .. autosummary::
            FS_MOUSEWHEEL
            FS_INTEGER

        :arg parent:   The :mod:`wx` parent object.

        :arg value:    Initial slider value.

        :arg minValue: Minimum slider value.

        :arg maxValue: Maximum slider value.

        :arg style:    A combination of :data:`FS_MOUSEWHEEL` and
                       :data:`FS_INTEGER`.
        """

        if value    is None: value    = 0
        if minValue is None: minValue = 0
        if maxValue is None: maxValue = 1

        self.__sliderMin   = -2 ** 31
        self.__sliderMax   =  2 ** 31 - 1
        self.__sliderRange = abs(self.__sliderMax - self.__sliderMin)
        self.__integer     = style & FS_INTEGER > 0

        wx.Panel.__init__(self, parent)

        self.__slider = wx.Slider(self,
                                  minValue=self.__sliderMin,
                                  maxValue=self.__sliderMax,
                                  style=wx.SL_HORIZONTAL)
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer.Add(self.__slider, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)

        if style & FS_MOUSEWHEEL:
            self.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        # Under GTK, slider widgets absorb
        # mousewheel events, so we bind our
        # own handler to prevent this, and
        # propagate the mousewheel event
        # upwards.
        elif wx.Platform == '__WXGTK__':
            def wheel(ev):
                self.GetParent().GetEventHandler().ProcessEvent(ev)
            self.Bind(wx.EVT_MOUSEWHEEL, wheel)

        self.__lastSliderValue = None
        self.__SetRange(minValue, maxValue)
        self.SetValue(value)

        # Under GTK, sliders don't seem to
        # be sized appropriately, so setting
        # the min size will force them to
        # have a good size
        if self.HasFlag(wx.VERTICAL): self.__slider.SetMinSize((-1,  150))
        else:                         self.__slider.SetMinSize((150, -1))

        # Under CentOS6/GTK, mouse clicks on
        # the slider do not update the slider
        # position - users have to click+drag
        # on the slider thumb. Workaround
        # is to re-implement mouse dragging
        # logic on GTK.
        if wx.Platform == '__WXGTK__':
            self.__dragging = False
            self.__slider.Bind(wx.EVT_LEFT_DOWN, self.__onMouseDown)
            self.__slider.Bind(wx.EVT_MOTION,    self.__onMouseMove)
            self.__slider.Bind(wx.EVT_LEFT_UP,   self.__onMouseUp)

        self.__slider.Bind(wx.EVT_SLIDER, self.__onSlider)


    def __onSlider(self, ev):
        """Called when the child ``wx.Slider`` instance generates an
        ``EVT_SLIDER`` event. If the slider value has changed, the
        event is propagated upwards.
        """

        newSliderValue = self.__slider.GetValue()

        # Under OSX, slider values are emitted on
        # both mouse down and mouse up events, so
        # we make sure to only propagate the event
        # if the slider value has actually changed.
        if self.__lastSliderValue is None or \
           not np.isclose(self.__lastSliderValue, newSliderValue):
            self.__lastSliderValue = newSliderValue
            ev.Skip()


    def __onMouseDown(self, ev):
        """Only called when running on GTK. Sets an internal dragging
        flag, and calls :meth:`__mouseMove`.
        """
        self.__dragging = True
        self.__onMouseMove(ev)


    def __onMouseMove(self, ev):
        """Only called when running on GTK. Updates the slider value based
        on the mouse location.
        """
        if not self.__dragging:
            return

        dataMin, dataMax = self.GetRange()
        width, height    = self.GetClientSize().Get()
        vertical         = self.GetWindowStyle() & wx.VERTICAL > 0
        x                = float(ev.GetX())
        y                = float(ev.GetY())

        if vertical: value = dataMin + (y / height) * (dataMax - dataMin)
        else:        value = dataMin + (x / width)  * (dataMax - dataMin)

        if self.SetValue(value):
            ev = wx.PyCommandEvent(wx.EVT_SLIDER.typeId, self.GetId())
            wx.PostEvent(self.GetEventHandler(), ev)


    def __onMouseUp(self, ev):
        """Only called when running on GTK. Clears the internal dragging
        flag.
        """
        self.__dragging = False


    def __onMouseWheel(self, ev):
        """If the :data:`FS_MOUSEWHEEL` style is set, this method is called
        when the mouse wheel is spun over the slider widget.

        Increases/decreases the slider value accordingly.
        """
        if not self.IsEnabled():
            return

        wheelDir  = ev.GetWheelRotation()
        increment = (self.__realMax - self.__realMin) / 100.0

        if   wheelDir < 0: increment = -increment
        elif wheelDir > 0: increment =  increment
        else:              return

        if self.SetValue(self.GetValue() + increment):
            ev = wx.PyCommandEvent(wx.EVT_SLIDER.typeId, self.GetId())
            wx.PostEvent(self.GetEventHandler(), ev)


    def GetRange(self):
        """Return a tuple containing the (minimum, maximum) slider values."""
        return (self.__realMin, self.__realMax)


    def __SetRange(self, minValue, maxValue):
        """Set the minimum/maximum slider values.

        This logic is not in the public :meth:`SetRange` method so
        we can overcome a chicken-and-egg problem in :meth:`__init__` -
        :meth:`SetValue` needs :attr:`__realMin` and :attr:`__realMax`
        to be set, but :meth:`SetRange` needs to retrieve the value
        before setting :attr:`__realMin` and :attr:`__realMax`.
        """

        minValue  = float(minValue)
        maxValue  = float(maxValue)

        if self.__integer:
            minValue  = int(round(minValue))
            maxValue  = int(round(maxValue))

        self.__realMin   = minValue
        self.__realMax   = maxValue
        self.__realRange = abs(self.__realMax - self.__realMin)


    def SetRange(self, minValue, maxValue):
        """Set the minimum/maximum slider values."""

        if minValue > maxValue:
            raise ValueError('Min cannot be greater than max '
                             '({} > {})'.format(minValue, maxValue))

        # wx.Slider values change when their bounds
        # are changed. It does this to keep the
        # slider position the same as before, but I
        # think it is more appropriate to keep the
        # slider value the same ...
        oldValue = self.GetValue()
        self.__SetRange(minValue, maxValue)
        self.SetValue(oldValue)


    def GetMin(self):
        """Return the minimum slider value."""
        return self.GetRange()[0]


    def GetMax(self):
        """Return the maximum slider value."""
        return self.GetRange()[1]


    def SetMin(self, minValue):
        """Set the minimum slider value."""
        self.SetRange(minValue, self.GetMax())


    def SetMax(self, maxValue):
        """Set the maximum slider value."""
        self.SetRange(self.GetMin(), maxValue)


    def __sliderToReal(self, value):
        """Converts the given value from slider space to real space."""

        if self.__realRange == 0:
            return 0

        value = self.__realMin + (value - self.__sliderMin) * \
            (float(self.__realRange) / self.__sliderRange)

        if self.__integer: return int(round(value))
        else:              return value


    def __realToSlider(self, value):
        """Converts the given value from real space to slider space."""

        if self.__integer:
            value = int(round(value))

        if self.__realRange == 0:
            return 0

        value = self.__sliderMin + (value - self.__realMin) * \
            (self.__sliderRange / float(self.__realRange))
        return int(round(value))


    def SetValue(self, value):
        """Set the slider value. Returns ``True`` if the value changed,
        ``False`` otherwise.
        """

        svalue   = self.__realToSlider(value)
        oldValue = self.GetValue()

        if svalue < self.__sliderMin: svalue = self.__sliderMin
        if svalue > self.__sliderMax: svalue = self.__sliderMax

        self.__slider.SetValue(svalue)
        self.__lastSliderValue = svalue

        return not np.isclose(value, oldValue)


    def GetValue(self):
        """Returns the slider value."""
        value = self.__slider.GetValue()
        return self.__sliderToReal(value)


class SliderSpinPanel(wx.Panel):
    """A panel containing a :class:`FloatSlider` and a :class:`.FloatSpinCtrl`.

    The slider and spinbox are linked such that changes to one are reflected
    in the other.  The ``SliderSpinPanel`` class also provides the option to
    have the minimum/maximum limits displayed on either side of the
    slider/spinbox, and to have those limits editable via a
    :class:`.NumberDialog` .

    Users of the ``SliderSpinPanel`` may wish to bind listeners to
    the following events:

      - :data:`EVT_SSP_VALUE`: Emitted when the slider value changes.

      - :data:`EVT_SSP_LIMIT`: Emitted when the slider limits change.
    """

    def __init__(self,
                 parent,
                 value=None,
                 minValue=None,
                 maxValue=None,
                 label=None,
                 style=None,
                 spinWidth=None):
        """Create a ``SliderSpinPanel``.

        The following style flags are available:

         .. autosummary::
            SSP_SHOW_LIMITS
            SSP_EDIT_LIMITS
            SSP_MOUSEWHEEL
            SSP_INTEGER

        :arg parent:   A parent control.

        :arg value:    Initial slider/spin value.

        :arg minValue: Minimum slider/spin value.

        :arg maxValue: Maximum slider/spin value.

        :arg label:    If not ``None``, a :class:`wx.StaticText`
                       widget is added to the left of the slider,
                       containing the given label.

        :arg style:    A combination of :data:`SSP_SHOW_LIMITS`,
                       :data:`SSP_EDIT_LIMITS`, :data:`SSP_NO_LIMITS`,
                       :data:`SSP_MOUSEWHEEL` and
                       :data:`SSP_INTEGER`. Defaults to
                       :data:`SSP_SHOW_LIMITS`.

        :arg spinWidth: Desired spin control width in characters. See the
                        :class:`.FloatSpinCtrl` class.
        """

        wx.Panel.__init__(self, parent, style=0)

        if style is None: style = SSP_SHOW_LIMITS

        showLimits = style & SSP_SHOW_LIMITS
        editLimits = style & SSP_EDIT_LIMITS
        noLimits   = style & SSP_NO_LIMITS
        integer    = style & SSP_INTEGER
        mousewheel = style & SSP_MOUSEWHEEL

        if value    is None: value    = 0
        if minValue is None: minValue = 0
        if maxValue is None: maxValue = 1

        if not showLimits:
            editLimits = False

        self.__showLimits = showLimits

        if integer: self.__fmt = '{}'
        else:       self.__fmt = '{: 0.3G}'

        spinStyle   = 0
        sliderStyle = 0

        if noLimits:
            spinStyle |= floatspin.FSC_NO_LIMIT

        if mousewheel:
            spinStyle   |= floatspin.FSC_MOUSEWHEEL
            sliderStyle |=            FS_MOUSEWHEEL

        if integer:
            spinStyle   |= floatspin.FSC_INTEGER
            sliderStyle |=            FS_INTEGER
            increment    = 1
        else:
            increment    = (maxValue - minValue) / 100.0

        self.__slider = FloatSlider(
            self,
            value=value,
            minValue=minValue,
            maxValue=maxValue,
            style=sliderStyle)

        self.__spinbox = floatspin.FloatSpinCtrl(
            self,
            value=value,
            minValue=minValue,
            maxValue=maxValue,
            increment=increment,
            style=spinStyle,
            width=spinWidth)

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        if label is not None:
            self.__label = wx.StaticText(self, label=label)
            self.__sizer.Add(self.__label, flag=wx.EXPAND)

        self.__sizer.Add(self.__slider,  flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__spinbox, flag=wx.EXPAND)

        self.__slider .Bind(wx.EVT_SLIDER,           self.__onSlider)
        self.__spinbox.Bind(floatspin.EVT_FLOATSPIN, self.__onSpin)

        if showLimits:
            self.__minButton = wx.Button(self,
                                         label=self.__fmt.format(minValue))
            self.__maxButton = wx.Button(self,
                                         label=self.__fmt.format(maxValue))

            self.__sizer.Insert(0, self.__minButton, flag=wx.EXPAND)
            self.__sizer.Add(      self.__maxButton, flag=wx.EXPAND)

            self.__minButton.Enable(editLimits)
            self.__maxButton.Enable(editLimits)

            self.__minButton.Bind(wx.EVT_BUTTON, self.__onLimitButton)
            self.__maxButton.Bind(wx.EVT_BUTTON, self.__onLimitButton)

        self.Layout()


    @property
    def slider(self):
        """Returts a reference to the ``FloatSlider`` contained in this
        ``SliderSpinPanel``.
        """
        return self.__slider


    @property
    def spinCtrl(self):
        """Returts a reference to the ``FloatSpinCtrl`` contained in this
        ``SliderSpinPanel``.
        """
        return self.__spinbox


    def __onLimitButton(self, ev):
        """Only called if the :data:`SSP_SHOW_LIMITS` and
        :data:`SSP_EDIT_LIMITS` style flags are set.

        Called when either of the minimum/maximum limit buttons are clicked.

        Pops up a :class:`.NumberDialog` window. If the user changes the limit
        value, updates the slider/spin limits, and emits an
        :data:`EVT_SSP_LIMIT` event.
        """

        source = ev.GetEventObject()

        if source == self.__minButton:
            message = 'New minimum value'
            initVal = self.GetMin()
            minVal  = None
            maxVal  = self.GetMax()
        elif source == self.__maxButton:
            message = 'New maximum value'
            initVal = self.GetMax()
            minVal  = self.GetMin()
            maxVal  = None
        else:
            return

        dlg = numberdialog.NumberDialog(
            self.GetTopLevelParent(),
            message=message,
            initial=initVal,
            minValue=minVal,
            maxValue=maxVal)

        pos = ev.GetEventObject().GetScreenPosition()
        dlg.SetPosition(pos)
        if dlg.ShowModal() != wx.ID_OK:
            return

        # The NumberDialog should not return
        # an invalid value, but just in case,
        # we absorb any ValueErrors that are
        # raised.
        try:
            if   source == self.__minButton: self.SetMin(dlg.GetValue())
            elif source == self.__maxButton: self.SetMax(dlg.GetValue())
        except ValueError:
            return

        wx.PostEvent(self, SliderSpinLimitEvent(
            min=self.GetMin(),
            max=self.GetMax()))


    def __onSlider(self, ev):
        """Called when the user changes the slider value.

        Updates the spinbox value and emits an :data:`EVT_SSP_VALUE` event.
        """
        val = self.__slider.GetValue()
        self.__spinbox.SetValue(val)
        wx.PostEvent(self, SliderSpinValueEvent(value=val))


    def __onSpin(self, ev):
        """Called when the user changes the spinbox value.

        Updates the slider value and emits an :data:`EVT_SSP_VALUE` event.
        """
        val = self.__spinbox.GetValue()
        self.__slider.SetValue(val)
        wx.PostEvent(self, SliderSpinValueEvent(value=val))


    def GetRange(self):
        """Return a tuple containing the (minimum, maximum) slider/spinbox
        values.
        """
        return self.__slider.GetRange()


    def GetMin(self):
        """Returns the minimum slider/spinbox value."""
        return self.__slider.GetMin()


    def GetMax(self):
        """Returns the maximum slider/spinbox value."""
        return self.__slider.GetMax()


    def GetValue(self):
        """Returns the current slider/spinbox value. """

        # If SSP_NO_LIMITS is set, the slider might
        # return a value limited to the min/max, but
        # the spinbox will return an unlimited value.
        return self.__spinbox.GetValue()


    def SetRange(self, minValue, maxValue):
        """Sets the minimum/maximum slider/spinbox values."""
        self.__slider .SetRange(minValue, maxValue)
        self.__spinbox.SetRange(minValue, maxValue)

        if self.__showLimits:
            self.__minButton.SetLabel(self.__fmt.format(minValue))
            self.__maxButton.SetLabel(self.__fmt.format(maxValue))


    def SetMin(self, minValue):
        """Sets the minimum slider/spinbox value."""
        self.SetRange(minValue, self.GetMax())


    def SetMax(self, maxValue):
        """Sets the maximum slider/spinbox value."""
        self.SetRange(self.GetMin(), maxValue)


    def SetValue(self, value):
        """Sets the current slider/spinbox value."""
        self.__slider .SetValue(value)
        self.__spinbox.SetValue(value)


FS_MOUSEWHEEL = 1
"""If set, mouse wheel events on the slider will change the value. """


FS_INTEGER = 2
"""If set, the slider will store an integer value instead of a floating point
value.
"""


_SliderSpinValueEvent, _EVT_SSP_VALUE = wxevent.NewEvent()
_SliderSpinLimitEvent, _EVT_SSP_LIMIT = wxevent.NewEvent()


EVT_SSP_VALUE        = _EVT_SSP_VALUE
"""Identifier for the :data:`SliderSpinValueEvent`."""


EVT_SSP_LIMIT        = _EVT_SSP_LIMIT
"""Identifier for the :data:`SliderSpinLimitEvent`."""


SliderSpinValueEvent = _SliderSpinValueEvent
"""Event emitted when the :class:`SliderSpinPanel` value
changes. Contains a single attribute, ``value``, which
contains the new value.
"""


SliderSpinLimitEvent = _SliderSpinLimitEvent
"""Event emitted when the :class:`SliderSpinPanel` limits
change. Contains two attributes, ``min`` and ``max``, which
contain the new limit values.
"""


SSP_SHOW_LIMITS = 1
"""If set, the data range limits are shown alongside the slider/spin control
widgets.
"""


SSP_EDIT_LIMITS = 2
"""If set, and :data:`SSP_SHOW_LIMITS` is also set, the data range limits
are shown on buttons alongside the slider/spin control widgets.

When the user pushes the button, a :class:`.NumberDialog` is shown, allowing
the user to change the data range.
"""

SSP_MOUSEWHEEL = 4
"""If set, mouse wheel events on the slider/spin controls will change the
value.
"""


SSP_INTEGER = 8
"""If set, the ``SliderSpinPanel`` will store an integer value instead of
floating point value.
"""


SSP_NO_LIMITS = 16
"""If set, the user is able to enter values outside of the range into the
spin controls.
"""
