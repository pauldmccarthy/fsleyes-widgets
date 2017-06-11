#!/usr/bin/env python
#
# widgetlist.py - A widget which displays a list of groupable widgets.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`WidgetList` class, which displays a list
of widgets.
"""


from collections import OrderedDict

import wx
import wx.lib.newevent      as wxevent
import wx.lib.scrolledpanel as scrolledpanel


class WidgetList(scrolledpanel.ScrolledPanel):
    """A scrollable list of widgets.

    The ``WidgetList`` provides a number of features:

      - Widgets can be grouped.
      - A label can be shown next to each widget.
      - Widget groups can be collapsed/expanded.
      - Widgets and groups can be dynamically added/removed.


    The most important methods are:

     .. autosummary::
        :nosignatures:

        AddWidget
        AddGroup


    A ``WidgetList`` looks something like this:

     .. image:: images/widgetlist.png
        :scale: 50%
        :align: center


    A ``WidgetList`` emits a :data:`WidgetListChangeEvent` whenever its
    contents change.
    """


    _defaultOddColour   = '#eaeaea'
    """Background colour for widgets on odd rows. """


    _defaultEvenColour  = '#ffffff'
    """Background colour for widgets on even rows. """


    _defaultGroupColour = '#cdcdff'
    """Border and title background colour for widget groups. """


    def __init__(self, parent):
        """Create a ``WidgetList``.

        :arg parent: The :mod:`wx` parent object.
        """
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
        """Widgets are stored in a dictionary - this method generates a
        string to use as a key, based on the widget ``id``.
        """
        return str(id(widget))


    def __setLabelWidths(self, widgets):
        """Calculates the maximum width of all widget labels, and sets all
        labels to that width.

        This ensures that all labels/widgets line are horizontally aligned.
        """

        if len(widgets) == 0:
            return

        dc        = wx.ClientDC(widgets[0].label)
        lblWidths = [dc.GetTextExtent(w.displayName)[0] for w in widgets]
        maxWidth  = max(lblWidths)

        for w in widgets:
            w.label.SetMinSize((maxWidth + 10, -1))
            w.label.SetMaxSize((maxWidth + 10, -1))


    def __setColours(self):
        """Called whenever the widget list needs to be refreshed.

        Makes sure that odd/even widgets and their labels have the correct
        background colour.
        """
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


    def __refresh(self, *args, **kwargs):
        """Updates widget colours (see :meth:`__setColours`), and lays out
        the widget list.

        :arg postEvent: If ``True`` (the default), a
                        :data:`WidgetListChangeEvent` is posted.
        """
        self.__setColours()
        self.FitInside()
        self.Layout()

        if kwargs.get('postEvent', True):
            wx.PostEvent(self, WidgetListChangeEvent())


    def SetColours(self, odd=None, even=None, group=None):
        """Sets the colours used on this ``WidgetList``.

        Each argument is assumed to be a tuple of ``(r, g, b)`` values,
        each in the range ``[0 - 255]``.

        :arg odd:   Background colour for widgets on odd rows.
        :arg even:  Background colour for widgets on even rows.
        :arg group: Border/title colour for widget groups.
        """
        if odd   is not None: self.__oddColour   = odd
        if even  is not None: self.__evenColour  = even
        if group is not None: self.__groupColour = group
        self.__setColours()


    def GetGroups(self):
        """Returns a list containing the name of every group in this
        ``WidgetList``.
        """
        return list(self.__groups.keys())


    def HasGroup(self, groupName):
        """Returns ``True`` if this ``WidgetList`` contains a group
        with the specified name.
        """
        return groupName in self.__groups


    def RenameGroup(self, groupName, newDisplayName):
        """Changes the display name of the specified group.

         .. note:: This method only changes the *display name* of a group,
                   not the group identifier name. See the :meth:`AddGroup`
                   method.

        :arg groupName:      Name of the group.

        :arg newDisplayName: New display name for the group.
        """
        group = self.__groups[groupName]
        group.displayName = newDisplayName
        group.colPanel.SetLabel(newDisplayName)


    def AddGroup(self, groupName, displayName=None):
        """Add a new group to this ``WidgetList``.

        A :exc:`ValueError` is raised if a group with the specified name
        already exists.

        :arg groupName:   The name of the group - this is used as an
                          identifier for the group.

        :arg displayName: A string to be shown in the title bar for the
                          group. This can be changed later via the
                          :meth:`RenameGroup` method.
        """

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

        group = _Group(groupName,
                       displayName,
                       gapSizer,
                       parentPanel,
                       colPanel,
                       widgPanel,
                       widgSizer)

        self.__groups[groupName] = group
        self.__refresh()

        # Mouse wheel listener needed
        # on all children under linux/GTK
        if wx.Platform == '__WXGTK__':
            parentPanel.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)
            colPanel   .Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        colPanel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.__refresh)


    def AddWidget(self, widget, displayName, tooltip=None, groupName=None):
        """Add an arbitrary widget to the property list.

        If the ``groupName`` is not provided, the widget is added to a list
        of *top level* widgets, which appear at the top of the list, above
        any groups. Otherwise, the widget is added to the collapsible panel
        corresponding to the specified group.

        A :exc:`ValueError` is raised if the widget is already contained
        in the list.

        :arg widget:      The widget to add to the list.

        :arg displayName: The widget label/display name.

        :arg tooltip:     A tooltip for the widget.

        :arg groupName:   Name of the group to which the widget should be
                          added.

         .. note:: The provided ``widget`` may also be a :class:`wx.Sizer`
                   instances, although support for this is basic. Specifically,
                   only one level of nesting is possible, i.e. the provided
                   ``wx.Sizer`` may not have any other ``wx.Sizer``
                   instances as its children.
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

        widg = _Widget(displayName,
                       tooltip,
                       label,
                       widget,
                       widgPanel,
                       widgSizer)

        if tooltip is not None:
            widg.SetTooltip(tooltip)

        # Under linux/GTK, mouse events are
        # captured by child windows, so if
        # we want scrolling to work, we need
        # to capture scroll events on every
        # child. Under OSX/cocoa, this is
        # not necessary.
        if wx.Platform == '__WXGTK__':
            widg.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        widgDict[key] = widg

        self.__setLabelWidths(list(widgDict.values()))
        self.__refresh()


    def __onMouseWheel(self, ev):
        """Only called if running on GTK. Scrolls the widget list according
        to the mouse wheel rotation.
        """

        posx, posy = self.GetViewStart()
        rotation   = ev.GetWheelRotation()

        if   rotation > 0: delta =  5
        elif rotation < 0: delta = -5
        else:              return

        if ev.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL: posy -= delta
        else:                                            posx += delta

        self.Scroll(posx, posy)


    def AddSpace(self, groupName=None):
        """Adds some empty vertical space to the widget list.

        :arg groupName: Name of the group tio which the space should be added.
                        If not specified, the space is added to the *top level*
                        widget list - see the :meth:`AddWidget` method.
        """
        if groupName is None: parentSizer = self.__widgSizer
        else:                 parentSizer = self.__groups[groupName].sizer

        parentSizer.Add((-1, 10))


    def RemoveWidget(self, widget, groupName=None):
        """Removes and destroys the specified widget from this ``WidgetList``.

        :arg widget:    The widget to remove.

        :arg groupName: Name of the group in which the widget is contained.
        """
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
        """Removes the specified group, and destroys all of the widgets
        contained within it.
        """
        group = self.__groups.pop(groupName)

        self.__groupSizer.Detach(group.gapSizer)
        group.parentPanel.Destroy()
        self.__refresh()


    def Clear(self):
        """Removes and destroys all widgets and groups. """
        keys = self.__widgets.keys()
        for key in keys:
            widg = self.__widgets.pop(key)
            self.__propSizer.Detach(widg.sizer)
            widg.Destroy()

        for group in self.GetGroups():
            self.RemoveGroup(group)
        self.__refresh()


    def ClearGroup(self, groupName):
        """Removes and destroys all widgets in the specified group, but
        does not remove the group.
        """
        group = self.__groups[groupName]
        group.sizer.Clear(True)
        group.widgets.clear()
        self.__refresh()


    def GroupSize(self, groupName):
        """Returns the number of widgets that have been added to the
        specified group.
        """
        return len(self.__groups[groupName].widgets)


    def IsExpanded(self, groupName):
        """Returns ``True`` if the panel for the specified group is currently
        expanded, ``False`` if it is collapsed
        """
        return self.__groups[groupName].colPanel.IsExpanded()


    def Expand(self, groupName, expand=True):
        """Expands or collapses the panel for the specified group. """
        panel = self.__groups[groupName].colPanel
        if expand: panel.Expand()
        else:      panel.Collapse()
        self.__refresh()


class _Widget(object):
    """The ``_Widget`` class is used internally by the :class:`WidgetList`
    to organise references to each widget in the list.
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


    def SetTooltip(self, tooltip):

        self.label.SetToolTip(wx.ToolTip(tooltip))

        if isinstance(self.widget, wx.Sizer):
            for child in self.widget.GetChildren():
                child.GetWindow().SetToolTip(wx.ToolTip(tooltip))
        else:
            self.widget.SetToolTip(wx.ToolTip(tooltip))


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


class _Group(object):
    """The ``_Group`` class is used internally by :class:`WidgetList`
    instances to represent groups of widgets that are in the list.
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



_WidgetListChangeEvent, _EVT_WL_CHANGE_EVENT = wxevent.NewEvent()


WidgetListChangeEvent = _WidgetListChangeEvent
"""Event emitted by a :class:`WidgetList` when its contents change. """


EVT_WL_CHANGE_EVENT = _EVT_WL_CHANGE_EVENT
"""Identifier for the :data:`WidgetListChangeEvent`. """
