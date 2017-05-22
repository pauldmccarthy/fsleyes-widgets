#!/usr/bin/env python
#
# elistbox.py - An alternative to wx.gizmos.EditableListBox.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""This module provides the :class:`EditableListBox` class, an alternative to
:class:`wx.gizmos.EditableListBox`.
"""

import math
import logging

import six

import wx
import wx.lib.newevent as wxevent
import wx.lib.stattext as stattext


log = logging.getLogger(__name__)


class EditableListBox(wx.Panel):
    """A panel which displays a list of items.


    An ``EditableListBox`` contains a :class:`wx.Panel` which in turn contains
    a collection of :class:`wx.StaticText` widgets, which are laid out
    vertically, and display labels for each of the items in the list. Some
    rudimentary wrapper methods for modifying the list contents are provided
    by an ``EditableListBox`` object, with an interface similar to that of the
    :class:`wx.ListBox` class.


    In addition to displaying ``StaticText`` controls, the ``EditableListBox``
    can also display arbitrary panels/controls associated with each label -
    see the :meth:`Insert` and :meth:`SetItemWidget`` methods.


     .. warning:: If you are using an ``EditableListBox`` to display arbitrary
                  controls/panels it is important to know that the
                  ``EditableListBox`` assumes that all items are of the same
                  size. Sizing/scrolling will not work properly if
                  controls/panels for different list items are of different
                  sizes.


    The following style flags are available:

     .. autosummary::
        ELB_NO_SCROLL
        ELB_NO_ADD
        ELB_NO_REMOVE
        ELB_NO_MOVE
        ELB_REVERSE
        ELB_TOOLTIP
        ELB_EDITABLE
        ELB_NO_LABELS
        ELB_WIDGET_RIGHT
        ELB_TOOLTIP_DOWN
        ELB_SCROLL_BUTTONS


    An ``EditableListBox`` generates the following events:

     .. autosummary::
        ListSelectEvent
        ListAddEvent
        ListRemoveEvent
        ListMoveEvent
        ListEditEvent
        ListDblClickEvent


     .. note::
        The ``EditableListBox`` is an alternative to the
        :class:`wx.gizmos.EditableListBox`. The latter is buggy under OS X,
        and getting tooltips working with the :class:`wx.ListBox` is an
        absolute pain in the behind. So I felt the need to replicate its
        functionality.  This implementation supports single selection only.
    """

    _selectedFG = '#000000'
    """Default foreground colour for the currently selected item."""


    _defaultFG = '#000000'
    """Default foreground colour for unselected items."""


    _selectedBG = '#cdcdff'
    """Background colour for the currently selected item."""


    _defaultBG  = '#FFFFFF'
    """Background colour for the unselected items."""


    def __init__(
            self,
            parent,
            labels=None,
            clientData=None,
            tooltips=None,
            style=0):
        """Create an ``EditableListBox``.

        :arg parent:     :mod:`wx` parent object

        :arg labels:     List of strings, the items in the list

        :arg clientData: List of data associated with the list items.

        :arg tooltips:   List of strings, tooltips for each item.

        :arg style:      Style bitmask - accepts :data:`ELB_NO_SCROLL`,
                         :data:`ELB_NO_ADD`, :data:`ELB_NO_REMOVE`,
                         :data:`ELB_NO_MOVE`, :data:`ELB_REVERSE`,
                         :data:`ELB_TOOLTIP`, :data:`ELB_EDITABLE`,
                         :data:`ELB_NO_LABEL`, :data:`ELB_WIDGET_RIGHT`,
                         :data:`ELB_TOOLTIP_DOWN`, and
                         :data:`ELB_SCROLL_BUTTONS`.
        """

        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)

        reverseOrder  =      style & ELB_REVERSE
        addScrollbar  = not (style & ELB_NO_SCROLL)
        addSupport    = not (style & ELB_NO_ADD)
        removeSupport = not (style & ELB_NO_REMOVE)
        moveSupport   = not (style & ELB_NO_MOVE)
        editSupport   =      style & ELB_EDITABLE
        showTooltips  =      style & ELB_TOOLTIP
        noLabels      =      style & ELB_NO_LABELS
        widgetOnRight =      style & ELB_WIDGET_RIGHT
        tooltipDown   =      style & ELB_TOOLTIP_DOWN   and not showTooltips
        scrollButtons =      style & ELB_SCROLL_BUTTONS and     addScrollbar
        noButtons     = not any((addSupport, removeSupport, moveSupport))

        if noLabels:
            editSupport = False

        self.__reverseOrder  = reverseOrder
        self.__showTooltips  = showTooltips
        self.__moveSupport   = moveSupport
        self.__editSupport   = editSupport
        self.__noLabels      = noLabels
        self.__widgetOnRight = widgetOnRight
        self.__tooltipDown   = tooltipDown
        self.__scrollButtons = scrollButtons

        if labels     is None: labels     = []
        if clientData is None: clientData = [None] * len(labels)
        if tooltips   is None: tooltips   = [None] * len(labels)

        # index of the currently selected
        # item, and the list of items
        # (_ListItem instances).
        self.__selection  = wx.NOT_FOUND
        self.__listItems  = []

        # the panel containing the list items
        # This is laid out with two sizers -
        # the sizer contains the list items, and
        # the SizerSizer contains scroll buttons
        # (if enabled) and the item sizer.
        self.__listPanel      = wx.Panel(self, style=wx.WANTS_CHARS)
        self.__listSizerSizer = wx.BoxSizer(wx.VERTICAL)
        self.__listSizer      = wx.BoxSizer(wx.VERTICAL)

        self.__listSizerSizer.Add(self.__listSizer,
                                  flag=wx.EXPAND,
                                  proportion=1)

        self.__listPanel.SetSizer(self.__listSizerSizer)
        self.__listPanel.SetBackgroundColour(EditableListBox._defaultBG)

        if addScrollbar:
            self.__scrollbar = wx.ScrollBar(self, style=wx.SB_VERTICAL)
        else:
            self.__scrollbar = None

        # A panel containing buttons for doing stuff with the list
        if not noButtons:
            self.__buttonPanel      = wx.Panel(self)
            self.__buttonPanelSizer = wx.BoxSizer(wx.VERTICAL)
            self.__buttonPanel.SetSizer(self.__buttonPanelSizer)

        # Buttons for moving the selected item up/down
        if moveSupport:
            self.__upButton   = wx.Button(self.__buttonPanel,
                                          label=six.u('\u25B2'),
                                          style=wx.BU_EXACTFIT)
            self.__downButton = wx.Button(self.__buttonPanel,
                                          label=six.u('\u25BC'),
                                          style=wx.BU_EXACTFIT)
            self.__upButton  .Bind(wx.EVT_BUTTON, self.__moveItemUp)
            self.__downButton.Bind(wx.EVT_BUTTON, self.__moveItemDown)

            self.__buttonPanelSizer.Add(self.__upButton,   flag=wx.EXPAND)
            self.__buttonPanelSizer.Add(self.__downButton, flag=wx.EXPAND)

        # Button for adding new items
        if addSupport:
            self.__addButton = wx.Button(self.__buttonPanel, label='+',
                                         style=wx.BU_EXACTFIT)
            self.__addButton.Bind(wx.EVT_BUTTON, self.__addItem)
            self.__buttonPanelSizer.Add(self.__addButton, flag=wx.EXPAND)

        # Button for removing the selected item
        if removeSupport:
            self.__removeButton = wx.Button(self.__buttonPanel, label='-',
                                            style=wx.BU_EXACTFIT)

            self.__removeButton.Bind(wx.EVT_BUTTON, self.__removeItem)
            self.__buttonPanelSizer.Add(self.__removeButton, flag=wx.EXPAND)

        # Up/down scroll buttons above/below the list
        if self.__scrollButtons:

            # Using wx.lib.stattext instead
            # of wx.StaticText because GTK
            # can't horizontally align text.
            self.__scrollUp   = stattext.GenStaticText(self.__listPanel,
                                                       label=six.u('\u25B2'),
                                                       style=wx.ALIGN_CENTRE)
            self.__scrollDown = stattext.GenStaticText(self.__listPanel,
                                                       label=six.u('\u25BC'),
                                                       style=wx.ALIGN_CENTRE)

            self.__scrollUp  .SetFont(self.__scrollUp  .GetFont().Smaller())
            self.__scrollDown.SetFont(self.__scrollDown.GetFont().Smaller())

            self.__listSizerSizer.Insert(0, self.__scrollUp,   flag=wx.EXPAND)
            self.__listSizerSizer.Insert(2, self.__scrollDown, flag=wx.EXPAND)

            self.__scrollUp  .Enable(False)
            self.__scrollDown.Enable(False)

            self.__scrollUp  .SetBackgroundColour('#e0e0e0')
            self.__scrollDown.SetBackgroundColour('#e0e0e0')

            self.__scrollUp  .Bind(wx.EVT_LEFT_UP, self.__onScrollButton)
            self.__scrollDown.Bind(wx.EVT_LEFT_UP, self.__onScrollButton)

        else:
            self.__scrollUp   = None
            self.__scrollDown = None

        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        if not noButtons:
            self.__sizer.Add(self.__buttonPanel, flag=wx.EXPAND)

        self.__sizer.Add(self.__listPanel, flag=wx.EXPAND, proportion=1)

        if addScrollbar:
            self.__sizer.Add(self.__scrollbar, flag=wx.EXPAND)
            self.__scrollbar.Bind(wx.EVT_SCROLL,     self.__drawList)
            self            .Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)
            self.__listPanel.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        def refresh(ev):
            self.__updateScrollbar()
            self.__drawList()
            ev.Skip()

        # We use CHAR_HOOK for key events,
        # because we want to capture key
        # presses whenever this panel or
        # any of its children has focus.
        self.Bind(wx.EVT_CHAR_HOOK, self.__onKeyboard)
        self.Bind(wx.EVT_PAINT,     refresh)
        self.Bind(wx.EVT_SIZE,      refresh)

        for label, data, tooltip in zip(labels, clientData, tooltips):
            self.Append(label, data, tooltip)

        # Figure out a nice minimum width
        dummyLabel = wx.StaticText(self, label='w' * 25)
        lblWidth, lblHeight = dummyLabel.GetBestSize().Get()
        dummyLabel.Destroy()

        # If there are buttons on this listbox,
        # set the minimum height to the height
        # of said buttons, or the height of
        # four items, whichever is bigger
        if not noButtons:
            self.SetMinSize((
                lblWidth,
                max(4 * lblHeight, self.__buttonPanelSizer.CalcMin()[1])))

        # Otherwise set the minimum height
        # to the height of four items
        else:
            self.SetMinSize((lblWidth, 4 * lblHeight))

        self.Layout()


    def __onKeyboard(self, ev):
        """Called when a key is pressed. On up/down arrow key presses,
        changes the selected item, and scrolls if necessary.
        """

        key = ev.GetKeyCode()

        # GTK seemingly randomly steals focus from
        # this control, and gives it to something
        # else, unless we force-retain focus.
        wx.CallAfter(self.SetFocus)

        # We're only interested in
        # up/down key presses
        if ev.HasModifiers() or (key not in (wx.WXK_UP, wx.WXK_DOWN)):
            ev.Skip()
            return

        # On up/down keys, we want to
        # select the next/previous item
        if   key == wx.WXK_UP:   offset = -1
        elif key == wx.WXK_DOWN: offset =  1

        selected = self.__selection + offset

        if any((selected < 0, selected >= self.GetCount())):
            return

        # Change the selected item, simulating
        # a mouse click so that event listeners
        # are notified
        self.__itemClicked(None, self.__listItems[selected].labelWidget)

        # Update the scrollbar position, to make
        # sure the newly selected item is visible
        if self.__scrollbar is not None:
            scrollPos = self.__scrollbar.GetThumbPosition()

            if any((selected <  scrollPos,
                    selected >= scrollPos + self.__scrollbar.GetPageSize())):
                self.__onMouseWheel(None, -offset)


    def __onMouseWheel(self, ev=None, move=None):
        """Called when the mouse wheel is scrolled over the list. Scrolls
        through the list accordingly.

        :arg ev:   A :class:`wx.MouseEvent`

        :arg move: If called programmatically, a number indicating the
                   direction in which to scroll.
        """

        if self.__scrollbar is None:
            return

        if ev is not None:
            move = ev.GetWheelRotation()

        scrollPos = self.__scrollbar.GetThumbPosition()

        if   move < 0: self.__scrollbar.SetThumbPosition(scrollPos + 1)
        elif move > 0: self.__scrollbar.SetThumbPosition(scrollPos - 1)

        self.__drawList()
        self.SetFocus()


    def __onScrollButton(self, ev):
        """Called when either of the scroll up/down buttons are clicked (if
        the :data:`.ELB_SCROLL_BUTTONS` style is active). Scrolls the list
        up/down, if possible.
        """

        button = ev.GetEventObject()

        if not button.IsEnabled():
            return

        if button is self.__scrollUp: move =  1
        else:                         move = -1

        self.__onMouseWheel(move=move)


    def VisibleItemCount(self):
        """Returns the number of items in the list which are visible
        (i.e. which have not been hidden via a call to :meth:`ApplyFilter`).
        """
        nitems = 0

        for item in self.__listItems:
            if not item.hidden:
                nitems += 1

        return nitems


    def __drawList(self, ev=None):
        """'Draws' the set of items in the list according to the
        current scrollbar thumb position.
        """

        nitems = self.VisibleItemCount()

        if self.__scrollbar is not None:
            thumbPos     = self.__scrollbar.GetThumbPosition()
            itemsPerPage = self.__scrollbar.GetPageSize()
        else:
            thumbPos      = 0
            itemsPerPage = len(self.__listItems)

        if itemsPerPage >= nitems:
            start = 0
            end   = nitems
        else:
            start = thumbPos
            end   = thumbPos + itemsPerPage

        if end > nitems:

            start = start - (end - nitems)
            end   = nitems

        visI = 0
        for i, item in enumerate(self.__listItems):

            if item.hidden:
                self.__listSizer.Show(item.container, False)
                continue

            if (visI < start) or (visI >= end):
                self.__listSizer.Show(item.container, False)
            else:
                self.__listSizer.Show(item.container, True)

            visI += 1

        if self.__scrollButtons:
            self.__scrollUp  .Enable(thumbPos > 0)
            self.__scrollDown.Enable(end      < nitems)

        self.__listSizer.Layout()

        if ev is not None:
            ev.Skip()


    def __updateScrollbar(self, ev=None):
        """Updates the scrollbar parameters according to the number of items
        in the list, and the screen size of the list panel. If there is
        enough room to display all items in the list, the scroll bar is
        hidden.
        """

        if self.__scrollbar is None:
            return

        nitems     = self.VisibleItemCount()
        pageHeight = self.__listSizerSizer.GetItem(self.__listSizer) \
                                          .GetSize().GetHeight()

        # Yep, I'm assuming that all
        # items are the same size
        if nitems > 0:
            itemHeight = self.__listItems[0].container.GetSize().GetHeight()
        else:
            itemHeight = 0

        if pageHeight == 0 or itemHeight == 0:
            itemsPerPage = nitems
        else:
            itemsPerPage = math.floor(pageHeight / float(itemHeight))

        thumbPos     = self.__scrollbar.GetThumbPosition()
        itemsPerPage = min(itemsPerPage, nitems)

        # Hide the scrollbar if there is enough
        # room to display the entire list (but
        # configure the scrollbar correctly)
        if nitems == 0 or itemsPerPage >= nitems:
            self.__scrollbar.SetScrollbar(0,
                                          nitems,
                                          nitems,
                                          nitems,
                                          True)
            self.__sizer.Show(self.__scrollbar, False)
        else:
            self.__sizer.Show(self.__scrollbar, True)
            self.__scrollbar.SetScrollbar(thumbPos,
                                          itemsPerPage,
                                          nitems,
                                          itemsPerPage,
                                          True)
        self.Layout()


    def __fixIndex(self, idx):
        """If the :data:`ELB_REVERSE` style is active, this method will return
        an inverted version of the given index. Otherwise it returns the index
        value unchanged.
        """

        if idx is None:               return idx
        if idx == wx.NOT_FOUND:       return idx
        if not self.__reverseOrder:   return idx

        fixIdx = len(self.__listItems) - idx - 1

        # if len(self.__listItems) is passed to Insert
        # (i.e. an item is to be appended to the list)
        # the above formula will produce -1
        if (idx == len(self.__listItems)) and (fixIdx == -1):
            fixIdx = 0

        return fixIdx


    def GetCount(self):
        """Returns the number of items in the list."""
        return len(self.__listItems)


    def Clear(self):
        """Removes all items from the list."""

        nitems = len(self.__listItems)
        for i in range(nitems):
            self.Delete(0)


    def ClearSelection(self):
        """Ensures that no items are selected."""

        for i, item in enumerate(self.__listItems):
            item.labelWidget.SetForegroundColour(item.defaultFGColour)
            item.labelWidget.SetBackgroundColour(item.defaultBGColour)
            item.container  .SetBackgroundColour(item.defaultBGColour)

            item.labelWidget.Refresh()
            item.container  .Refresh()

            if item.extraWidget is not None:
                item.extraWidget.SetBackgroundColour(item.defaultBGColour)
                item.extraWidget.Refresh()

        self.__selection = wx.NOT_FOUND


    def SetSelection(self, n):
        """Selects the item at the given index."""

        if n != wx.NOT_FOUND and (n < 0 or n >= len(self.__listItems)):
            raise IndexError('Index {} out of bounds'.format(n))

        self.ClearSelection()

        if n == wx.NOT_FOUND: return

        self.__selection = self.__fixIndex(n)

        item = self.__listItems[self.__selection]

        item.labelWidget.SetForegroundColour(item.selectedFGColour)
        item.labelWidget.SetBackgroundColour(item.selectedBGColour)
        item.container  .SetBackgroundColour(item.selectedBGColour)

        item.labelWidget.Refresh()
        item.container  .Refresh()

        if item.extraWidget is not None:
            item.extraWidget.SetBackgroundColour(item.selectedBGColour)
            item.extraWidget.Refresh()

        self.__updateMoveButtons()


    def GetSelection(self):
        """Returns the index of the selected item, or :data:`wx.NOT_FOUND`
        if no item is selected.
        """
        return self.__fixIndex(self.__selection)


    def Insert(self,
               label,
               pos,
               clientData=None,
               tooltip=None,
               extraWidget=None):
        """Insert an item into the list.

        :arg label:       The label to be displayed.

        :arg pos:         Index at which the item is to be inserted.

        :arg clientData:  Data associated with the item.

        :arg tooltip:     Tooltip to be shown, if the :data:`ELB_TOOLTIP`
                          style is active.

        :arg extraWidget: A widget to be displayed alongside the label.
        """

        if pos < 0 or pos > self.GetCount():
            raise IndexError('Index {} out of bounds'.format(pos))

        pos = self.__fixIndex(pos)

        if self.__noLabels:
            label = ''

        # StaticText under Linux/GTK poses problems -
        # we cannot set background colour, nor can we
        # intercept mouse motion events. So we embed
        # the StaticText widget within a wx.Panel.
        container   = wx.Panel(self.__listPanel, style=wx.WANTS_CHARS)
        labelWidget = wx.StaticText(container,
                                    label=label,
                                    style=(wx.ST_ELLIPSIZE_MIDDLE   |
                                           wx.ALIGN_CENTRE_VERTICAL |
                                           wx.WANTS_CHARS))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        container.SetSizer(sizer)

        sizerItems = [labelWidget]
        if self.__noLabels: sizerFlags = [{}]
        else:               sizerFlags = [{'flag'       : wx.ALIGN_CENTRE,
                                           'proportion' : 1}]

        if extraWidget is not None:
            extraWidget.Reparent(container)

            if self.__widgetOnRight: index = 1
            else:                    index = 0

            sizerItems.insert(index, extraWidget)
            sizerFlags.insert(index, {})

        for item, flags in zip(sizerItems, sizerFlags):
            sizer.Add(item, **flags)

        labelWidget.Bind(wx.EVT_LEFT_DOWN, self.__itemClicked)
        container  .Bind(wx.EVT_LEFT_DOWN, self.__itemClicked)

        # Under linux/GTK, mouse wheel handlers
        # need to be added to children, not
        # just the top level container
        if self.__scrollbar is not None:
            labelWidget.Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)
            container  .Bind(wx.EVT_MOUSEWHEEL, self.__onMouseWheel)

        item = _ListItem(label,
                         clientData,
                         tooltip,
                         labelWidget,
                         container,
                         EditableListBox._defaultFG,
                         EditableListBox._selectedFG,
                         EditableListBox._defaultBG,
                         EditableListBox._selectedBG,
                         extraWidget)

        def onEdit(ev):
            self.__onEdit(ev, item)

        def onDblClick(ev):
            self.__onDoubleClick(ev, item)

        # If the items are editable,
        # double clicking will call
        # the __onEdit method
        if self.__editSupport:
            labelWidget.Bind(wx.EVT_LEFT_DCLICK, onEdit)
            container  .Bind(wx.EVT_LEFT_DCLICK, onEdit)

        # Otherwise, double clicking will
        # call the __onDoubleClick method
        else:
            labelWidget.Bind(wx.EVT_LEFT_DCLICK, onDblClick)
            container  .Bind(wx.EVT_LEFT_DCLICK, onDblClick)

        log.debug('Inserting item ({}) at index {}'.format(label, pos))

        self.__listItems.insert(pos, item)
        self.__listSizer.Insert(pos, container, flag=wx.EXPAND)
        self.__listSizer.Layout()

        # if an item was inserted before the currently
        # selected item, the __selection index will no
        # longer be valid - fix it.
        if self.__selection != wx.NOT_FOUND and pos < self.__selection:
            self.__selection = self.__selection + 1

        # Make sure item fg/bg colours are up to date
        self.SetSelection(self.__fixIndex(self.__selection))

        self.__updateMoveButtons()
        if self.__tooltipDown: self.__configTooltipDown(item)
        else:                  self.__configTooltip(    item)
        self.__updateScrollbar()

        # Make sure the enabled state of the
        # new label/widget is consistent with
        # the state of this elistbox.
        container.Enable(self.IsEnabled())

        self.Refresh()


    def __configTooltip(self, listItem):
        """If the :data:`ELB_TOOLTIP` style was enabled, this method
        configures mouse-over listeners on the widget representing the given
        list item, so the item displays the tool tip on mouse overs.

        If :data:`ELB_TOOLTIP` is not enabled, a regular tooltip is configured.
        """

        if not self.__showTooltips:
            if listItem.tooltip is not None:
                tooltip = wx.ToolTip(listItem.tooltip)
                listItem.labelWidget.SetToolTip(tooltip)

        else:

            def mouseOver(ev):
                if listItem.tooltip is not None:
                    listItem.labelWidget.SetLabel(listItem.tooltip)

            def mouseOut(ev):
                listItem.labelWidget.SetLabel(listItem.label)

            # Register motion listeners on the widget
            # container so it works under GTK
            listItem.container.Bind(wx.EVT_ENTER_WINDOW, mouseOver)
            listItem.container.Bind(wx.EVT_LEAVE_WINDOW, mouseOut)


    def __configTooltipDown(self, listItem):
        """If the :data:`ELB_TOOLTIP_DOWN` style was enabled, this method
        configures mouse-down listeners on the given
        list item widget, so the item displays the tool tip on mouse down.

        This method is not called if :data:`ELB_TOOLTIP_DOWN` is not enabled.
        """

        # The tooltip is shown only after the mouse
        # has been held down for a short period of
        # time. This is required so the tooltip is
        # not shown on regular clicks/double clicks.
        listItem._cancelTooltipDown = False

        def changeLabel(lbl):
            if not listItem._cancelTooltipDown:
                listItem.labelWidget.SetLabel(lbl)

        def mouseDown(ev):
            ev.Skip()
            listItem._cancelTooltipDown = False
            if listItem.tooltip is not None:
                wx.CallLater(300, changeLabel, listItem.tooltip)

        def mouseUp(ev):

            ev.Skip()
            listItem._cancelTooltipDown = True

            listItem.labelWidget.SetLabel(listItem.label)

        listItem.labelWidget.Bind(wx.EVT_LEFT_DOWN, mouseDown)
        listItem.labelWidget.Bind(wx.EVT_LEFT_UP,   mouseUp)


    def Append(self, label, clientData=None, tooltip=None, extraWidget=None):
        """Appends an item to the end of the list.

        :arg label:       The label to be displayed

        :arg clientData:  Data associated with the item

        :arg tooltip:     Tooltip to be shown, if the :data:`ELB_TOOLTIP`
                          style is active.

        :arg extraWidget: A widget to be displayed alonside the item.
        """
        self.Insert(label,
                    len(self.__listItems),
                    clientData,
                    tooltip,
                    extraWidget)


    def Delete(self, n):
        """Removes the item at the given index from the list."""

        n = self.__fixIndex(n)

        if n < 0 or n >= len(self.__listItems):
            raise IndexError('Index {} out of bounds'.format(n))

        item = self.__listItems.pop(n)

        self.__listSizer.Remove(n)

        # Destroying the container will result in the
        # child widget(s) being destroyed as well.
        item.container.Destroy()

        self.__listSizer.Layout()

        # if the deleted item was selected, clear the selection
        if self.__selection == n:
            self.ClearSelection()

        # or if the deleted item was before the
        # selection, fix the selection index
        elif self.__selection > n:
            self.__selection = self.__selection - 1

        self.__updateMoveButtons()
        self.__updateScrollbar()
        self.Refresh()


    def IndexOf(self, clientData):
        """Returns the index of the list item with the specified
        ``clientData``.
        """

        for i, item in enumerate(self.__listItems):
            if item.data == clientData:
                return self.__fixIndex(i)

        return -1


    def GetLabels(self):
        """Returns the labels of all items in the list."""
        indices = map(self.__fixIndex, range(self.GetCount()))
        return [self.__listItems[i].label for i in indices]


    def GetData(self):
        """Returns the data associated with every item in the list."""
        indices = map(self.__fixIndex, range(self.GetCount()))
        return [self.__listItems[i].data for i in indices]


    def SetItemLabel(self, n, s):
        """Sets the label of the item at index ``n`` to the string ``s``.

        :arg n: Index of the item.
        :arg s: New label for the item.
        """

        if n < 0 or n >= self.GetCount():
            raise IndexError('Index {} is out of bounds'.format(n))

        n = self.__fixIndex(n)

        self.__listItems[n].labelWidget.SetLabel(s)
        self.__listItems[n].label = s


    def GetItemLabel(self, n):
        """Returns the label of the item at index ``n``.

        :arg n: Index of the item.
        """
        if n < 0 or n >= self.GetCount():
            raise IndexError('Index {} is out of bounds'.format(n))

        n = self.__fixIndex(n)

        return self.__listItems[n].label


    def SetItemWidget(self, n, widget=None):
        """Sets the widget to be displayed alongside the item at index ``n``.

        If ``widget`` is set to ``None``, any existing widget associated
        with the item is destroyed.
        """

        item = self.__listItems[self.__fixIndex(n)]

        if widget is None and item.extraWidget is None:
            return

        sizer = item.container.GetSizer()

        if item.extraWidget is not None:
            sizer.Detach(item.extraWidget)
            item.extraWidget.Destroy()

        item.extraWidget = widget

        if widget is not None:
            widget.Reparent(item.container)
            sizer.Insert(0, widget)


    def GetItemWidget(self, i):
        """Returns the widget for the item at index ``i``, or ``None``,
        if the widget hasn't been set.
        """

        return self.__listItems[i].extraWidget

    def SetItemTooltip(self, n, tooltip=None):
        """Sets the tooltip associated with the item at index ``n``."""
        n = self.__fixIndex(n)
        self.__listItems[n].tooltip = tooltip


    def GetItemTooltip(self, n):
        """Returns the tooltip associated with the item at index ``n``."""
        n = self.__fixIndex(n)
        return self.__listItems[n].tooltip


    def SetItemData(self, n, data=None):
        """Sets the data associated with the item at index ``n``."""
        n = self.__fixIndex(n)
        self.__listItems[n].data = data


    def GetItemData(self, n):
        """Returns the data associated with the item at index ``n``."""
        n = self.__fixIndex(n)
        return self.__listItems[n].data


    def SetItemForegroundColour(self,
                                n,
                                defaultColour=None,
                                selectedColour=None):
        """Sets the foreground colour of the item at index ``n``."""

        if defaultColour is None:
            defaultColour  = EditableListBox._defaultFG
            selectedColour = EditableListBox._selectedFG

        if selectedColour is None:
            selectedColour = defaultColour

        item = self.__listItems[self.__fixIndex(n)]

        item.defaultFGColour  = defaultColour
        item.selectedFGColour = selectedColour

        self.SetSelection(self.__fixIndex(self.__selection))


    def SetItemBackgroundColour(self,
                                n,
                                defaultColour=None,
                                selectedColour=None):
        """Sets the background colour of the item at index ``n``."""

        if defaultColour is None:
            defaultColour  = EditableListBox._defaultBG
            selectedColour = EditableListBox._selectedBG

        if selectedColour is None:
            selectedColour = defaultColour

        item = self.__listItems[self.__fixIndex(n)]

        item.defaultBGColour  = defaultColour
        item.selectedBGColour = selectedColour

        self.SetSelection(self.__fixIndex(self.__selection))


    def SetItemFont(self, n, font):
        """Sets the font for the item label at index ``n``."""
        li   = self.__listItems[self.__fixIndex(n)]
        li.labelWidget.SetFont(font)


    def GetItemFont(self, n):
        """Returns the font for the item label at index ``n``."""
        li = self.__listItems[self.__fixIndex(n)]
        return li.labelWidget.GetFont()


    def Enable(self, enable=True):
        """Enables/disables this ``EditableListBox`` and all of its children.
        """
        wx.Panel.Enable(self, enable)
        for item in self.__listItems:
            item.container.Enable(enable)


    def Disable(self):
        """Equivalent to ``Enable(False)``. """
        self.Enable(False)


    def ApplyFilter(self, filterStr=None, ignoreCase=False):
        """Hides any items for which the label does not contain the given
        ``filterStr``.

        To clear the filter (and hence show all items), pass in
        ``filterStr=None``.
        """

        if filterStr is None:
            filterStr = ''

        filterStr = filterStr.strip().lower()

        for item in self.__listItems:
            item.hidden = filterStr not in item.label.lower()

        self.__updateScrollbar()
        self.__drawList()


    def __getSelection(self, fix=False):
        """Returns a 3-tuple containing the (uncorrected) index, label,
        and associated client data of the currently selected list item,
        or (None, None, None) if no item is selected.
        """

        idx   = self.__selection
        label = None
        data  = None

        if idx == wx.NOT_FOUND:
            idx = None
        else:
            label = self.__listItems[idx].label
            data  = self.__listItems[idx].data

        if fix:
            idx = self.__fixIndex(idx)

        return idx, label, data


    def __itemClicked(self, ev=None, widget=None):
        """Called when an item in the list is clicked. Selects the item
        and posts an :data:`EVT_ELB_SELECT_EVENT`.

        This method may be called programmatically, by explicitly passing
        in the target ``widget``.  This functionality is used by the
        :meth:`__onKeyboard` event.

        :arg ev:     A :class:`wx.MouseEvent`.
        :arg widget: The widget on which to simulate a mouse click. Must
                     be provided when called programmatically.
        """

        # Give focus to the top level  panel,
        # otherwise it will not receive char events
        self.SetFocusIgnoringChildren()

        if ev is not None:
            widget = ev.GetEventObject()

        itemIdx = -1

        for i, listItem in enumerate(self.__listItems):
            if widget in (listItem.labelWidget, listItem.container):
                itemIdx = i
                break

        if itemIdx == -1:
            return

        self.SetSelection(self.__fixIndex(itemIdx))

        idx, label, data = self.__getSelection(True)

        log.debug('ListSelectEvent (idx: {}; label: {})'.format(idx, label))

        ev = ListSelectEvent(idx=idx, label=label, data=data)
        wx.PostEvent(self, ev)


    def __moveItem(self, offset):
        """Called when the *move up* or *move down* buttons are pushed.

        Moves the selected item by the specified offset and posts an
        :data:`EVT_ELB_MOVE_EVENT`, unless it doesn't make sense to do the
        move.
        """

        oldIdx, label, data = self.__getSelection()

        if oldIdx is None: return

        newIdx = oldIdx + offset

        # the selected item is at the top/bottom of the list.
        if oldIdx < 0 or oldIdx >= self.GetCount(): return
        if newIdx < 0 or newIdx >= self.GetCount(): return

        widget = self.__listSizer.GetItem(oldIdx).GetWindow()

        self.__listItems.insert(newIdx, self.__listItems.pop(oldIdx))

        self.__listSizer.Detach(oldIdx)
        self.__listSizer.Insert(newIdx, widget, flag=wx.EXPAND)

        oldIdx = self.__fixIndex(oldIdx)
        newIdx = self.__fixIndex(newIdx)

        self.SetSelection(newIdx)

        self.__listSizer.Layout()

        log.debug('ListMoveEvent (oldIdx: {}; newIdx: {}; label: {})'.format(
            oldIdx, newIdx, label))

        ev = ListMoveEvent(
            oldIdx=oldIdx, newIdx=newIdx, label=label, data=data)
        wx.PostEvent(self, ev)


    def __moveItemDown(self, ev):
        """Called when the *move down* button is pushed. Calls the
        :meth:`__moveItem` method.
        """
        self.__moveItem(1)


    def __moveItemUp(self, ev):
        """Called when the *move up* button is pushed. Calls the
        :meth:`__moveItem` method.
        """
        self.__moveItem(-1)


    def __addItem(self, ev):
        """Called when the *add item* button is pushed.

        Does nothing but post an :data:`EVT_ELB_ADD_EVENT` - it is up to a
        registered handler to implement the functionality of adding an item to
        the list.
        """

        idx, label, data = self.__getSelection(True)

        log.debug('ListAddEvent (idx: {}; label: {})'.format(idx, label))

        ev = ListAddEvent(idx=idx, label=label, data=data)

        wx.PostEvent(self, ev)


    def __removeItem(self, ev):
        """Called when the *remove item* button is pushed.

        Posts an :data:`EVT_ELB_REMOVE_EVENT` and removes the
        selected item from the list.

        Event listeners may call ``Veto()`` on the event object to cancel
        the removal.
        """

        idx, label, data = self.__getSelection(True)

        if idx is None: return

        ev = ListRemoveEvent(idx=idx, label=label, data=data)

        log.debug('ListRemoveEvent (idx: {}; label: {})'.format(
            idx, label))

        # We use ProcessEvent instead of wx.PostEvent,
        # because the latter processes the event
        # asynchronously, and we need to check whether
        # the event handler vetoed the event.
        self.GetEventHandler().ProcessEvent(ev)

        if ev.GetVeto():
            log.debug('ListRemoveEvent vetoed (idx: {}; label: {})'.format(
                idx, label))
            return

        self.Delete(idx)

        if self.GetCount() > 0:
            if idx == self.GetCount():
                self.SetSelection(idx - 1)
            else:
                self.SetSelection(idx)


    def __onEdit(self, ev, listItem):
        """Called when an item is double clicked.

        This method is only called if the :data:`ELB_EDITABLE` style flag is
        set.

        Creates and displays a :class:`wx.TextCtrl` allowing the user to edit
        the item label. A :class:`ListEditEvent` is posted every time the text
        changes.
        """
        idx      = self.__listItems.index(listItem)
        idx      = self.__fixIndex(idx)

        sizer    = listItem.container.GetSizer()
        editCtrl = wx.TextCtrl(listItem.container, style=wx.TE_PROCESS_ENTER)

        editCtrl.SetValue(listItem.label)

        # Listens to key presses. The edit is
        # cancelled if the escape key is pressed.
        def onKey(ev):
            ev.Skip()
            key = ev.GetKeyCode()
            if key == wx.WXK_ESCAPE: onFinish()

        # Destroyes the textctrl, and re-shows the item label.
        def onFinish(ev=None):

            if ev is not None:
                ev.Skip()

            def _onFinish():
                sizer.Detach(editCtrl)
                editCtrl.Destroy()
                sizer.Show(listItem.labelWidget, True)
                sizer.Layout()

            wx.CallAfter(_onFinish)

        # Sets the list item label to the new
        # value, and posts a ListEditEvent.
        def onText(ev):
            oldLabel       = listItem.labelWidget.GetLabel()
            newLabel       = editCtrl.GetValue()
            listItem.label = newLabel
            listItem.labelWidget.SetLabel(newLabel)

            log.debug('ListEditEvent (idx: {}, oldLabel: {}, newLabel: {})'
                      .format(idx, oldLabel, newLabel))

            ev = ListEditEvent(idx=idx, label=newLabel, data=listItem.data)
            wx.PostEvent(self, ev)

        editCtrl.Bind(wx.EVT_TEXT,       onText)
        editCtrl.Bind(wx.EVT_KEY_DOWN,   onKey)
        editCtrl.Bind(wx.EVT_TEXT_ENTER, onFinish)
        editCtrl.Bind(wx.EVT_KILL_FOCUS, onFinish)

        if self.__widgetOnRight:
            sizer.Insert(0, editCtrl, flag=wx.EXPAND, proportion=1)
        else:
            sizer.Insert(2, editCtrl, flag=wx.EXPAND, proportion=1)

        sizer.Show(listItem.labelWidget, False)
        sizer.Layout()

        editCtrl.SetFocus()


    def __onDoubleClick(self, ev, listItem):
        """Called when an item is double clicked. See the :data:`ELB_EDITABLE`
        style.

        This method is only called if the :data:`ELB_EDITABLE` style flag is
        not set.

        Posts a :class:`ListDblClickEvent`.
        """

        idx = self.__listItems.index(listItem)
        idx = self.__fixIndex(idx)

        ev = ListDblClickEvent(idx=idx,
                               label=listItem.label,
                               data=listItem.data)
        wx.PostEvent(self, ev)


    def __updateMoveButtons(self):
        if self.__moveSupport:
            self.__upButton  .Enable((self.__selection != wx.NOT_FOUND) and
                                     (self.__selection != 0))
            self.__downButton.Enable((self.__selection != wx.NOT_FOUND) and
                                     (self.__selection != self.GetCount() - 1))


class _ListItem(object):
    """Internal class used to represent items in the list."""

    def __init__(self,
                 label,
                 data,
                 tooltip,
                 labelWidget,
                 container,
                 defaultFGColour,
                 selectedFGColour,
                 defaultBGColour,
                 selectedBGColour,
                 extraWidget=None):

        """Create a _ListItem object.

        :param str label:        The item label which will be displayed.

        :param data:             User data associated with the item.

        :param str tooltip:      A tooltip to be displayed when the mouse
                                 is moved over the item.

        :param labelWidget:      The :mod:`wx` object which represents the
                                 list item.

        :param container:        The :mod:`wx` object used as a container for
                                 the ``widget``.

        :param defaultFGColour:  Foreground colour to use when the item is
                                 not selected.

        :param selectedFGColour: Foreground colour to use when the item is
                                 selected.

        :param defaultBGColour:  Background colour to use when the item is
                                 not selected.

        :param selectedBGColour: Background colour to use when the item is
                                 selected.

        :param extraWidget:      A user-settable widget to be displayed
                                 alongside this item.
        """
        self.label            = label
        self.data             = data
        self.labelWidget      = labelWidget
        self.container        = container
        self.tooltip          = tooltip
        self.defaultFGColour  = defaultFGColour
        self.selectedFGColour = selectedFGColour
        self.defaultBGColour  = defaultBGColour
        self.selectedBGColour = selectedBGColour
        self.extraWidget      = extraWidget
        self.hidden           = False


_ListSelectEvent,   _EVT_ELB_SELECT_EVENT   = wxevent.NewEvent()
_ListAddEvent,      _EVT_ELB_ADD_EVENT      = wxevent.NewEvent()
_ListRemoveEvent,   _EVT_ELB_REMOVE_EVENT   = wxevent.NewEvent()
_ListMoveEvent,     _EVT_ELB_MOVE_EVENT     = wxevent.NewEvent()
_ListEditEvent,     _EVT_ELB_EDIT_EVENT     = wxevent.NewEvent()
_ListDblClickEvent, _EVT_ELB_DBLCLICK_EVENT = wxevent.NewEvent()


EVT_ELB_SELECT_EVENT = _EVT_ELB_SELECT_EVENT
"""Identifier for the :data:`ListSelectEvent` event."""


EVT_ELB_ADD_EVENT = _EVT_ELB_ADD_EVENT
"""Identifier for the :data:`ListAddEvent` event."""


EVT_ELB_REMOVE_EVENT = _EVT_ELB_REMOVE_EVENT
"""Identifier for the :data:`ListRemoveEvent` event."""


EVT_ELB_MOVE_EVENT = _EVT_ELB_MOVE_EVENT
"""Identifier for the :data:`ListMoveEvent` event."""


EVT_ELB_EDIT_EVENT = _EVT_ELB_EDIT_EVENT
"""Identifier for the :data:`ListEditEvent` event."""


EVT_ELB_DBLCLICK_EVENT = _EVT_ELB_DBLCLICK_EVENT


ListSelectEvent = _ListSelectEvent
"""Event emitted when an item is selected. A ``ListSelectEvent``
has the following attributes (all are set to ``None`` if no
item was selected):

- ``idx``:   Index of selected item
- ``label``: Label of selected item
- ``data``:  Client data associated with selected item
"""


ListAddEvent = _ListAddEvent
"""Event emitted when the 'add item' button is pushed. It is
up to a listener of this event to actually add a new item
to the list. A ``ListAddEvent`` has the following attributes
(all are set to ``None`` if no item was selected):

- ``idx``:   Index of selected item
- ``label``: Label of selected item
- ``data``:  Client data associated with selected item
"""


ListRemoveEvent = _ListRemoveEvent
"""Event emitted when the 'remove item' button is pushed. A
``ListRemoveEvent`` has the following attributes:

- ``idx``:   Index of removed item
- ``label``: Label of removed item
- ``data``:  Client data associated with removed item

An event handler can call ``ListRemoveEvent.Veto()`` to cancel
the item removal.
"""

def Veto(self):
    self._vetoed = True

def GetVeto(self):
    return getattr(self, '_vetoed', False)


ListRemoveEvent.Veto    = Veto
ListRemoveEvent.GetVeto = GetVeto


ListMoveEvent = _ListMoveEvent
"""Event emitted when one of the 'move up'/'move down'
buttons is pushed. A ``ListMoveEvent`` has the following
attributes:

- ``oldIdx``: Index of item before move
- ``newIdx``: Index of item after move
- ``label``:  Label of moved item
- ``data``:   Client data associated with moved item
"""


ListEditEvent = _ListEditEvent
"""Event emitted when a list item is edited by the user (see the
:data:`ELB_EDITABLE` style). A ``ListEditEvent`` has the following
attributes:

  - ``idx``:   Index of edited item
  - ``label``: New label of edited item
  - ``data``:  Client data associated with edited item.
"""

ListDblClickEvent = _ListDblClickEvent
"""Event emitted when a list item is double-clicked onthe user (see
the :data:`ELB_EDITABLE` style). A ``ListDblClickEvent`` has the
following attributes:

  - ``idx``:   Index of clicked item
  - ``label``: Label of clicked item
  - ``data``:  Client data associated with clicked item.
"""


ELB_NO_SCROLL = 1
"""If enabled, there will be no scrollbar. """


ELB_NO_ADD    = 2
"""If enabled, there will be no *add item* button."""


ELB_NO_REMOVE = 4
"""If enabled, there will be no *remove item* button."""


ELB_NO_MOVE   = 8
"""If enabled there will be no *move item up* or *move item down* buttons. """


ELB_REVERSE   = 16
"""If enabled, the first item in the list (index 0) will be shown at the
bottom, and the last item at the top.
"""


ELB_TOOLTIP   = 32
"""If enabled, list items will be replaced with a tooltip on mouse-over. If
disabled, a regular tooltip is shown.
"""


ELB_EDITABLE = 64
"""If enabled, double clicking a list item will allow the user to edit the
item value.

If this style is disabled, the :attr:`EVT_ELB_DBLCLICK_EVENT` will not
be generated.
"""

ELB_NO_LABELS = 128
"""If enabled, item labels are not shown - this is intended for lists which
are to consist solely of widgets (see the ``extraWidget`` parameter to the
:meth:`Insert` method). This style flag will negate the :data:`ELB_EDITABLE`
flag.
"""


ELB_WIDGET_RIGHT = 256
"""If enabled, item widgets are shown to the right of the item label.
Otherwise (by default) item widgets are shown to the left.
"""


ELB_TOOLTIP_DOWN = 512
"""If enabled, when the left mouse button is clicked and held down on a list
item, the item label is replaced with its tooltip while the mouse is held down.
This style is ignored if the :data:`ELB_TOOLTIP` style is active.
"""


ELB_SCROLL_BUTTONS = 1024
"""If enabled, and :data:`ELB_NO_SCROLL` is not enabled, up/down buttons are
added above/below the list, which allow the user to scroll up/down.
"""
