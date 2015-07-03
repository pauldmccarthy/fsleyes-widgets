#!/usr/bin/env python
#
# propertylist.py - A widget which displays a list of widgets linked to
#                   HasProperties properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`PropertyList` class, which displays a
list of widgets which are linked to the properties of one or more
:class:`HasProperties` instances. The widgets can be grouped arbitrarily,
and widgets and groups can be dynamically added and removed.
"""

from collections import OrderedDict

import wx
import wx.lib.scrolledpanel as scrolledpanel

import props

class Property(object):
    """The ``Property`` class is used internally by :class:`PropertyList`
    instances to represent properties that are in the list.
    """
    def __init__(self,
                 hasProps,
                 propName,
                 displayName,
                 tooltip,
                 label,
                 widget,
                 sizer):
        self.hasProps    = hasProps
        self.propName    = propName
        self.displayName = displayName
        self.tooltip     = tooltip
        self.label       = label
        self.widget      = widget
        self.sizer       = sizer


class Widget(object):
    """
    """
    def __init__(self,
                 displayName,
                 tooltip,
                 label,
                 widget,
                 sizer):
        self.displayName = displayName
        self.tooltip     = tooltip
        self.label       = label
        self.widget      = widget
        self.sizer       = sizer    
        

class Group(object):
    """The ``Group`` class is used internally by :class:`PropertyList`
    instances to represent groups of properties that are in the list.
    """ 
    def __init__(self,
                 groupName,
                 displayName,
                 parentPanel,
                 colPanel,
                 propPanel,
                 sizer):
        self.groupName   = groupName
        self.displayName = displayName
        self.parentPanel = parentPanel
        self.colPanel    = colPanel
        self.propPanel   = propPanel
        self.sizer       = sizer
        self.props       = OrderedDict()


class PropertyList(scrolledpanel.ScrolledPanel):


    _defaultOddColour   = '#eaeaea'
    _defaultEvenColour  = '#ffffff'
    _defaultGroupColour = '#eaeaff'

    
    def __init__(self, parent):
        scrolledpanel.ScrolledPanel.__init__(self, parent)

        self.__sizer       = wx.BoxSizer(wx.VERTICAL)
        self.__propSizer   = wx.BoxSizer(wx.VERTICAL)
        self.__groupSizer  = wx.BoxSizer(wx.VERTICAL)
        self.__properties  = OrderedDict()
        self.__groups      = OrderedDict()

        self.__oddColour   = PropertyList._defaultOddColour
        self.__evenColour  = PropertyList._defaultEvenColour
        self.__groupColour = PropertyList._defaultGroupColour

        self.__sizer.Add(self.__propSizer,  flag=wx.EXPAND)
        self.__sizer.Add(self.__groupSizer, flag=wx.EXPAND)

        self.SetSizer(self.__sizer)
        self.SetBackgroundColour((255, 255, 255))
        self.SetupScrolling()
        self.SetAutoLayout(1)

        
    def __makePropKey(self, hasProps, propName):
        return '{}.{}_{}'.format(
            type(hasProps).__name__, propName, id(hasProps))


    def __makeWidgetKey(self, widget):
        return str(id(widget))


    def __setLabelWidths(self, props):

        if len(props) == 0:
            return

        dc        = wx.ClientDC(props[0].label)
        lblWidths = [dc.GetTextExtent(p.displayName)[0] for p in props]
        maxWidth  = max(lblWidths)

        for p in props:
            p.label.SetMinSize((maxWidth + 10, -1))
            p.label.SetMaxSize((maxWidth + 10, -1))
 

    def __setColours(self):
        def setPropColours(propDict):
            for i, prop in enumerate(propDict.values()):
                
                if i % 2: colour = self.__oddColour
                else:     colour = self.__evenColour
                prop.label .SetBackgroundColour(colour)
                prop.widget.SetBackgroundColour(colour)

        setPropColours(self.__properties)
                    
        for group in self.__groups.values():

            setPropColours(group.props)
            group.parentPanel.SetBackgroundColour(self.__groupColour)
            group.colPanel   .SetBackgroundColour(self.__groupColour)


    def __refresh(self, *a):
        self.__setColours()
        self.FitInside()
        self.Layout()


    def SetColours(self, odd=None, even=None, group=None):

        if odd   is not None: self.__oddColour   = odd
        if even  is not None: self.__evenColour  = even
        if group is not None: self.__groupColour = group
        self.__setColours()

        
    def AddGroup(self, groupName, displayName=None):

        if displayName is None:
            displayName = groupName

        if groupName in self.__groups:
            raise ValueError('A group with name {} '
                             'already exists'.format(groupName))

        parentPanel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        colPanel    = wx.CollapsiblePane(parentPanel, label=displayName)
        propPanel   = colPanel.GetPane()
        propSizer   = wx.BoxSizer(wx.VERTICAL)
        
        propPanel.SetSizer(propSizer)
        parentPanel.SetWindowStyleFlag(wx.SUNKEN_BORDER)
        self.__groupSizer.Add(parentPanel, border=10, flag=wx.EXPAND | wx.ALL)

        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(colPanel, flag=wx.EXPAND, proportion=1)
        parentPanel.SetSizer(parentSizer)

        group = Group(groupName,
                      displayName,
                      parentPanel,
                      colPanel,
                      propPanel,
                      propSizer)

        self.__groups[groupName] = group
        self.__refresh()

        colPanel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.__refresh)


    def AddWidget(self, widget, displayName, tooltip=None, groupName=None):
        """Add an arbitrary widget to the property list."""

        if groupName is None:
            widgDict    = self.__properties
            parent      = self
            parentSizer = self.__propSizer
        else:
            group       = self.__groups[groupName]
            widgDict    = group.props
            parent      = group.propPanel
            parentSizer = group.sizer 

        key = self.__makeWidgetKey(widget)

        if key in widgDict:
            raise ValueError('Widgets {} already exist'.format(key))

        widget.Reparent(parent)
        label = wx.StaticText(parent, label=displayName, style=wx.ALIGN_RIGHT)
        widgSizer = wx.BoxSizer(wx.HORIZONTAL)

        widgSizer.Add(label,  flag=wx.EXPAND)
        widgSizer.Add(widget, flag=wx.EXPAND, proportion=1)
        
        parentSizer.Add(widgSizer,
                        flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                        border=5)

        widg = Widget(displayName,
                      tooltip,
                      label,
                      widget,
                      widgSizer)

        widgDict[key] = widg

        self.__setLabelWidths(widgDict.values())
        self.__refresh()
        
    
    def AddProp(self,
                hasProps,
                propName,
                displayName=None,
                tooltip=None,
                groupName=None,
                **kwargs):

        if groupName is None:
            propDict    = self.__properties
            parent      = self
            parentSizer = self.__propSizer
        else:
            group       = self.__groups[groupName]
            propDict    = group.props
            parent      = group.propPanel
            parentSizer = group.sizer

        key = self.__makePropKey(hasProps, propName)

        if key in propDict:
            raise ValueError('Property {} already exists'.format(key))

        if displayName is None:
            displayName = propName

        label  = wx.StaticText(parent, label=displayName, style=wx.ALIGN_RIGHT)
        widget = props.makeWidget(parent, hasProps, propName, **kwargs)
        
        propSizer = wx.BoxSizer(wx.HORIZONTAL)

        propSizer.Add(label,  flag=wx.EXPAND)
        propSizer.Add(widget, flag=wx.EXPAND, proportion=1)
        
        parentSizer.Add(propSizer,
                        flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                        border=5)
        
        prop = Property(hasProps,
                        propName,
                        displayName,
                        tooltip,
                        label,
                        widget,
                        propSizer)

        propDict[key] = prop

        self.__setLabelWidths(propDict.values())
        self.__refresh()

    
    def RemoveProp(self, hasProps, propName, groupName=None):

        key = self.__makePropKey(hasProps, propName)

        if groupName is None:
            parentSizer = self.__propSizer
            propDict    = self.__properties
        else:
            group       = self.__groups[groupName]
            parentSizer = group.sizer            
            propDict    = group.props

        prop = propDict.pop(key)
        parentSizer.Detach(prop.sizer)

        prop.widget.Destroy()
        prop.label .Destroy()
        self.__refresh()

        
    def RemoveWidget(self, widget, groupName=None):
        key = self.__makeWidgetKey(widget)

        if groupName is None:
            parentSizer = self.__propSizer
            widgDict    = self.__properties
        else:
            group       = self.__groups[groupName]
            parentSizer = group.sizer            
            widgDict    = group.props

        widg = widgDict.pop(key)
        parentSizer.Detach(widg.sizer)

        widg.widget.Destroy()
        widg.label .Destroy()
        self.__refresh()

        
    def RemoveGroup(self, groupName):
        group = self.__groups.pop(groupName)
        self.__groupSizer.detach(group.parentPanel)
        group.parentPanel.Destroy()
        self.__refresh()


    def Clear(self):
        keys = self.__properties.keys()
        for key in keys:
            prop = self.__properties.pop(key)
            self.__propSizer.Detach(prop.sizer)
            prop.widget.Destroy()
            prop.label.Destroy()
        self.__refresh()
        
        
    def ClearGroup(self, groupName):
        group = self.__groups[groupName]
        group.sizer.Clear(True)
        group.props.clear()
        self.__refresh()

        
if __name__ == '__main__':

    class Test(props.HasProperties):
        myint    = props.Int()
        mybool   = props.Boolean()
        myreal   = props.Real(minval=0, maxval=10, clamped=True)
        mystring = props.String()
        mybounds = props.Bounds(ndims=2)

        myreal2    = props.Real(minval=0, maxval=10, clamped=True)
        myreal3    = props.Real(minval=0, maxval=10, clamped=True)
        mystring2  = props.String()
        mystring3  = props.String()
        mybool2    = props.Boolean()
        myint2     = props.Boolean()


    testObj = Test()
    testObj.mybounds.xmin = 0
    testObj.mybounds.xmax = 10
    testObj.mybounds.ymin = 10
    testObj.mybounds.ymax = 20 
    app     = wx.App()
    frame   = wx.Frame(None)
    plist   = PropertyList(frame)

    widg = wx.TextCtrl(plist)
    widg.SetValue('Bah, humbug!')

    plist.AddProp( testObj, 'myint', 'My int')
    plist.AddProp( testObj, 'mybool')
    plist.AddProp( testObj, 'myreal', 'My real', showLimits=False, spin=False)
    plist.AddProp( testObj, 'mystring')

    plist.AddWidget(widg, 'My widget')
    
    plist.AddGroup('extra1', 'Extras 1')
    plist.AddGroup('extra2', 'Extras 2')
    
    plist.AddProp(testObj, 'myreal2',   groupName='extra1', showLimits=False)
    plist.AddProp(testObj, 'myreal3',   groupName='extra1', spin=False)
    plist.AddProp(testObj, 'mystring2', groupName='extra1')
    plist.AddProp(testObj, 'mybounds',
                  'My bounds, hur', groupName='extra1', showLimits=False)
    plist.AddProp(testObj, 'mystring3', groupName='extra2')
    plist.AddProp(testObj, 'mybool2',   groupName='extra2')
    plist.AddProp(testObj, 'myint2',    groupName='extra2')

    frame.Layout()
    frame.Fit()

    frame.Show()
    app.MainLoop()
