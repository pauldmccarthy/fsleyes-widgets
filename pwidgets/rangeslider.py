#!/usr/bin/env python
#
# rangeslider.py - Twin sliders for defining the values of a range.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`RangePanel` and
:class:`RangeSliderSpinPanel` classes, both of which contain controls allowing
the user to modify a range.

The :class:`RangeSliderSpinPanel` is a widget which contains two
:class:`RangePanel` widgets - one with sliders, and one with spinboxes. All
four control widgets are linked.

"""


import logging

import wx
import wx.lib.newevent as wxevent

import floatspin
import floatslider
import numberdialog


log = logging.getLogger(__name__)


class RangePanel(wx.PyPanel):
    """``RangePanel`` is a widget which contains two sliders or spinboxes (either
    :class:`.FloatSlider`, or :class:`.FloatSpinCtrl`), allowing a range to be
    set.

    
    When the user changes the low range value to a value beyond the current
    high value, the high value is increased such that it remains at least a
    minimum value above the low value. The inverse relationship is also
    enforced. Whenever the user chenges the *low* or *high* range values,
    :data:`EVT_LOW_RANGE` or :data:`EVT_HIGH_RANGE`  events are generated
    respectively. 
    

    The following style flags are available:

      .. autosummary::
         RP_INTEGER
         RP_MOUSEWHEEL
         RP_SLIDER
    """ 

    def __init__(self,
                 parent,
                 minValue=None,
                 maxValue=None,
                 lowValue=None,
                 highValue=None,
                 lowLabel=None,
                 highLabel=None,
                 minDistance=None,
                 style=0):
        """Create a :class:`RangePanel`.
        
        :arg parent:      The :mod:`wx` parent object.

        :arg minValue:    Minimum range value.
        
        :arg maxValue:    Maximum range value.

        :arg lowLabel:    If not ``None``, a :class:`wx.StaticText` 
                          widget is placed to the left of the low 
                          widget, containing the given label.

        :arg highLabel:   If not ``None``, a :class:`wx.StaticText` 
                          widget is placed to the left of the high 
                          widget, containing the given label.

        :arg lowValue:    Initial low range value.
        
        :arg highValue:   Initial high range value.
        
        :arg minDistance: Minimum distance to be maintained between
                          low/high values.

        :arg style:       A combination of :data:`RP_MOUSEWHEEL`,
                          :data:`RP_INTEGER`, and :data:`RP_SLIDER`.
        """

        if style & RP_SLIDER: widgetType = 'slider'
        else:                 widgetType = 'spin'

        wx.PyPanel.__init__(self, parent)

        if minValue    is None: minValue    = 0
        if maxValue    is None: maxValue    = 100
        if lowValue    is None: lowValue    = 0
        if highValue   is None: highValue   = 100
        if minDistance is None: minDistance = 0

        self.__minDistance = minDistance

        if widgetType == 'slider':

            if style & RP_MOUSEWHEEL: widgStyle = floatslider.FS_MOUSEWHEEL
            else:                     widgStyle = 0
            
            if style & RP_INTEGER:
                widgStyle |= floatslider.FS_INTEGER
                
            self.__lowWidget  = floatslider.FloatSlider(self, style=widgStyle)
            self.__highWidget = floatslider.FloatSlider(self, style=widgStyle)
            
            self.__lowWidget .Bind(wx.EVT_SLIDER, self.__onLowChange)
            self.__highWidget.Bind(wx.EVT_SLIDER, self.__onHighChange)
            
        elif widgetType == 'spin':

            if style & RP_MOUSEWHEEL: widgStyle = floatspin.FSC_MOUSEWHEEL
            else:                     widgStyle = 0
            
            if style & RP_INTEGER:
                widgStyle |= floatspin.FSC_INTEGER
            
            self.__lowWidget  = floatspin.FloatSpinCtrl(self, style=widgStyle)
            self.__highWidget = floatspin.FloatSpinCtrl(self, style=widgStyle)

            self.__lowWidget .Bind(floatspin.EVT_FLOATSPIN,
                                   self.__onLowChange)
            self.__highWidget.Bind(floatspin.EVT_FLOATSPIN,
                                   self.__onHighChange)

        # Widgets under Linux/GTK absorb mouse
        # wheel events, so we bind a handler
        # to prevent this.
        if not (style & RP_MOUSEWHEEL) and wx.Platform == '__WXGTK__':
            def wheel(ev):
                self.GetParent().GetEventHandler().ProcessEvent(ev)
            self.Bind(wx.EVT_MOUSEWHEEL, wheel)

        self.__sizer = wx.GridBagSizer(1, 1)
        self.__sizer.SetEmptyCellSize((0, 0))
        
        self.SetSizer(self.__sizer)

        self.__sizer.Add(self.__lowWidget,
                         pos=(0, 1),
                         flag=wx.EXPAND | wx.ALL)
        self.__sizer.Add(self.__highWidget,
                         pos=(1, 1),
                         flag=wx.EXPAND | wx.ALL)

        if lowLabel is not None:
            self.__lowLabel = wx.StaticText(self, label=lowLabel)
            self.__sizer.Add(self.__lowLabel,
                             pos=(0, 0),
                             flag=wx.EXPAND | wx.ALL)

        if highLabel is not None:
            self.__highLabel = wx.StaticText(self, label=highLabel)
            self.__sizer.Add(self.__highLabel,
                             pos=(1, 0),
                             flag=wx.EXPAND | wx.ALL) 

        self.SetLimits(minValue, maxValue)
        self.SetRange( lowValue, highValue)
        
        self.__sizer.AddGrowableCol(1)

        self.Layout()


    def __onLowChange(self, ev=None):
        """Called when the user changes the low widget.

        Attempts to make sure that the high widget is at least (low value +
        min distance), then posts a :data:`RangeEvent`.
        """

        lowValue  = self.GetLow()
        highValue = self.GetHigh()

        if lowValue >= (self.GetMax() - self.__minDistance):
            self.SetLow(self.GetMax() - self.__minDistance)
            lowValue = self.GetLow()

        if highValue <= (lowValue + self.__minDistance):
            highValue = lowValue + self.__minDistance
            self.SetHigh(highValue)
            highValue = self.GetHigh()

        log.debug('Low range value changed - posting events: '
                  '[{} - {}]'.format(lowValue, highValue))

        ev = LowRangeEvent(low=lowValue)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)

            
    def __onHighChange(self, ev=None):
        """Called when the user changes the high widget.

        Attempts to make sure that the low widget is at least (high value -
        min distance), then posts a :data:`RangeEvent`.
        """ 

        lowValue  = self.GetLow()
        highValue = self.GetHigh()

        if highValue <= (self.GetMin() + self.__minDistance):
            self.SetHigh(self.GetMin() + self.__minDistance)
            highValue = self.GetHigh() 

        if lowValue >= (highValue - self.__minDistance):
            lowValue = highValue - self.__minDistance
            self.SetLow(lowValue)
            lowValue = self.GetLow()

        log.debug('High range value changed - posting events: '
                  '[{} - {}]'.format(lowValue, highValue))

        ev = HighRangeEvent(high=highValue)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)

        
    def GetRange(self):
        """Returns a tuple containing the current (low, high) range values."""
        return (self.GetLow(), self.GetHigh())

        
    def SetRange(self, lowValue, highValue):
        """Sets the current (low, high) range values.""" 
        self.SetLow( lowValue)
        self.SetHigh(highValue)

        
    def GetLow(self):
        """Returns the current low range value."""
        return self.__lowWidget.GetValue()

        
    def GetHigh(self):
        """Returns the current high range value.""" 
        return self.__highWidget.GetValue()

        
    def SetLow(self, lowValue):
        """Set the current low range value, and attempts to make sure
        that the high value is at least (low value + min distance).
        """
        self.__lowWidget.SetValue(lowValue)

        highValue = self.GetHigh()
        if highValue <= lowValue + self.__minDistance:
            self.__highWidget.SetValue(lowValue + self.__minDistance)

        
    def SetHigh(self, highValue):
        """Set the current high range value, and attempts to make sure
        that the high value is at least (low value + min distance).
        """ 
        self.__highWidget.SetValue(highValue)
        
        lowValue = self.GetLow()
        if lowValue >= highValue - self.__minDistance:
            self.__lowWidget.SetValue(highValue - self.__minDistance)


    def GetLimits(self):
        """Returns a tuple containing the current (minimum, maximum) range
        limit values.
        """
        return (self.GetMin(), self.GetMax())

        
    def SetLimits(self, minValue, maxValue):
        """Sets the current (minimum, maximum) range limit values.""" 
        self.SetMin(minValue)
        self.SetMax(maxValue)


    def GetMin(self):
        """Returns the current minimum range value."""
        return self.__lowWidget.GetMin()

        
    def GetMax(self):
        """Returns the current maximum range value.""" 
        return self.__highWidget.GetMax()

        
    def SetMin(self, minValue):
        """Sets the current minimum range value."""

        self.__lowWidget .SetMin(minValue)
        self.__highWidget.SetMin(minValue)

        
    def SetMax(self, maxValue):
        """Sets the current maximum range value."""
        self.__lowWidget .SetMax(maxValue)
        self.__highWidget.SetMax(maxValue)


class RangeSliderSpinPanel(wx.PyPanel):
    """A :class:`wx.Panel` which contains two sliders and two spinboxes.

    
    The sliders and spinboxes are contained within two :class:`RangePanel`
    instances respectively. One slider and spinbox pair is used to edit the
    *low* value of a range, and the other slider/spinbox used to edit the
    *high* range value. Buttons are optionally displayed on either end
    which display the minimum/maximum limits and, when clicked, allow the
    user to modify said limits.

    
    The ``RangeSliderSpinPanel`` generates a :data:`RangeEvent` when the
    user edits the *low*/*high* range values,  and a :data:`RangeLimitEvent`
    when the user edits the range limits.

    
    The following style flags are available:

     .. autosummary::
        RSSP_INTEGER
        RSSP_MOUSEWHEEL
        RSSP_SHOW_LIMITS
        RSSP_EDIT_LIMITS


    A ``RangeSliderSpinPanel`` will look something like this:

     .. image:: images/rangesliderspinpanel.png
        :scale: 50%
        :align: center
    """

    
    def __init__(self,
                 parent,
                 minValue=None,
                 maxValue=None,
                 lowValue=None,
                 highValue=None,
                 minDistance=None,
                 lowLabel=None,
                 highLabel=None,
                 style=None):
        """Create a :class:`RangeSliderSpinPanel`.
        
        :arg parent:      The :mod:`wx` parent object.
        
        :arg minValue:    Minimum low value.
        
        :arg maxValue:    Maximum high value.
        
        :arg lowValue:    Initial low value.
        
        :arg highValue:   Initial high value.
        
        :arg minDistance: Minimum distance to maintain between low and high
                          values.

        :arg lowLabel:    If not ``None``, a :class:`wx.StaticText` widget is
                          placed to the left of the low slider, containing the
                          label.

        :arg highLabel:   If not ``None``, a :class:`wx.StaticText` widget is
                          placed to the left of the high slider, containing
                          the label.

        :arg style:       A combination of :data:`RSSP_INTEGER`,
                          :data:`RSSP_MOUSEWHEEL`, :data:`RSSP_SHOW_LIMITS`,
                          and :data:`RSSP_EDIT_LIMITS`. Defaults to
                          :data:`RSSP_SHOW_LIMITS`.
        """

        if style is None:
            style = RSSP_SHOW_LIMITS

        showLimits =     style & RSSP_SHOW_LIMITS
        editLimits =     style & RSSP_EDIT_LIMITS
        mousewheel =     style & RSSP_MOUSEWHEEL
        real       = not style & RSSP_INTEGER

        wx.PyPanel.__init__(self, parent)

        if minValue    is None: minValue    = 0
        if maxValue    is None: maxValue    = 1
        if lowValue    is None: lowValue    = 0
        if highValue   is None: highValue   = 1
        if minDistance is None: minDistance = 0.01 
        
        if not showLimits:
            editLimits = False
        
        self.__showLimits = showLimits

        if real: self.__fmt = '{: 0.3G}'
        else:    self.__fmt = '{}'

        params = {
            'minValue'    : minValue,
            'maxValue'    : maxValue,
            'lowValue'    : lowValue,
            'highValue'   : highValue,
            'minDistance' : minDistance,
        }

        style = 0

        if mousewheel: style |= RP_MOUSEWHEEL
        if not real:   style |= RP_INTEGER
        
        self.__sliderPanel = RangePanel(
            self,
            lowLabel=lowLabel,
            highLabel=highLabel,
            style=style | RP_SLIDER,
            **params)
        self.__spinPanel = RangePanel(
            self,
            style=style,
            **params)
        
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        self.__sizer.Add(self.__sliderPanel, flag=wx.EXPAND, proportion=1)
        self.__sizer.Add(self.__spinPanel,   flag=wx.EXPAND)

        self.__sliderPanel.Bind(EVT_LOW_RANGE,  self.__onLowRangeChange)
        self.__spinPanel  .Bind(EVT_LOW_RANGE,  self.__onLowRangeChange)
        self.__sliderPanel.Bind(EVT_HIGH_RANGE, self.__onHighRangeChange)
        self.__spinPanel  .Bind(EVT_HIGH_RANGE, self.__onHighRangeChange) 

        if showLimits:
            self.__minButton = wx.Button(self)
            self.__maxButton = wx.Button(self)

            self.__sizer.Insert(0, self.__minButton, flag=wx.EXPAND | wx.ALL)
            self.__sizer.Add(      self.__maxButton, flag=wx.EXPAND | wx.ALL)

            self.__minButton.SetLabel(self.__fmt.format(minValue))
            self.__maxButton.SetLabel(self.__fmt.format(maxValue))

            self.__minButton.Enable(editLimits)
            self.__maxButton.Enable(editLimits)

            self.__minButton.Bind(wx.EVT_BUTTON, self.__onLimitButton)
            self.__maxButton.Bind(wx.EVT_BUTTON, self.__onLimitButton)

        # Widgets under Linux/GTK absorb mouse
        # wheel events, so we bind a handler
        # to prevent this.
        if not mousewheel and wx.Platform == '__WXGTK__':
            def wheel(ev):
                self.GetParent().GetEventHandler().ProcessEvent(ev)
            self.Bind(wx.EVT_MOUSEWHEEL, wheel)
            
        self.Layout()


    def __onLowRangeChange(self, ev):
        """Called when the slider or spin panel generates an
        :data:`EVT_LOW_RANGE` event. Calls the :meth:`__onRangeChange`
        method.
        """

        src = ev.GetEventObject()
        self.__onRangeChange(src, low=ev.low)

    
    def __onHighRangeChange(self, ev):
        """Called when the slider or spin panel generates an
        :data:`EVT_HIGH_RANGE` event. Calls the :meth:`__onRangeChange`
        method.
        """ 
        src = ev.GetEventObject()
        self.__onRangeChange(src, high=ev.high)

        
    def __onRangeChange(self, source, low=None, high=None):
        """Called by :meth:`__onLowRangeChange` and :meth:`onHighRangeChange`.
        Syncs the change between the sliders and spinboxes, and emits
        a :data:`RangeEvent`.
        """

        slider = self.__sliderPanel
        spin   = self.__spinPanel

        # Get a reference to the panel
        # that needs to be synced.
        if   source is slider: slave = spin
        elif source is spin:   slave = slider

        if low is not None: slave.SetLow( low)
        else:               slave.SetHigh(high)

        lowValue, highValue = source.GetRange()

        log.debug('Range values changed - posting event: [{} - {}]'.format(
            lowValue, highValue))

        if low is not None: ev = LowRangeEvent( low=low)
        else:               ev = HighRangeEvent(high=high)

        rev = RangeEvent(low=lowValue, high=highValue)
        
        ev .SetEventObject(self)
        rev.SetEventObject(self)

        wx.PostEvent(self, ev)
        wx.PostEvent(self, rev)

            
    def __onLimitButton(self, ev):
        """Called when one of the min/max buttons is pushed. Pops up
        a dialog prompting the user to enter a new value, and updates
        the range limits accordingly. Emits a :data:`RangeLimitEvent`.
        """

        source = ev.GetEventObject()
        
        if source == self.__minButton:
            labeltxt = 'New minimum value'
            initVal  = self.GetMin()
            minVal   = None
            maxVal   = self.GetMax()
            
        elif source == self.__maxButton:
            labeltxt = 'New maximum value'
            initVal  = self.GetMax()
            minVal   = self.GetMin() 
            maxVal   = None
            
        else:
            return

        dlg = numberdialog.NumberDialog(
            self.GetTopLevelParent(),
            message=labeltxt,
            initial=initVal,
            minValue=minVal,
            maxValue=maxVal)

        pos = ev.GetEventObject().GetScreenPosition()
        dlg.SetPosition(pos)
        if dlg.ShowModal() != wx.ID_OK:
            return

        if   source == self.__minButton: self.SetMin(dlg.GetValue())
        elif source == self.__maxButton: self.SetMax(dlg.GetValue())

        ev = RangeLimitEvent(min=self.GetMin(), max=self.GetMax())
        ev.SetEventObject(self)

        wx.PostEvent(self, ev)

        
    def SetLimits(self, minValue, maxValue):
        """Sets the minimum/maximum range values."""
        self.SetMin(minValue)
        self.SetMax(maxValue)

        
    def SetMin(self, minValue):
        """Sets the minimum range value."""
        self.__sliderPanel.SetMin(minValue)
        self.__spinPanel  .SetMin(minValue)

        if self.__showLimits:
            self.__minButton.SetLabel(self.__fmt.format(minValue))

            
    def SetMax(self, maxValue):
        """Sets the maximum range value."""
        self.__sliderPanel.SetMax(maxValue)
        self.__spinPanel  .SetMax(maxValue)
        
        if self.__showLimits:
            self.__maxButton.SetLabel(self.__fmt.format(maxValue))

            
    def GetMin(self):
        """Returns the minimum range value."""
        return self.__sliderPanel.GetMin()

        
    def GetMax(self):
        """Returns the maximum range value.""" 
        return self.__sliderPanel.GetMax()

        
    def GetLow( self):
        """Returns the current low range value."""
        return self.__sliderPanel.GetLow()

        
    def GetHigh(self):
        """Returns the current high range value."""
        return self.__sliderPanel.GetHigh()

        
    def SetLow(self, lowValue):
        """Sets the current low range value."""
        self.__sliderPanel.SetLow(lowValue)
        self.__spinPanel  .SetLow(lowValue)

        
    def SetHigh(self, highValue):
        """Sets the current high range value.""" 
        self.__sliderPanel.SetHigh(highValue)
        self.__spinPanel  .SetHigh(highValue)


    def GetRange(self):
        """Return the current (low, high) range values."""
        return self.__sliderPanel.GetRange()


    def SetRange(self, lowValue, highValue):
        """Set the current low and high range values."""
        self.__sliderPanel.SetRange(lowValue, highValue)
        self.__spinPanel  .SetRange(lowValue, highValue)

        
RP_INTEGER = 1
"""If set, the :class:`RangePanel` stores integer values, rather than
floating point.
"""


RP_MOUSEWHEEL = 2
"""If set, the user will be able to change the range values with the mouse
wheel.
"""


RP_SLIDER = 4
"""If set, :class:`.FloatSlider` widgets will be used to control the range
values. If not set, :class:`.FloatSpinCtrl` widgets are used.
"""


RSSP_INTEGER = 1
"""If set, the :class:`RangeSliderSpinPanel` stores integer values, rather
than floating point.
"""


RSSP_MOUSEWHEEL = 2
"""If set, the user will be able to change the range values with the mouse
wheel.
"""


RSSP_SHOW_LIMITS = 4
"""If set, the minimum/maximum range values are shown alongside the range
controls.
"""


RSSP_EDIT_LIMITS = 8
"""If set, and :data:`RSSP_SHOW_LIMITS` is also set, the minimum/maximum
range values are shown alongside the range controls on buttons. When
the presses a button, a dialog is displayed allowing them to change the
range limits.
"""


_RangeEvent,      _EVT_RANGE       = wxevent.NewEvent()
_LowRangeEvent,   _EVT_LOW_RANGE   = wxevent.NewEvent()
_HighRangeEvent,  _EVT_HIGH_RANGE  = wxevent.NewEvent()
_RangeLimitEvent, _EVT_RANGE_LIMIT = wxevent.NewEvent()


EVT_RANGE = _EVT_RANGE
"""Identifier for the :data:`RangeEvent`."""


EVT_LOW_RANGE = _EVT_LOW_RANGE
"""Identifier for the :data:`LowRangeEvent`."""


EVT_HIGH_RANGE = _EVT_HIGH_RANGE
"""Identifier for the :data:`HighRangeEvent`."""


EVT_RANGE_LIMIT = _EVT_RANGE_LIMIT
"""Identifier for the :data:`RangeLimitEvent`."""


RangeEvent = _RangeEvent
"""Event emitted by :class:`RangePanel` and :class:`RangeSliderSpinPanel`
objects  when either of their low or high values change. Contains two
attributes, ``low`` and ``high``, containing the new low/high range values.
"""


LowRangeEvent = _LowRangeEvent
"""Event emitted by :class:`RangePanel` and :class:`RangeSliderSpinPanel`
objects when their low value changes. Contains one attributes, ``low``,
containing the new low range value.
"""


HighRangeEvent = _HighRangeEvent
"""Event emitted by :class:`RangePanel` and :class:`RangeSliderSpinPanel`
objects when their high value changes. Contains one attributes, ``high``,
containing the new high range value.
"""


RangeLimitEvent = _RangeLimitEvent
"""Event emitted by :class:`RangeSliderSpinPanel` objects when the user
modifies the range limits. Contains two attributes, ``min`` and ``max``,
containing the new minimum/maximum range limits.
"""
