#!/usr/bin/env python
#
# widgets.py - Generate wx GUI widgets for props.PropertyBase objects.
#
# The sole entry point for this module is the makeWidget function,
# which is called via the build module when it automatically
# builds a GUI for the properties of a props.HasProperties instance.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import sys

import os
import os.path as op

import logging

from collections import OrderedDict
from collections import Iterable

import wx

# the List property is complex enough to get its own module.
from widgets_list import _List

import properties as props


def _propBind(hasProps, propObj, propVal, guiObj, evType, labelMap=None):
    """
    Sets up event callback functions such that, on a change to the given
    property value, the value displayed by the given GUI widget will be
    updated. Similarly, whenever a GUI event of the specified type (or
    types) occurs, the property value will be set to the value controlled
    by the GUI widget. 

    If labelMap is provided, it should be a dictionary of value->label pairs
    where the label is what is displayed to the user, and the value is what is
    assigned to the property value when a corresponding label is selected. It
    is basically here to support Choice properties
    """

    if not isinstance(evType, Iterable): evType = [evType]

    listenerName = 'propBind_{}'.format(id(guiObj))
    valMap       = None

    if labelMap is not None:
        valMap = dict([(lbl,val) for (val,lbl) in labelMap.items()])

    def _guiUpdate(value, *a):
        """
        Called whenever the property value is changed.
        Sets the GUI widget value to that of the property.
        """

        if guiObj.GetValue() == value: return

        if valMap is not None: guiObj.SetValue(labelMap[value])
        else:                  guiObj.SetValue(value)
        
    def _propUpdate(*a):
        """
        Called when the value controlled by the GUI widget
        is changed. Updates the property value.
        """

        # TODO remove property value listener when GUI object is destroyed
        try:
            value = guiObj.GetValue()
        except:
            raise

        if propVal.get() == value: return

        if labelMap is not None: propVal.set(valMap[value])
        else:                    propVal.set(value)

    guiObj.SetValue(propVal.get())

    # set up the callback functions
    for ev in evType: guiObj.Bind(ev, _propUpdate)
    propVal.addListener(listenerName, _guiUpdate)


def _setupValidation(widget, hasProps, propObj, propVal):
    """
    Configures input validation for the given widget, which is assumed
    to be managing the given prop (props.PropertyBase) object.  Any
    changes to the property value are validated and, if the new value
    is invalid, the widget background colour is changed to a light
    red, so that the user is aware of the invalid-ness.
    """

    invalidBGColour = '#ff9999'
    validBGColour   = widget.GetBackgroundColour()

    def _changeBGOnValidate(value, valid, instance, *a):
        """
        Called whenever the property value changes. Checks
        to see if the new value is valid and changes the
        widget background colour according to the validity
        of the new value.
        """
        
        if valid: newBGColour = validBGColour
        else:     newBGColour = invalidBGColour
        
        widget.SetBackgroundColour(newBGColour)
        widget.Refresh()

    # We add a callback listener to the PropertyValue object,
    # rather than to the PropertyBase, as one property may be
    # associated with multiple variables, and we don't want
    # the widgets associated with those other variables to
    # change background.
    propVal.addListener('changeBGOnValidate', _changeBGOnValidate)

    # Validate the initial property value,
    # so the background is appropriately set
    _changeBGOnValidate(None, propVal.isValid(), None)
    

# The _lastFilePathDir variable is used to retain the
# most recentlyvisited directory in file dialogs. New
# file dialogs are initialised to display this
# directory.
#
# This is currently a global setting, but it may be
# more appropriate to make it a per-widget setting.
# Easily done, just make this a dict, with the widget
# (or property name) as the key.
_lastFilePathDir = None
def _FilePath(parent, hasProps, propObj, propVal):
    """
    Creates and returns a panel containing a text field and a
    Button. The button, when clicked, opens a file dialog
    allowing the user to choose a file/directory to open, or
    a location to save (this depends upon how the propObj
    [props.FilePath] object was configured).
    """

    global _lastFilePathDir
    if _lastFilePathDir is None:
        _lastFilePathDir = os.getcwd()

    value = propVal.get()
    if value is None: value = ''

    panel   = wx.Panel(parent)
    textbox = wx.TextCtrl(panel)
    button  = wx.Button(panel)
    
    def _choosePath():
        global _lastFilePathDir

        if propObj.exists and propObj.isFile:
            dlg = wx.FileDialog(parent,
                                message='Choose file',
                                defaultDir=_lastFilePathDir,
                                defaultFile=value,
                                style=wx.FD_OPEN)
            
        elif propObj.exists and (not propObj.isFile):
            dlg = wx.DirDialog(parent,
                               message='Choose directory',
                               defaultPath=_lastFilePathDir) 

        else:
            dlg = wx.FileDialog(parent,
                                message='Save file',
                                defaultDir=_lastFilePathDir,
                                defaultFile=value,
                                style=wx.FD_SAVE)


        dlg.ShowModal()
        path = dlg.GetPath()
        
        if path != '' and path is not None:
            _lastFilePathDir = op.dirname(path)
            propVal.set(path)
            
    _setupValidation(textbox, hasProps, propObj, propVal)
    _propBind(hasProps, propObj, propVal, textbox, wx.EVT_TEXT)

    button.Bind(wx.EVT_BUTTON, _choosePath)
    
    return panel
    

def _Choice(parent, hasProps, propObj, propVal):
    """
    Creates and returns a ttk Combobox allowing the
    user to set the given propObj (props.Choice) object.
    """

    choices = propObj.choices
    labels  = propObj.choiceLabels
    
    valMap  = OrderedDict(zip(choices, labels))

    widget  = wx.ComboBox(
        parent,
        choices=labels,
        style=wx.CB_READONLY | wx.CB_DROPDOWN)

    _propBind(hasProps, propObj, propVal, widget, wx.EVT_COMBOBOX, valMap)
    
    return widget


def _String(parent, hasProps, propObj, propVal):
    """
    Creates and returns a ttk Entry object, allowing
    the user to edit the given propObj (props.String)
    object.
    """

    widget = wx.TextCtrl(parent)

    _propBind(hasProps, propObj, propVal, widget, wx.EVT_TEXT)
    _setupValidation(widget, hasProps, propObj, propVal)
    
    return widget


def _Number(parent, hasProps, propObj, propVal):
    """
    Creates and returns a widget allowing the user to edit
    the given property (a props.Int or props.Double).
    """

    value   = propVal.get()
    minval  = propObj.minval
    maxval  = propObj.maxval

    if   isinstance(propObj, props.Int):    SpinCtr = wx.SpinCtrl
    elif isinstance(propObj, props.Double): SpinCtr = wx.SpinCtrlDouble
        
    else:
        raise TypeError('Unrecognised property type: {}'.format(
            propObj.__class__.__name__))

    makeSlider = (minval is not None) and (maxval is not None)

    if   isinstance(propObj, props.Int):    increment = None
    elif isinstance(propObj, props.Double):
        if makeSlider: increment = (maxval-minval)/20.0
        else:          increment = 0.5

    params = {}
    if increment is not None: params['inc']     = increment
    if minval    is not None: params['min']     = minval
    if maxval    is not None: params['max']     = maxval
    if value     is not None: params['initial'] = value

    # The minval and maxval attributes have not both
    # been set, so we create a spinbox instead of a slider.
    if not makeSlider:

        widget = SpinCtr(parent, **params)
        
        _propBind(hasProps, propObj, propVal, widget,
                  [wx.EVT_SPINCTRL, wx.EVT_TEXT])
        _setupValidation(widget, hasProps, propObj, propVal)

    # if both minval and maxval have been set, we can use
    # a slider. We also add a spinbox for manual entry, and
    # some labels to show the min/max/current slider value.
    else:

        panel = wx.Panel(parent)

        slider = wx.Slider(
            panel,
            value=value,
            minValue=minval,
            maxValue=maxval)

        spin = SpinCtr(panel, **params)

        minLabel = wx.StaticText(panel, label='{}'.format(minval))
        curLabel = wx.StaticText(panel, label='{}'.format(value))
        maxLabel = wx.StaticText(panel, label='{}'.format(maxval))

        sizer = wx.GridBagSizer()
        panel.SetSizer(sizer)
        
        sizer.Add(slider,   pos=(0,0), span=(1,3), flag=wx.EXPAND)
        sizer.Add(spin,     pos=(0,3), span=(2,1), flag=wx.EXPAND)
        sizer.Add(minLabel, pos=(1,0), span=(1,1), flag=wx.ALIGN_LEFT)
        sizer.Add(curLabel, pos=(1,1), span=(1,1), flag=wx.ALIGN_CENTER)
        sizer.Add(maxLabel, pos=(1,2), span=(1,1), flag=wx.ALIGN_RIGHT)

        sizer.AddGrowableCol(0)
        sizer.Layout()

        # TODO how do I remove this listener when the widget is destroyed?
        def _updateCurLabel(value, *a):
            curLabel.SetLabel('{}'.format(value))
        listenerName = 'sliderLabel'

        propVal.addListener(listenerName, _updateCurLabel)
        _propBind(hasProps, propObj, propVal, slider,   wx.EVT_SLIDER)
        _propBind(hasProps, propObj, propVal, spin,     wx.EVT_SPINCTRL)
        
        _setupValidation(spin, hasProps, propObj, propVal)

        widget = panel

    return widget


def _Double(parent, hasProps, propObj, propVal):
    return _Number(parent, hasProps, propObj, propVal)


def _Int(parent, hasProps, propObj, propVal):
    return _Number(parent, hasProps, propObj, propVal)


def _Percentage(parent, hasProps, propObj, propVal):
    # TODO Add '%' signs to Scale labels.
    return _Number(parent, hasProps, propObj, propVal) 
        

def _Boolean(parent, hasProps, propObj, propVal):
    """
    Creates and returns a check box, allowing the user
    to set the given propObj (props.Boolean) object.
    """

    checkBox = wx.CheckBox(parent)
    _propBind(hasProps, propObj, propVal, checkBox, wx.EVT_CHECKBOX)
    return checkBox


def makeWidget(parent, hasProps, propName):
    """
    Given hasProps (a props.HasProperties object), propName (the name
    of a property of hasProps), and parent GUI object, creates and
    returns a widget, or a frame containing widgets, which may be
    used to edit the property.
    """

    propObj = hasProps.getProp(propName)
    propVal = propObj.getPropVal(hasProps)

    if propObj is None:
        raise ValueError('Could not find property {}.{}'.format(
            hasProps.__class__.__name__, propName))

    makeFunc = getattr(
        sys.modules[__name__],
        '_{}'.format(propObj.__class__.__name__), None)

    if makeFunc is None:
        raise ValueError(
            'Unknown property type: {}'.format(propObj.__class__.__name__))

    return makeFunc(parent, hasProps, propObj, propVal)
