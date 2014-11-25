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
_ListEnableEvent, _EVT_ELB_ENABLE_EVENT = wxevent.NewEvent()
_ListEditEvent,   _EVT_ELB_EDIT_EVENT   = wxevent.NewEvent()


EVT_ELB_SELECT_EVENT = _EVT_ELB_SELECT_EVENT
"""Identifier for the :data:`ListSelectEvent` event."""


EVT_ELB_ADD_EVENT = _EVT_ELB_ADD_EVENT
"""Identifier for the :data:`ListAddEvent` event."""


EVT_ELB_REMOVE_EVENT = _EVT_ELB_REMOVE_EVENT
"""Identifier for the :data:`ListRemoveEvent` event."""


EVT_ELB_MOVE_EVENT = _EVT_ELB_MOVE_EVENT
"""Identifier for the :data:`ListMoveEvent` event."""

EVT_ELB_ENABLE_EVENT = _EVT_ELB_ENABLE_EVENT
"""Identifier for the :data:`ListEnableEvent` event."""

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


ListEnableEvent = _ListEnableEvent
"""Event emitted when a list item is enabled/disabled by
the enable/disable checkbox (see the :data:`ELB_ENABLEABLE`
style). A ``ListEnableEvent`` has the following attributes:

  - ``idx``:     Index of enabled/disabled item
  - ``label``:   Label of enabled/disabled item
  - ``data``:    Client data associated with enabled/disabled item
  - ``enabled``: State of enabled/disabled item (True for
                 enabled, False otherwise)
"""


ListEditEvent = _ListEditEvent
"""Event emitted when a list item is edited by the user (see the
:data:`ELB_EDITABLE` style). A ``ListEditEvent`` has the following
attributes:

  - ``idx``:   Index of edited item
  - ``label``: New label of edited item
  - ``data``:  Client data associated with edited item.
"""


ELB_NO_ADD    = 1
"""Style flag - if enabled, there will be no 'add item' button."""


ELB_NO_REMOVE = 2
"""Style flag - if enabled, there will be no 'remove item' button."""


ELB_NO_MOVE   = 4
"""Style flag - if enabled there will be no 'move item up' or 'move item
down' buttons."""


ELB_REVERSE   = 8
"""Style flag - if enabled, the first item in the list (index 0) will be
shown at the botom, and the last item at the top."""


ELB_TOOLTIP   = 16
"""Style flag - if enabled, list items will be replaced with a tooltip
on mouse-over."""


ELB_ENABLEABLE = 32
"""Style flag - if enabled, a check box will be displayed alongside
each list item, allowing items to be enabled/disabled.
"""


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
                 enableWidget=None):

        """Create a _ListItem object.

        :param str label:    The item label which will be displayed.

        :param data:         User data associated with the item.

        :param str tooltip:  A tooltip to be displayed when the mouse
                             is moved over the item.
        
        :param labelWidget:  The :mod:`wx` object which represents the list
                             item.
        
        :param container:    The :mod:`wx` object used as a container for 
                             the ``widget``.

        :param enableWidget: :class:`wx.CheckBox` allowing the user to
                             enable/disable the item (only present if the
                             :data:`ELB_ENABLEABLE` style is set).
        """
        self.label        = label
        self.data         = data
        self.labelWidget  = labelWidget
        self.container    = container
        self.tooltip      = tooltip
        self.enableWidget = enableWidget


class EditableListBox(wx.Panel):
    """An alternative to :class:`wx.gizmos.EditableListBox`.

    An ``EditableListBox`` contains a :class:`wx.Panel` which in turn contains
    a collection of :class:`wx.StaticText` widgets, which are laid out
    vertically, and display labels for each of the items in the list. Some
    rudimentary wrapper methods for modifying the list contents are provided
    by an ``EditableListBox`` object, with an interface similar to that of the
    :class:`wx.ListBox` class.
    """

    _selectedBG = '#7777FF'
    """Background colour for the currently selected item."""

    
    _defaultBG  = '#FFFFFF'
    """Background colour for the unselected items."""


    _enabledFG  = '#000000'
    """Foreground colour for 'enabled' list items."""

    
    _disabledFG = '#CCCCCC'
    """Foreground colour for 'disabled' list items."""

    
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

        :param int style:  Style bitmask - accepts :data:`ELB_NO_ADD`,
                           :data:`ELB_NO_REMOVE`, :data:`ELB_NO_MOVE`,
                           :data:`ELB_REVERSE`, :data:`ELB_TOOLTIP`,
                           :data:`ELB_ENABLEABLE`, and :data:`ELB_EDITABLE`.
        """

        wx.Panel.__init__(self, parent)

        reverseOrder  =      style & ELB_REVERSE
        addSupport    = not (style & ELB_NO_ADD)
        removeSupport = not (style & ELB_NO_REMOVE)
        moveSupport   = not (style & ELB_NO_MOVE)
        enableSupport =      style & ELB_ENABLEABLE
        editSupport   =      style & ELB_EDITABLE
        showTooltips  =      style & ELB_TOOLTIP
        noButtons     = not any((addSupport, removeSupport, moveSupport))

        self._reverseOrder  = reverseOrder
        self._showTooltips  = showTooltips
        self._moveSupport   = moveSupport
        self._enableSupport = enableSupport
        self._editSupport   = editSupport

        if labels     is None: labels     = []
        if clientData is None: clientData = [None] * len(labels)
        if tooltips   is None: tooltips   = [None] * len(labels)

        # index of the currently selected item
        self._selection  = wx.NOT_FOUND
        self._listItems  = []

        # the panel containing the list items
        self._listPanel = wx.Panel(self)
        self._listSizer = wx.BoxSizer(wx.VERTICAL)
        self._listPanel.SetSizer(self._listSizer)
        self._listPanel.SetBackgroundColour(EditableListBox._defaultBG)

        # The list panel width doesn't seem to be
        # automatically sized correctly, (probably
        # because of my scrollbar hackery in the
        # _updateScrollBar method). So I'm explicitly
        # setting a minimum width to overcome this.
        self._listPanel.SetMinSize((250, -1)) 

        self._scrollbar = wx.ScrollBar(self, style=wx.SB_VERTICAL)

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
        self._sizer.Add(self._scrollbar, flag=wx.EXPAND)

        def refresh(ev):
            self._updateScrollbar()
            self._drawList()
            ev.Skip()

        self._scrollbar.Bind(wx.EVT_SCROLL, self._drawList)
        self.Bind(wx.EVT_PAINT, refresh)
        self.Bind(wx.EVT_SIZE,  refresh)

        for label, data, tooltip in zip(labels, clientData, tooltips):
            self.Append(label, data, tooltip)

        self._sizer.Layout()

    
    def _drawList(self, ev=None):
        """'Draws' the set of items in the list according to the
        current scrollbar thumb position.
        """

        nitems       = len(self._listItems)
        thumbPos     = self._scrollbar.GetThumbPosition()
        itemsPerPage = self._scrollbar.GetPageSize()

        if itemsPerPage >= nitems:
            start = 0
            end   = nitems
        else:
            start = thumbPos
            end   = thumbPos + itemsPerPage

        if end > nitems:

            start = start - (end - nitems)
            end   = nitems

        for i in range(len(self._listItems)):

            if (i < start) or (i >= end):
                self._listSizer.Show(i, False)
            else:
                self._listSizer.Show(i, True)

        self._listSizer.Layout()

        if ev is not None:
            ev.Skip()


    def _updateScrollbar(self, ev=None):
        """Updates the scrollbar parameters according to the
        number of items in the list, and the screen size
        of the list panel. If there is enough room to display
        all items in the list, the scroll bar is hidden.
        """

        nitems     = len(self._listItems)
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
        self._sizer.Layout()

        
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
        
        for item in self._listItems:
            item.labelWidget.SetBackgroundColour(EditableListBox._defaultBG)
            item.container.  SetBackgroundColour(EditableListBox._defaultBG)

            item.labelWidget.Refresh()
            item.container  .Refresh()
            
            if self._enableSupport:
                item.enableWidget.SetBackgroundColour(
                    EditableListBox._defaultBG)
                item.enableWidget.Refresh()
                
        self._selection = wx.NOT_FOUND

        
    def SetSelection(self, n):
        """Selects the item at the given index."""

        if n != wx.NOT_FOUND and (n < 0 or n >= len(self._listItems)):
            raise IndexError('Index {} out of bounds'.format(n))

        self.ClearSelection()

        if n == wx.NOT_FOUND: return

        self._selection = self._fixIndex(n)

        enableWidget = self._listItems[self._selection].enableWidget
        labelWidget  = self._listItems[self._selection].labelWidget
        container    = self._listItems[self._selection].container
        
        labelWidget.SetBackgroundColour(EditableListBox._selectedBG)
        container.  SetBackgroundColour(EditableListBox._selectedBG)

        labelWidget.Refresh()
        container  .Refresh()
        
        if self._enableSupport:
            enableWidget.SetBackgroundColour(
                EditableListBox._selectedBG)
            enableWidget.Refresh()

        self._updateMoveButtons()
        
        
    def GetSelection(self):
        """Returns the index of the selected item, or :data:`wx.NOT_FOUND`
        if no item is selected.
        """
        return self._fixIndex(self._selection)

        
    def Insert(self, label, pos, clientData=None, tooltip=None):
        """Insert an item into the list.

        :param str label:   The label to be displayed
        
        :param int pos:     Index at which the item is to be inserted
        
        :param clientData:  Data associated with the item

        :param str tooltip: Tooltip to be shown, if the
                            :data:`ELB_TOOLTIP` style is active.
        """

        if pos < 0 or pos > self.GetCount():
            raise IndexError('Index {} out of bounds'.format(pos))

        pos = self._fixIndex(pos)

        # StaticText under Linux/GTK poses problems - 
        # we cannot set background colour, nor can we
        # intercept mouse motion events. So we embed
        # the StaticText widget within a wx.Panel.

        container    = wx.Panel(self._listPanel)
        enableWidget = None
        labelWidget  = wx.StaticText(container,
                                     label=label,
                                     style=wx.ST_ELLIPSIZE_MIDDLE)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        container.SetSizer(sizer)

        if self._enableSupport:
            enableWidget = wx.CheckBox(container)
            enableWidget.SetValue(True)
            sizer.Add(enableWidget)
        
        sizer.Add(labelWidget, flag=wx.EXPAND, proportion=1)
                
        container.  SetBackgroundColour(EditableListBox._defaultBG)
        labelWidget.SetBackgroundColour(EditableListBox._defaultBG)
        container  .Refresh()
        labelWidget.Refresh()
        if self._enableSupport:
            enableWidget.SetBackgroundColour(EditableListBox._defaultBG)
            enableWidget.Refresh()
        
        labelWidget.Bind(wx.EVT_LEFT_DOWN, self._itemClicked)

        item = _ListItem(label,
                         clientData,
                         tooltip,
                         labelWidget,
                         container,
                         enableWidget)

        if self._enableSupport:
            enableWidget.Bind(
                wx.EVT_CHECKBOX,
                lambda ev: self._onEnable(ev, item))
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
                
            
    def Append(self, label, clientData=None, tooltip=None):
        """Appends an item to the end of the list.

        :param str label:   The label to be displayed
        
        :param clientData:  Data associated with the item
        
        :param str tooltip: Tooltip to be shown, if the
                            :data:`ELB_TOOLTIP` style is active. 
        """
        self.Insert(label, len(self._listItems), clientData, tooltip)


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

        
    def EnableItem(self, n):
        """'Enables the list item at the given index.

        This basically amounts to changing the foreground colour. This method
        has no effect if the :data:`ELB_ENABLEABLE` style is not set.
        """

        if not self._enableSupport: return
        
        li = self._listItems[self._fixIndex(n)]
        li.labelWidget .SetForegroundColour(EditableListBox._enabledFG)
        li.container   .SetForegroundColour(EditableListBox._enabledFG)
        li.enableWidget.SetForegroundColour(EditableListBox._enabledFG)
        li.enableWidget.SetValue(True)

        li.labelWidget .Refresh()
        li.enableWidget.Refresh()
        li.container   .Refresh()

        
    def DisableItem(self, n):
        """'Disables the list item at the given index."""

        if not self._enableSupport: return
        
        li = self._listItems[self._fixIndex(n)]
        li.labelWidget .SetForegroundColour(EditableListBox._disabledFG)
        li.container   .SetForegroundColour(EditableListBox._disabledFG)
        li.enableWidget.SetForegroundColour(EditableListBox._disabledFG)
        li.enableWidget.SetValue(False)

        li.labelWidget .Refresh()
        li.enableWidget.Refresh()
        li.container   .Refresh() 

        
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
        
        
    def _itemClicked(self, ev):
        """Called when an item in the list is clicked. Selects the item
        and posts an :data:`EVT_ELB_SELECT_EVENT`.
        """

        widget  = ev.GetEventObject()
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


    def _onEnable(self, ev, listItem):
        """Called when a checkbox is clicked to enable/disable a list item.

        Toggles the item enabled state, and posts a
        :data:`EVT_ELB_ENABLE_EVENT` event.
        """

        idx = self._listItems.index(listItem)
        idx = self._fixIndex(idx)

        enabled = listItem.enableWidget.GetValue()

        if enabled: self.EnableItem( idx)
        else:       self.DisableItem(idx)

        log.debug('ListEnableEvent (idx: {}; label: {}; enabled: {})'.format(
            idx, listItem.label, enabled)) 

        ev = ListEnableEvent(idx=idx,
                             label=listItem.label,
                             data=listItem.data,
                             enabled=enabled)

        wx.PostEvent(self, ev)


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
                                     ELB_ENABLEABLE |
                                     ELB_EDITABLE))

    panelSizer = wx.BoxSizer(wx.HORIZONTAL)
    panel.SetSizer(panelSizer)
    panelSizer.Add(listbox, flag=wx.EXPAND, proportion=1)

    frameSizer = wx.BoxSizer(wx.HORIZONTAL)
    frame.SetSizer(frameSizer)
    frameSizer.Add(panel, flag=wx.EXPAND, proportion=1) 

    frame.Show()

    def addItem(ev):
        
        listbox.Append(str(random.randint(100, 200)), None)

    listbox.Bind(EVT_ELB_ADD_EVENT, addItem)
    
    
    app.MainLoop()
