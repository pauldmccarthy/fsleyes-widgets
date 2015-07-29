#!/usr/bin/env python
#
# widgetlist.py - A widget which displays a list of groupable widgets.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`WidgetList` class, which displays a list
of widgets. The widgets can be grouped arbitrarily, and widgets and groups can
be dynamically added and removed.

"""

from collections import OrderedDict

import wx
import wx.lib.scrolledpanel as scrolledpanel


class Widget(object):
    """
    """
    def __init__(self,
                 displayName,
                 tooltip,
                 label,
                 widget,
                 panel,
                 sizer):
        self.displayName = displayName
        self.tooltip     = tooltip
        self.label       = label
        self.widget      = widget
        self.panel       = panel
        self.sizer       = sizer


    def SetBackgroundColour(self, colour):
        self.panel.SetBackgroundColour(colour)
        self.label.SetBackgroundColour(colour)

        if isinstance(self.widget, wx.Sizer):
            for c in self.widget.GetChildren():
                c.GetWindow().SetBackgroundColour(colour)
        else:
            self.widget.SetBackgroundColour(colour)


    def Bind(self, evType, callback):
        self.panel.Bind(evType, callback)
        self.label.Bind(evType, callback)

        if isinstance(self.widget, wx.Sizer):
            for c in self.widget.GetChildren():
                c.GetWindow().Bind(evType, callback)
        else:
            self.widget.Bind(evType, callback)

            
    def Destroy(self):
        self.label.Destroy()
        if isinstance(self.widget, wx.Sizer):
            self.widget.Clear(True)
        else:
            self.widget.Destroy() 
                             

class Group(object):
    """The ``Group`` class is used internally by :class:`PropertyList`
    instances to represent groups of properties that are in the list.
    """ 
    def __init__(self,
                 groupName,
                 displayName,
                 gapSizer,
                 parentPanel,
                 colPanel,
                 widgPanel,
                 sizer):
        self.groupName   = groupName
        self.displayName = displayName
        self.gapSizer    = gapSizer
        self.parentPanel = parentPanel
        self.colPanel    = colPanel
        self.widgPanel   = widgPanel
        self.sizer       = sizer
        self.widgets     = OrderedDict()


class WidgetList(scrolledpanel.ScrolledPanel):


    _defaultOddColour   = '#eaeaea'
    _defaultEvenColour  = '#ffffff'
    _defaultGroupColour = '#cdcdff'

    
    def __init__(self, parent):
        self.__widgSizer   = wx.BoxSizer(wx.VERTICAL)
        self.__sizer       = wx.BoxSizer(wx.VERTICAL)

        self.__groupSizer  = wx.BoxSizer(wx.VERTICAL)
        self.__widgets     = OrderedDict()
        self.__groups      = OrderedDict()

        self.__oddColour   = WidgetList._defaultOddColour
        self.__evenColour  = WidgetList._defaultEvenColour
        self.__groupColour = WidgetList._defaultGroupColour

        self.__sizer.Add(self.__widgSizer,  flag=wx.EXPAND)
        self.__sizer.Add(self.__groupSizer, flag=wx.EXPAND)

        # The SP.__init__ method seemingly
        # induces a call to DoGetBestSize,
        # which assumes that all of the
        # things above exist. So we call
        # init after we've created those
        # things.
        scrolledpanel.ScrolledPanel.__init__(self, parent)

        self.SetSizer(self.__sizer)
        self.SetBackgroundColour((255, 255, 255))
        self.SetupScrolling()
        self.SetAutoLayout(1)

        
    def DoGetBestSize(self):
        """Returns the best size for the widget list, with all group
        widgets expanded.
        """

        width, height = self.__widgSizer.GetSize().Get()
        for name, group in self.__groups.items():
            w, h    = group.parentPanel.GetBestSize().Get()
            w      += 20
            h      += 10
            
            if w > width:
                width = w
            height += h
        
        return wx.Size(width, height)


    def __makeWidgetKey(self, widget):
        return str(id(widget))


    def __setLabelWidths(self, widgets):

        if len(widgets) == 0:
            return

        dc        = wx.ClientDC(widgets[0].label)
        lblWidths = [dc.GetTextExtent(w.displayName)[0] for w in widgets]
        maxWidth  = max(lblWidths)

        for w in widgets:
            w.label.SetMinSize((maxWidth + 10, -1))
            w.label.SetMaxSize((maxWidth + 10, -1))
 

    def __setColours(self):
        def setWidgetColours(widgDict):
            for i, widg in enumerate(widgDict.values()):
                
                if i % 2: colour = self.__oddColour
                else:     colour = self.__evenColour
                widg.SetBackgroundColour(colour)

        setWidgetColours(self.__widgets)
                    
        for group in self.__groups.values():

            setWidgetColours(group.widgets)
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


    def GetGroups(self):
        return self.__groups.keys()


    def HasGroup(self, groupName):
        return groupName in self.__groups


    def RenameGroup(self, groupName, newDisplayName):
        group = self.__groups[groupName]
        group.displayName = newDisplayName
        group.colPanel.SetLabel(newDisplayName)

        
    def AddGroup(self, groupName, displayName=None):

        if displayName is None:
            displayName = groupName

        if groupName in self.__groups:
            raise ValueError('A group with name {} '
                             'already exists'.format(groupName))

        parentPanel = wx.Panel(self, style=wx.SUNKEN_BORDER)
        colPanel    = wx.CollapsiblePane(parentPanel,
                                         label=displayName,
                                         style=wx.CP_NO_TLW_RESIZE)
        widgPanel   = colPanel.GetPane()
        widgSizer   = wx.BoxSizer(wx.VERTICAL)
        
        widgPanel.SetSizer(widgSizer)
        parentPanel.SetWindowStyleFlag(wx.SUNKEN_BORDER)

        gapSizer = wx.BoxSizer(wx.VERTICAL)

        # A spacer exists at the top,
        # and between, every group. 
        gapSizer.Add((-1, 5))
        gapSizer.Add(parentPanel, border=10, flag=(wx.EXPAND |
                                                   wx.LEFT   |
                                                   wx.RIGHT))
        self.__groupSizer.Add(gapSizer, flag=wx.EXPAND)

        parentSizer = wx.BoxSizer(wx.VERTICAL)
        parentSizer.Add(colPanel,
                        border=5,
                        flag=wx.EXPAND | wx.BOTTOM,
                        proportion=1)
        parentPanel.SetSizer(parentSizer)

        group = Group(groupName,
                      displayName,
                      gapSizer,
                      parentPanel,
                      colPanel,
                      widgPanel,
                      widgSizer)

        self.__groups[groupName] = group
        self.__refresh()

        parentPanel.Bind(wx.EVT_MOUSEWHEEL,              self.__onMouseWheel)
        colPanel   .Bind(wx.EVT_MOUSEWHEEL,              self.__onMouseWheel)
        colPanel   .Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.__refresh)


    def AddWidget(self, widget, displayName, tooltip=None, groupName=None):
        """Add an arbitrary widget to the property list.

        Accepts :class:`wx.Window` instances, or :class:`wx.Sizer` instances,
        although support for the latter is basic - only one level of nesting
        is possible, unless all of the child objects are created with this
        ``PropertyList`` as their parent.
        """

        if groupName is None:
            widgDict    = self.__widgets
            parent      = self
            parentSizer = self.__widgSizer
        else:
            group       = self.__groups[groupName]
            widgDict    = group.widgets
            parent      = group.widgPanel
            parentSizer = group.sizer 

        key = self.__makeWidgetKey(widget)

        if key in widgDict:
            raise ValueError('Widgets {} already exist'.format(key))


        widgPanel = wx.Panel(parent)
        widgSizer = wx.BoxSizer(wx.HORIZONTAL)
        widgPanel.SetSizer(widgSizer) 

        if isinstance(widget, wx.Sizer):
            for child in widget.GetChildren():
                child.GetWindow().Reparent(widgPanel)
        else:
            widget.Reparent(widgPanel)

        label = wx.StaticText(widgPanel,
                              label=displayName,
                              style=wx.ALIGN_RIGHT)

        widgSizer.Add(label,  flag=wx.EXPAND)
        widgSizer.Add(widget, flag=wx.EXPAND, proportion=1)

        parentSizer.Add(widgPanel,
                        flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                        border=5)

        widg = Widget(displayName,
                      tooltip,
                      label,
                      widget,
                      widgPanel,
                      widgSizer)

        # Under linux/GTK, mouse events are
        # captured by child windows, so if
        # we want scrolling to work, we need
        # to capture scroll events on every
        # child
        widg.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        widgDict[key] = widg

        self.__setLabelWidths(widgDict.values())
        self.__refresh()

        
    def __onMouseWheel(self, ev):
        posx, posy = self.GetViewStart().Get()
        rotation   = ev.GetWheelRotation()

        if   rotation > 0: delta =  20
        elif rotation < 0: delta = -20
        else:              return

        if ev.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL: posy -= delta
        else:                                            posx += delta

        self.Scroll(posx, posy)


    def AddSpace(self, groupName=None):
        if groupName is None: parentSizer = self.__widgSizer
        else:                 parentSizer = self.__groups[groupName].sizer

        parentSizer.Add((-1, 10))
        

    def RemoveWidget(self, widget, groupName=None):
        key = self.__makeWidgetKey(widget)

        if groupName is None:
            parentSizer = self.__widgSizer
            widgDict    = self.__widgets
        else:
            group       = self.__groups[groupName]
            parentSizer = group.sizer 
            widgDict    = group.widgets

        widg = widgDict.pop(key)
        parentSizer.Detach(widg.panel)

        widg.Destroy()
        self.__refresh()

        
    def RemoveGroup(self, groupName):
        group = self.__groups.pop(groupName)
        
        self.__groupSizer.Detach(group.gapSizer)
        group.parentPanel.Destroy()
        self.__refresh()


    def Clear(self):
        keys = self.__widgets.keys()
        for key in keys:
            widg = self.__widgets.pop(key)
            self.__propSizer.Detach(widg.sizer)
            widg.Destroy()

        for group in self.GetGroups():
            self.RemoveGroup(group)
        self.__refresh()
        
        
    def ClearGroup(self, groupName):
        group = self.__groups[groupName]
        group.sizer.Clear(True)
        group.widgets.clear()
        self.__refresh()


    def IsExpanded(self, groupName):
        return self.__groups[groupName].colPanel.IsExpanded()

    
    def Expand(self, groupName, expand=True):
        panel = self.__groups[groupName].colPanel
        if expand: panel.Expand()
        else:      panel.Collapse()
        self.__refresh()
