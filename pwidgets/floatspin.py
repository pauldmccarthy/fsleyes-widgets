#!/usr/bin/env python
#
# floatspin.py - Alternate implementation to wx.SpinCtrlDouble and
#                wx.lib.agw.floatspin.FloatSpin.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""An alternative to :class:`wx.SpinCtrl`, :class:`wx.SpinCtrlDouble`, and
:class:`wx.lib.agw.floatspin.FloatSpin`.

 - :class:`wx.SpinCtrlDouble`: Under Linux/GTK, this widget does not allow the
   user to enter values that are not a multiple of the increment.

 - :class:`wx.lib.agw.floatspin.FloatSpin`. Differs from the
   :class:`wx.SpinCtrl` API in various annoying ways, and formatting is a
   pain.
"""


import                    wx
import wx.lib.newevent as wxevent

import re


_FloatSpinEvent, _EVT_FLOATSPIN = wxevent.NewEvent()


EVT_FLOATSPIN = _EVT_FLOATSPIN


FloatSpinEvent = _FloatSpinEvent


FSC_MOUSEWHEEL          = 1
FSC_EVENT_ON_TEXT       = 2
FSC_INTEGER             = 4


# TODO Add these styles if/when you need them:
#      FSC_NO_SPIN_BUTTON      = 8
#      FSC_IGNORE_OUT_OF_RANGE = 16


class FloatSpinCtrl(wx.PyPanel):

    def __init__(self,
                 parent,
                 minValue=0,
                 maxValue=100,
                 increment=1,
                 value=0,
                 style=0):
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

        self.SetRange(minValue, maxValue)
        self.SetValue(value)
        self.SetIncrement(increment)

    
    def GetValue(self):
        return self.__value
    

    def GetMin(self):
        return self.__realMin

    
    def GetMax(self):
        return self.__realMax


    def GetIncrement(self):
        return self.__increment


    def SetIncrement(self, inc):
        if self.__integer: self.__increment = int(round(inc))
        else:              self.__increment =           inc

        
    def GetRange(self):
        return (self.__realMin, self.__realMax)


    def SetMin(self, minval):
        self.SetRange(minval, self.__realMax)

    
    def SetMax(self, maxval):
        self.SetRange(self.__realMin, maxval)

    
    def SetRange(self, minval, maxval):
        
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
        """
        Returns ``True`` if the value was changed,
        ``False`` otherwise.
        """

        if self.__integer:
            value = int(round(value))

        if value < self.__realMin: value = self.__realMin
        if value > self.__realMax: value = self.__realMax

        oldValue     = self.__value
        self.__value = value

        self.__text.ChangeValue(self.__format.format(value))
        self.__spin.SetValue(   self.__realToSpin(value))

        return value != oldValue
    

    def __onText(self, ev):

        val = self.__text.GetValue().strip()

        if self.__textPattern.match(val) is None:
            self.SetValue(self.__value)
            return

        try:
            if self.__integer: val = int(  val)
            else:              val = float(val)
        except:
            self.SetValue(self.__value)
            return

        if self.SetValue(val):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value)) 


    def __onSpinDown(self, ev=None):
        if self.SetValue(self.__value - self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))

        
    def __onSpinUp(self, ev=None):
        if self.SetValue(self.__value + self.__increment):
            wx.PostEvent(self, FloatSpinEvent(value=self.__value))


    def __onMouseWheel(self, ev):

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
