#!/usr/bin/env python
#
# elistbox.py - An alternative to wx.gizmos.EditableListBox.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
# 

"""An alternative to :class:`wx.gizmos.EditableListBox`.

An :class:`EditableListBox` implementation. The
:class:`wx.gizmos.EditableListBox` is buggy under OS X Mavericks, and
getting tooltips working with the :class:`wx.ListBox` is an absolute pain
in the behind. So I felt the need to replicate its functionality.
This implementation supports single selection only.
"""

import math
import logging

import wx
import wx.lib.newevent as wxevent

log = logging.getLogger(__name__)


_ListSelectEvent, _EVT_ELB_SELECT_EVENT = wxevent.NewEvent()
_ListAddEvent,    _EVT_ELB_ADD_EVENT    = wxevent.NewEvent()
_ListRemoveEvent, _EVT_ELB_REMOVE_EVENT = wxevent.NewEvent()
_ListMoveEvent,   _EVT_ELB_MOVE_EVENT   = wxevent.NewEvent()
_ListEditEvent,   _EVT_ELB_EDIT_EVENT   = wxevent.NewEvent()


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
"""


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

ELB_NO_SCROLL = 1
"""Style flag - if enabled, there will be no scrollbar. """


ELB_NO_ADD    = 2
"""Style flag - if enabled, there will be no 'add item' button."""


ELB_NO_REMOVE = 4
"""Style flag - if enabled, there will be no 'remove item' button."""


ELB_NO_MOVE   = 8
"""Style flag - if enabled there will be no 'move item up' or 'move item
down' buttons."""


ELB_REVERSE   = 16
"""Style flag - if enabled, the first item in the list (index 0) will be
shown at the botom, and the last item at the top."""


ELB_TOOLTIP   = 32
"""Style flag - if enabled, list items will be replaced with a tooltip
on mouse-over."""


ELB_EDITABLE = 64
"""Style flag - if enabled, double clicking a list item will allow the
user to edit the item value.
"""


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


class EditableListBox(wx.Panel):
    """An alternative to :class:`wx.gizmos.EditableListBox`.

    An ``EditableListBox`` contains a :class:`wx.Panel` which in turn contains
    a collection of :class:`wx.StaticText` widgets, which are laid out
    vertically, and display labels for each of the items in the list. Some
    rudimentary wrapper methods for modifying the list contents are provided
    by an ``EditableListBox`` object, with an interface similar to that of the
    :class:`wx.ListBox` class.
    """

    _selectedFG = '#000000'
    """Default foreground colour for the currently selected item."""

    
    _defaultFG = '#000000'
    """Default foreground colour for unselected items."""

    
    _selectedBG = '#7777FF'
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
        """Create an :class:`EditableListBox` object.

        :param parent:     :mod:`wx` parent object
        
        :param labels:     List of strings, the items in the list
        :type  labels:     list of strings
        
        :param clientData: List of data associated with the list items.

        :param tooltips:   List of strings, tooltips for each item.
        :type  tooltips:   list of strings 

        :param int style:  Style bitmask - accepts :data:`ELB_NO_SCROLL`,
                           :data:`ELB_NO_ADD`, :data:`ELB_NO_REMOVE`,
                           :data:`ELB_NO_MOVE`, :data:`ELB_REVERSE`,
                           :data:`ELB_TOOLTIP`, and :data:`ELB_EDITABLE`.
        """

        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)

        reverseOrder  =      style & ELB_REVERSE
        addScrollbar  = not (style & ELB_NO_SCROLL)
        addSupport    = not (style & ELB_NO_ADD)
        removeSupport = not (style & ELB_NO_REMOVE)
        moveSupport   = not (style & ELB_NO_MOVE)
        editSupport   =      style & ELB_EDITABLE
        showTooltips  =      style & ELB_TOOLTIP
        noButtons     = not any((addSupport, removeSupport, moveSupport))

        self._reverseOrder  = reverseOrder
        self._showTooltips  = showTooltips
        self._moveSupport   = moveSupport
        self._editSupport   = editSupport

        if labels     is None: labels     = []
        if clientData is None: clientData = [None] * len(labels)
        if tooltips   is None: tooltips   = [None] * len(labels)

        # index of the currently selected item
        self._selection  = wx.NOT_FOUND
        self._listItems  = []

        # the panel containing the list items
        self._listPanel = wx.Panel(self, style=wx.WANTS_CHARS)
        self._listSizer = wx.BoxSizer(wx.VERTICAL)
        self._listPanel.SetSizer(self._listSizer)
        self._listPanel.SetBackgroundColour(EditableListBox._defaultBG)

        if addScrollbar:
            self._scrollbar = wx.ScrollBar(self, style=wx.SB_VERTICAL)
        else:
            self._scrollbar = None

        # A panel containing buttons for doing stuff with the list
        if not noButtons:
            self._buttonPanel      = wx.Panel(self)
            self._buttonPanelSizer = wx.BoxSizer(wx.VERTICAL)
            self._buttonPanel.SetSizer(self._buttonPanelSizer) 

        # Buttons for moving the selected item up/down
        if moveSupport:
            self._upButton   = wx.Button(self._buttonPanel, label=u'\u25B2',
                                         style=wx.BU_EXACTFIT)
            self._downButton = wx.Button(self._buttonPanel, label=u'\u25BC',
                                         style=wx.BU_EXACTFIT)
            self._upButton  .Bind(wx.EVT_BUTTON, self._moveItemUp)
            self._downButton.Bind(wx.EVT_BUTTON, self._moveItemDown)

            self._buttonPanelSizer.Add(self._upButton,   flag=wx.EXPAND)
            self._buttonPanelSizer.Add(self._downButton, flag=wx.EXPAND) 

        # Button for adding new items
        if addSupport:
            self._addButton = wx.Button(self._buttonPanel, label='+',
                                        style=wx.BU_EXACTFIT)
            self._addButton.Bind(wx.EVT_BUTTON, self._addItem)
            self._buttonPanelSizer.Add(self._addButton, flag=wx.EXPAND) 

        # Button for removing the selected item
        if removeSupport:
            self._removeButton = wx.Button(self._buttonPanel, label='-',
                                           style=wx.BU_EXACTFIT)

            self._removeButton.Bind(wx.EVT_BUTTON, self._removeItem)
            self._buttonPanelSizer.Add(self._removeButton, flag=wx.EXPAND)

        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._sizer)

        if not noButtons:
            self._sizer.Add(self._buttonPanel, flag=wx.EXPAND)
            
        self._sizer.Add(self._listPanel, flag=wx.EXPAND, proportion=1)

        if addScrollbar:
            self._sizer.Add(self._scrollbar, flag=wx.EXPAND)
            self._scrollbar.Bind(wx.EVT_SCROLL,     self._drawList)
            self           .Bind(wx.EVT_MOUSEWHEEL, self._onMouseWheel)
            self._listPanel.Bind(wx.EVT_MOUSEWHEEL, self._onMouseWheel)

        def refresh(ev):
            self._updateScrollbar()
            self._drawList()
            ev.Skip()

        self.Bind(wx.EVT_PAINT,     refresh)
        self.Bind(wx.EVT_SIZE,      refresh)
        self.Bind(wx.EVT_CHAR_HOOK, self._onKeyboard)

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
                max(4 * lblHeight, self._buttonPanelSizer.CalcMin()[1])))

        # Otherwise set the minimum height
        # to the height of four items
        else:
            self.SetMinSize((lblWidth, 4 * lblHeight))

        self.Layout()

        
    def _onKeyboard(self, ev):
        """Called when a key is pressed. On up/down arrow key presses,
        changes the selected item, and scrolls if necessary.
        """
        if self._scrollbar is None:
            return

        key = ev.GetKeyCode()

        # We're only interested in
        # up/down key presses
        if key not in (wx.WXK_UP, wx.WXK_DOWN):
            self.HandleAsNavigationKey(ev)
            return

        # On up/down keys, we want to
        # select the next/previous item
        if   key == wx.WXK_UP:   offset = -1
        elif key == wx.WXK_DOWN: offset =  1

        selected = self._selection + offset
        
        if any((selected < 0, selected >= self.GetCount())):
            return

        # Change the selected item, simulating
        # a mouse click so that event listeners
        # are notified
        self._itemClicked(None, self._listItems[selected].labelWidget)

        # Update the scrollbar position, to make
        # sure the newly selected item is visible
        scrollPos = self._scrollbar.GetThumbPosition()
        
        if any((selected <  scrollPos,
                selected >= scrollPos + self._scrollbar.GetPageSize())):
            self._onMouseWheel(None, -offset)

        # Retain focus
        self.SetFocus()

        
    def _onMouseWheel(self, ev=None, move=None):
        """Called when the mouse wheel is scrolled over the list. Scrolls
        through the list accordingly.

        :arg ev:   A :class:`wx.MouseEvent`
        
        :arg move: If called programmatically, a number indicating the
                   direction in which to scroll.
        """

        if self._scrollbar is None:
            return

        if ev is not None:
            move = ev.GetWheelRotation()
            
        scrollPos = self._scrollbar.GetThumbPosition()
        
        if   move < 0: self._scrollbar.SetThumbPosition(scrollPos + 1)
        elif move > 0: self._scrollbar.SetThumbPosition(scrollPos - 1)

        self._drawList()
        self.SetFocus()

        
    def VisibleItemCount(self):
        """Returns the number of items in the list which are visible
        (i.e. which have not been hidden via a call to :meth:`ApplyFilter`).
        """
        nitems = 0

        for item in self._listItems:
            if not item.hidden:
                nitems += 1

        return nitems

    
    def _drawList(self, ev=None):
        """'Draws' the set of items in the list according to the
        current scrollbar thumb position.
        """

        nitems       = self.VisibleItemCount()

        if self._scrollbar is not None:
            thumbPos     = self._scrollbar.GetThumbPosition()
            itemsPerPage = self._scrollbar.GetPageSize()
        else:
            thumbPos      = 0
            itemsPerPage = len(self._listItems)

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
        for i, item in enumerate(self._listItems):

            if item.hidden:
                self._listSizer.Show(i, False)
                continue
                
            if (visI < start) or (visI >= end):
                self._listSizer.Show(i, False)
            else:
                self._listSizer.Show(i, True)

            visI += 1

        self._listSizer.Layout()

        if ev is not None:
            ev.Skip()


    def _updateScrollbar(self, ev=None):
        """Updates the scrollbar parameters according to the
        number of items in the list, and the screen size
        of the list panel. If there is enough room to display
        all items in the list, the scroll bar is hidden.
        """

        if self._scrollbar is None:
            return

        nitems     = self.VisibleItemCount()
        pageHeight = self._listPanel.GetClientSize().GetHeight()
        
        # Yep, I'm assuming that all
        # items are the same size
        if nitems > 0:
            itemHeight = self._listItems[0].labelWidget.GetSize().GetHeight()
        else:
            itemHeight = 0 
        
        if pageHeight == 0 or itemHeight == 0:
            itemsPerPage = nitems
        else:
            itemsPerPage = math.floor(pageHeight / float(itemHeight))

        thumbPos     = self._scrollbar.GetThumbPosition()
        itemsPerPage = min(itemsPerPage, nitems)

        # Hide the scrollbar if there is enough
        # room to display the entire list (but
        # configure the scrollbar correctly)
        if nitems == 0 or itemsPerPage >= nitems:
            self._scrollbar.SetScrollbar(0,
                                         nitems,
                                         nitems,
                                         nitems,
                                         True)
            self._sizer.Show(self._scrollbar, False)
        else:
            self._sizer.Show(self._scrollbar, True) 
            self._scrollbar.SetScrollbar(thumbPos,
                                         itemsPerPage,
                                         nitems,
                                         itemsPerPage,
                                         True)
        self.Layout()

        
    def _fixIndex(self, idx):
        """If the :data:`ELB_REVERSE` style is active, this
        method will return an inverted version of the given
        index. Otherwise it returns the index value unchanged.
        """

        if idx is None:               return idx
        if idx == wx.NOT_FOUND:       return idx
        if not self._reverseOrder:    return idx

        fixIdx = len(self._listItems) - idx - 1

        # if len(self_listItems) is passed to Insert
        # (i.e. an item is to be appended to the list)
        # the above formula will produce -1
        if (idx == len(self._listItems)) and (fixIdx == -1):
            fixIdx = 0

        return fixIdx


    def GetCount(self):
        """Returns the number of items in the list."""
        return len(self._listItems)


    def Clear(self):
        """Removes all items from the list."""

        nitems = len(self._listItems)
        for i in range(nitems):
            self.Delete(0)


    def ClearSelection(self):
        """Ensures that no items are selected."""
        
        for i, item in enumerate(self._listItems):
            item.labelWidget.SetForegroundColour(item.defaultFGColour)
            item.labelWidget.SetBackgroundColour(item.defaultBGColour)
            item.container  .SetBackgroundColour(item.defaultBGColour)

            item.labelWidget.Refresh()
            item.container  .Refresh()
            
            if item.extraWidget is not None:
                item.extraWidget.SetBackgroundColour(item.defaultBGColour)
                item.extraWidget.Refresh()
                
        self._selection = wx.NOT_FOUND

        
    def SetSelection(self, n):
        """Selects the item at the given index."""

        if n != wx.NOT_FOUND and (n < 0 or n >= len(self._listItems)):
            raise IndexError('Index {} out of bounds'.format(n))

        self.ClearSelection()

        if n == wx.NOT_FOUND: return

        self._selection = self._fixIndex(n)

        item = self._listItems[self._selection]

        item.labelWidget.SetForegroundColour(item.selectedFGColour)
        item.labelWidget.SetBackgroundColour(item.selectedBGColour)
        item.container  .SetBackgroundColour(item.selectedBGColour)

        item.labelWidget.Refresh()
        item.container  .Refresh()

        if item.extraWidget is not None:
            item.extraWidget.SetBackgroundColour(item.selectedBGColour)
            item.extraWidget.Refresh()
        
        self._updateMoveButtons()
        
        
    def GetSelection(self):
        """Returns the index of the selected item, or :data:`wx.NOT_FOUND`
        if no item is selected.
        """
        return self._fixIndex(self._selection)

        
    def Insert(self,
               label,
               pos,
               clientData=None,
               tooltip=None,
               extraWidget=None):
        """Insert an item into the list.

        :param str label:   The label to be displayed
        
        :param int pos:     Index at which the item is to be inserted
        
        :param clientData:  Data associated with the item

        :param str tooltip: Tooltip to be shown, if the
                            :data:`ELB_TOOLTIP` style is active.
        
        :param extraWidget: A widget to be displayed alongside the
                            label.
        
        """

        if pos < 0 or pos > self.GetCount():
            raise IndexError('Index {} out of bounds'.format(pos))

        pos = self._fixIndex(pos)

        # StaticText under Linux/GTK poses problems - 
        # we cannot set background colour, nor can we
        # intercept mouse motion events. So we embed
        # the StaticText widget within a wx.Panel.
        container   = wx.Panel(self._listPanel, style=wx.WANTS_CHARS)
        labelWidget = wx.StaticText(container,
                                    label=label,
                                    style=(wx.ST_ELLIPSIZE_MIDDLE |
                                           wx.WANTS_CHARS))
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        container.SetSizer(sizer)

        if extraWidget is not None:
            extraWidget.Reparent(container)
            sizer.Add(extraWidget)

        sizer.Add(labelWidget, flag=wx.EXPAND, proportion=1)
        
        labelWidget.Bind(wx.EVT_LEFT_DOWN,  self._itemClicked)

        if self._scrollbar is not None:
            labelWidget.Bind(wx.EVT_MOUSEWHEEL, self._onMouseWheel)
            container  .Bind(wx.EVT_MOUSEWHEEL, self._onMouseWheel)

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

        if self._editSupport:
            labelWidget.Bind(
                wx.EVT_LEFT_DCLICK,
                lambda ev: self._onEdit(ev, item))

        log.debug('Inserting item ({}) at index {}'.format(label, pos))

        self._listItems.insert(pos, item)
        self._listSizer.Insert(pos, container, flag=wx.EXPAND)
        self._listSizer.Layout()

        # if an item was inserted before the currently
        # selected item, the _selection index will no
        # longer be valid - fix it.
        if self._selection != wx.NOT_FOUND and pos < self._selection:
            self._selection = self._selection + 1

        # Make sure item fg/bg colours are up to date
        self.SetSelection(self._fixIndex(self._selection))

        self._updateMoveButtons()
        self._configTooltip(item)
        self._updateScrollbar()
        self.Refresh()


    def _configTooltip(self, listItem):
        """If the :data:`ELB_TOOLTIP` style was enabled, this method
        configures mouse-over listeners on the widget representing the given
        list item, so the item displays the tool tip on mouse overs.
        """

        if not self._showTooltips: return

        def mouseOver(ev):
            if listItem.tooltip is not None:
                listItem.labelWidget.SetLabel(listItem.tooltip)
        def mouseOut(ev):
            if listItem.tooltip is not None:
                listItem.labelWidget.SetLabel(listItem.label)

        # Register motion listeners on the widget
        # container so it works under GTK
        listItem.container.Bind(wx.EVT_ENTER_WINDOW, mouseOver)
        listItem.container.Bind(wx.EVT_LEAVE_WINDOW, mouseOut) 
                
            
    def Append(self, label, clientData=None, tooltip=None, extraWidget=None):
        """Appends an item to the end of the list.

        :param str label:   The label to be displayed
        
        :param clientData:  Data associated with the item
        
        :param str tooltip: Tooltip to be shown, if the
                            :data:`ELB_TOOLTIP` style is active.

        :param extraWidget: A widget to be displayed alonside the item.
        """
        self.Insert(label,
                    len(self._listItems),
                    clientData,
                    tooltip,
                    extraWidget)


    def Delete(self, n):
        """Removes the item at the given index from the list."""

        n = self._fixIndex(n)

        if n < 0 or n >= len(self._listItems):
            raise IndexError('Index {} out of bounds'.format(n))

        item = self._listItems.pop(n)

        self._listSizer.Remove(n)

        # Destroying the container will result in the
        # child widget(s) being destroyed as well.
        item.container.Destroy()
        
        self._listSizer.Layout()

        # if the deleted item was selected, clear the selection
        if self._selection == n:
            self.ClearSelection()

        # or if the deleted item was before the
        # selection, fix the selection index
        elif self._selection > n:
            self._selection = self._selection - 1

        self._updateMoveButtons()
        self._updateScrollbar()
        self.Refresh()


    def IndexOf(self, clientData):
        """Returns the index of the list item with the specified
        ``clientData``.
        """

        for i, item in enumerate(self._listItems):
            if item.data == clientData:
                return self._fixIndex(i)
            
        return -1

    
    def SetItemWidget(self, n, widget=None):
        """Sets the widget to be displayed alongside the item at index ``n``.
        """

        item = self._listItems[self._fixIndex(n)]

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

        return self._listItems[i].extraWidget


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
        
        item = self._listItems[self._fixIndex(n)]

        item.defaultFGColour  = defaultColour
        item.selectedFGColour = selectedColour

        self.SetSelection(self._fixIndex(self._selection))

    
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
        
        item = self._listItems[self._fixIndex(n)]

        item.defaultBGColour  = defaultColour
        item.selectedBGColour = selectedColour

        self.SetSelection(self._fixIndex(self._selection))


    def SetItemFont(self, n, font):
        """Sets the font for the item label at index ``n``."""
        li   = self._listItems[self._fixIndex(n)]
        li.labelWidget.SetFont(font)

        
    def GetItemFont(self, n):
        """Returns the font for the item label at index ``n``."""
        li = self._listItems[self._fixIndex(n)]
        return li.labelWidget.GetFont()        

        
    def SetString(self, n, s):
        """Sets the label of the item at index ``n`` to the string ``s``.
        
        :param int n: Index of the item.
        :param str s: New label for the item.
        """

        if n < 0 or n >= self.GetCount():
            raise IndexError('Index {} is out of bounds'.format(n))

        n = self._fixIndex(n)
        
        self._listItems[n].labelWidget.SetLabel(s)
        self._listItems[n].label = s


    def ApplyFilter(self, filterStr=None, ignoreCase=False):
        """Hides any items for which the label does not contain the given
        ``filterStr``. To clear the filter (and hence show all items),
        pass in ``filterStr=None``.
        """

        if filterStr is None:
            filterStr = ''

        filterStr = filterStr.strip().lower()

        for item in self._listItems:
            item.hidden = filterStr not in item.label.lower()

        self._updateScrollbar()
        self._drawList()

            
    def _getSelection(self, fix=False):
        """Returns a 3-tuple containing the (uncorrected) index, label,
        and associated client data of the currently selected list item,
        or (None, None, None) if no item is selected. 
        """
        
        idx   = self._selection
        label = None
        data  = None

        if idx == wx.NOT_FOUND:
            idx = None
        else:
            label = self._listItems[idx].label
            data  = self._listItems[idx].data

        if fix:
            idx = self._fixIndex(idx)

        return idx, label, data
        
        
    def _itemClicked(self, ev=None, widget=None):
        """Called when an item in the list is clicked. Selects the item
        and posts an :data:`EVT_ELB_SELECT_EVENT`.

        This method may be called programmatically, by explicitly passing
        in the target ``widget``.  This functionality is used by the
        :meth:`_onKeyboard` event.

        :arg ev:     A :class:`wx.MouseEvent`.
        :arg widget: The widget on which to simulate a mouse click.
        """

        # Give focus to the top level  panel,
        # otherwise it will not receive char events
        self.SetFocus()

        if ev is not None:
            widget = ev.GetEventObject()

        itemIdx = -1

        for i, listItem in enumerate(self._listItems):
            if listItem.labelWidget == widget:
                itemIdx = i
                break

        if itemIdx == -1:
            return

        self.SetSelection(self._fixIndex(itemIdx))
        
        idx, label, data = self._getSelection(True)
        
        log.debug('ListSelectEvent (idx: {}; label: {})'.format(idx, label))
        
        ev = ListSelectEvent(idx=idx, label=label, data=data)
        wx.PostEvent(self, ev)

        
    def _moveItem(self, offset):
        """Called when the 'move up' or 'move down' buttons are pushed.
        Moves the selected item by the specified offset and posts an
        :data:`EVT_ELB_MOVE_EVENT`, unless it doesn't make sense
        to do the move. 
        """

        oldIdx, label, data = self._getSelection()
        
        if oldIdx is None: return
        
        newIdx = oldIdx + offset

        # the selected item is at the top/bottom of the list.
        if oldIdx < 0 or oldIdx >= self.GetCount(): return
        if newIdx < 0 or newIdx >= self.GetCount(): return

        widget = self._listSizer.GetItem(oldIdx).GetWindow()

        self._listItems.insert(newIdx, self._listItems.pop(oldIdx))

        self._listSizer.Detach(oldIdx) 
        self._listSizer.Insert(newIdx, widget, flag=wx.EXPAND)

        oldIdx = self._fixIndex(oldIdx)
        newIdx = self._fixIndex(newIdx)

        self.SetSelection(newIdx)

        self._listSizer.Layout()

        log.debug('ListMoveEvent (oldIdx: {}; newIdx: {}; label: {})'.format(
            oldIdx, newIdx, label))
        
        ev = ListMoveEvent(
            oldIdx=oldIdx, newIdx=newIdx, label=label, data=data)
        wx.PostEvent(self, ev)

        
    def _moveItemDown(self, ev):
        """Called when the 'move down' button is pushed. Calls the
        :meth:`_moveItem` method.
        """
        self._moveItem(1)

        
    def _moveItemUp(self, ev):
        """Called when the 'move up' button is pushed. Calls the
        :meth:`_moveItem` method.
        """ 
        self._moveItem(-1) 

        
    def _addItem(self, ev):
        """Called when the 'add item' button is pushed. Does nothing but
        post an :data:`EVT_ELB_ADD_EVENT` - it is up to a registered
        handler to implement the functionality of adding an item to the
        list.
        """

        idx, label, data = self._getSelection(True)

        log.debug('ListAddEvent (idx: {}; label: {})'.format(idx, label)) 

        ev = ListAddEvent(idx=idx, label=label, data=data)
        
        wx.PostEvent(self, ev)

        
    def _removeItem(self, ev):
        """Called when the 'remove item' button is pushed.
        Removes the selected item from the list, and posts an
        :data:`EVT_ELB_REMOVE_EVENT`.
        """

        idx, label, data = self._getSelection(True)

        if idx is None: return

        self.Delete(idx)

        if self.GetCount() > 0:
            if idx == self.GetCount():
                self.SetSelection(idx - 1)
            else:
                self.SetSelection(idx)

        log.debug('ListRemoveEvent (idx: {}; label: {})'.format(idx, label)) 

        ev = ListRemoveEvent(idx=idx, label=label, data=data)
        
        wx.PostEvent(self, ev)


    def _onEdit(self, ev, listItem):
        """Called when an item is double clicked. See the :data:`ELB_EDITABLE`
        style.

        Creates and displays a :class:`wx.TextCtrl` allowing the user to edit
        the item label. A :class:`ListEditEvent` is posted every time the text
        changes.
        """
        idx      = self._listItems.index(listItem)
        idx      = self._fixIndex(idx) 

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
            def _onFinish():
                sizer.Detach(editCtrl)
                editCtrl.Destroy()
                sizer.Show(listItem.labelWidget, True)
                sizer.Layout()
            wx.CallAfter(_onFinish)

        # Sets the list item label to the new
        # value, and posts a ListEditEvent.
        def onText(ev):
            newLabel       = editCtrl.GetValue()
            listItem.label = newLabel
            listItem.labelWidget.SetLabel(newLabel)

            ev = ListEditEvent(idx=idx, label=newLabel, data=listItem.data)
            wx.PostEvent(self, ev)

        editCtrl.Bind(wx.EVT_TEXT,       onText)
        editCtrl.Bind(wx.EVT_KEY_DOWN,   onKey)
        editCtrl.Bind(wx.EVT_TEXT_ENTER, onFinish)
        editCtrl.Bind(wx.EVT_KILL_FOCUS, onFinish)
        
        sizer.Add(editCtrl, flag=wx.EXPAND, proportion=1)
        sizer.Show(listItem.labelWidget, False)
        sizer.Layout()

        editCtrl.SetFocus()


    def _updateMoveButtons(self):
        if self._moveSupport:
            self._upButton  .Enable((self._selection != wx.NOT_FOUND) and
                                    (self._selection != 0))
            self._downButton.Enable((self._selection != wx.NOT_FOUND) and
                                    (self._selection != self.GetCount() - 1))


def _testEListBox():
    """Little testing application. """

    import random

    logging.basicConfig(
        format='%(levelname)8s '
               '%(filename)20s '
               '%(lineno)4d: '
               '%(funcName)s - '
               '%(message)s',
        level=logging.DEBUG)

    items   = map(str, range(5))
    tips    = ['--{}--'.format(i) for i in items]

    app     = wx.App()
    frame   = wx.Frame(None)
    panel   = wx.Panel(frame)
    listbox = EditableListBox(panel, items, tooltips=tips,
                              style=(ELB_REVERSE    |
                                     ELB_TOOLTIP    |
                                     ELB_EDITABLE))

    panelSizer = wx.BoxSizer(wx.HORIZONTAL)
    panel.SetSizer(panelSizer)
    panelSizer.Add(listbox, flag=wx.EXPAND, proportion=1)

    frameSizer = wx.BoxSizer(wx.HORIZONTAL)
    frame.SetSizer(frameSizer)
    frameSizer.Add(panel, flag=wx.EXPAND, proportion=1) 

    frame.Show()

    def addItem(ev):

        data   = random.randint(100, 200)
        widg   = wx.Button(listbox, label='Update')
        widg.toggle = False

        def onWidg(ev):

            widg.toggle = not widg.toggle
            idx    = listbox.IndexOf(data)
            if widg.toggle:
                font = wx.NORMAL_FONT.Larger().Larger().Bold().Italic()
                listbox.SetItemForegroundColour(idx, '#ff0000')
                listbox.SetItemFont(idx, font)
            else:
                listbox.SetItemForegroundColour(idx, '#000000')
                listbox.SetItemFont(idx, wx.NORMAL_FONT)

        widg.Bind(wx.EVT_BUTTON, onWidg)

        listbox.Append(
            str(data),
            data,
            extraWidget=widg)

    listbox.Bind(EVT_ELB_ADD_EVENT, addItem)
    
    
    app.MainLoop()
