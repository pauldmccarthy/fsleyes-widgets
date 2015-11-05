#!/usr/bin/env python
#
# widgetgrid.py - A tabular grid of widgets.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`WidgetGrid` class, which can display a
tabular grid of arbitrary widgets.
"""


import wx
import wx.lib.scrolledpanel as scrolledpanel
import wx.lib.newevent      as wxevent


class WidgetGrid(scrolledpanel.ScrolledPanel):
    """A scrollable panel which displays a tabular grid of widgets.  A
    ``WidgetGrid`` looks something like this:

      .. image:: images/widgetgrid.png
        :scale: 50%
        :align: center


    The most important methods are:

     .. autosummary::
        :nosignatures:

        GetGridSize
        SetGridSize
        SetColours
        SetWidget
        SetText
        ClearGrid

    
    *Labels*

    .. autosummary::
       :nosignatures:
    
       ShowRowLabels
       ShowColLabels
       SetRowLabel
       SetColLabel

    
    *Selections*

    .. autosummary::
       :nosignatures:
    
       GetSelection
       SetSelection

    
    *Styles*


    The ``WidgetGrid`` supports the following styles:

    =============================== ================================
    ``wx.HSCROLL``                  Use a horizontal scrollbar.
    ``wx.VSCROLL``                  Use a vertical scrollbar.
    :data:`WG_SELECTABLE_CELLS`     Individual cells are selectable.
    :data:`WG_SELECTABLE_ROWS`      Rows are selectable.
    :data:`WG_SELECTABLE_COLUMN`    Columns are selectable.
    :data:`WG_KEY_NAVIGATION`       The keyboard can be used for
                                    navigation
    =============================== ================================


    The ``*_SELECTABLE_*`` styles are mutualliy exclusive; their precedence
    is equivalent to their order in the above table. By default, the arrow
    keys are used for keyboard navigation, but these are customisable via
    the :meth:`SetNavKeys` method.


    *Events*

    The following events may be emitted by a ``WidgetGrid``:

    .. autosummary::
       :nosignatures:

       :data:`WidgetGridSelectEvent`
    """


    _defaultBorderColour = '#000000'
    """The colour of border a border which is shown around every cell in the
    grid. 
    """

    
    _defaultOddColour    = '#ffffff'
    """Background colour for cells on odd rows."""

    
    _defaultEvenColour   = '#eeeeee'
    """Background colour for cells on even rows."""

    
    _defaultLabelColour  = '#dddddd'
    """Background colour for row and column labels."""

    
    _defaultSelectedColour = '#cdcdff'
    """Background colour for selected cells. """
    

    def __init__(self, parent, style=None):
        """Create a ``WidgetGrid``.

        :arg parent: The :mod:`wx` parent object.
        :arg style:  Style flags  - can be a combination of ``wx.HSCROLL``,
                     ``wx.VSCROLL``, :data:`WG_SELECTABLE_CELLS`,
                     :data:`WG_SELECTABLE_ROWS`, and
                     :data:`WG_SELECTABLE_COLUMNS`.
        """
        
        if style is None:
            style = wx.HSCROLL | wx.VSCROLL

        self.__hscroll = style & wx.HSCROLL
        self.__vscroll = style & wx.VSCROLL
        self.__keynav  = style & WG_KEY_NAVIGATION
        
        if   style & WG_SELECTABLE_CELLS:   self.__selectable = 'cells'
        elif style & WG_SELECTABLE_ROWS:    self.__selectable = 'rows'
        elif style & WG_SELECTABLE_COLUMNS: self.__selectable = 'columns'
        else:
            self.__keynav     = False
            self.__selectable = None
            
        scrolledpanel.ScrolledPanel.__init__(self,
                                             parent,
                                             style=wx.WANTS_CHARS)
        
        self.SetupScrolling(scroll_x=self.__hscroll,
                            scroll_y=self.__vscroll)
        self.SetAutoLayout(1)

        self.__gridPanel = wx.Panel(self, style=wx.WANTS_CHARS)

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.__sizer.Add(self.__gridPanel, flag=wx.EXPAND)

        self.__gridSizer      = None
        self.__nrows          = 0
        self.__ncols          = 0
        self.__widgets        = []
        self.__rowLabels      = []
        self.__colLabels      = []
        self.__selected       = None
        
        self.__showRowLabels  = False
        self.__showColLabels  = False
        self.__borderColour   = WidgetGrid._defaultBorderColour
        self.__labelColour    = WidgetGrid._defaultLabelColour
        self.__oddColour      = WidgetGrid._defaultOddColour
        self.__evenColour     = WidgetGrid._defaultEvenColour
        self.__selectedColour = WidgetGrid._defaultSelectedColour
        self.__upKey          = wx.WXK_UP
        self.__downKey        = wx.WXK_DOWN
        self.__leftKey        = wx.WXK_LEFT
        self.__rightKey       = wx.WXK_RIGHT


        self.Bind(wx.EVT_SIZE, self.__onResize)

        if self.__keynav:
            self.Bind(wx.EVT_CHAR_HOOK, self.__onKeyboard)


    def SetColours(self, **kwargs):
        """Set the colours used in this ``WidgetGrid``.

        :arg border:   The cell border colour.

        :arg label:    Background colour for row and column labels.

        :arg odd:      Background colour for cells on odd rows.

        :arg even:     Background colour for cells on even rows.
        
        :arg selected: Background colour for selected cells.
        """

        border   = kwargs.get('border',   self)
        label    = kwargs.get('label',    self)
        odd      = kwargs.get('odd',      self)
        even     = kwargs.get('even',     self)
        selected = kwargs.get('selected', self)

        if border   is not self: self.__borderColour   = border
        if label    is not self: self.__labelColour    = label
        if odd      is not self: self.__oddColour      = odd
        if even     is not self: self.__evenColour     = even
        if selected is not self: self.__selectedColour = selected

        self.__refresh()


    def SetNavKeys(self, **kwargs):
        """Set the keys used for keyboard navigation (if the
        :data:`WG_KEY_NAVIGATION` style is enabled). Setting an argument
        to ``None`` will disable navigation in that direction.

        :arg up:    Key to use for up navigation.
        :arg down:  Key to use for down navigation.
        :arg left:  Key to use for left navigation.
        :arg right: Key to use for right navigation.
        """

        up    = kwargs.get('up',    self)
        down  = kwargs.get('down',  self)
        left  = kwargs.get('left',  self)
        right = kwargs.get('right', self)

        self.__upKey    = up
        self.__downKey  = down
        self.__leftKey  = left
        self.__rightKey = right


    def __onResize(self, ev):
        """Called when this ``WidgetGrid`` is resized. Makes sure the
        scrollbars are up to date.
        """
        self.FitInside()


    def __reparent(self, widget, parent):
        """Convenience method which  re-parents the given widget. If
        ``widget`` is a :class:`wx.Sizer` the sizer children are re-parented.
        """
        if isinstance(widget, wx.Sizer):
            widget = [c.GetWindow() for c in widget.GetChildren()]
        else:
            widget = [widget]

        for w in widget:
            w.Reparent(parent)
            

    def __setBackgroundColour(self, widget, colour):
        """Convenience method which changes the background colour of the given
        widget. If ``widget`` is a :class:`wx.Sizer` the background colours of
        the sizer children is updated.
        """        
        if isinstance(widget, wx.Sizer):
            widget = [c.GetWindow() for c in widget.GetChildren()]
        else:
            widget = [widget]

        for w in widget:
            w.SetBackgroundColour(colour)
 
        
    def __refresh(self):
        """Lays out and re-sizes the entire widget grid. """

        borderColour = self.__borderColour
        labelColour  = self.__labelColour
        oddColour    = self.__oddColour
        evenColour   = self.__evenColour

        if borderColour is None: WidgetGrid._defaultBorderColour
        if labelColour  is None: WidgetGrid._defaultLabelColour
        if oddColour    is None: WidgetGrid._defaultOddColour
        if evenColour   is None: WidgetGrid._defaultEvenColour
        
        if self.__gridSizer is None:
            self.FitInside()
            self.Layout()
            return

        self.__gridPanel.SetBackgroundColour(borderColour)

        # Clear the sizer per-item, as the
        # wx.Sizer.Clear will destroy any
        # child sizers, and we don't want that
        for i in reversed(range(self.__gridSizer.GetItemCount())):
            self.__gridSizer.Detach(i)

        # empty cell in top left of grid
        self.__gridSizer.Add((-1, -1), flag=wx.EXPAND)

        # column labels
        for coli, (lblPanel, colLabel) in enumerate(self.__colLabels):

            # 1px border between every column
            if coli == self.__ncols - 1: flag = wx.TOP | wx.LEFT | wx.RIGHT
            else:                        flag = wx.TOP | wx.LEFT

            lblPanel.SetBackgroundColour(labelColour)
            colLabel.SetBackgroundColour(labelColour)
            
            self.__gridSizer.Add( lblPanel, border=1, flag=wx.EXPAND | flag)
            self.__gridSizer.Show(lblPanel, self.__showColLabels)

        for rowi in range(self.__nrows):
            lblPanel, rowLabel = self.__rowLabels[rowi]
            widgets            = self.__widgets[  rowi]

            if rowi == self.__nrows - 1: flag = wx.TOP | wx.LEFT | wx.BOTTOM
            else:                        flag = wx.TOP | wx.LEFT

            lblPanel.SetBackgroundColour(labelColour)
            rowLabel.SetBackgroundColour(labelColour)

            self.__gridSizer.Add( lblPanel, border=1, flag=wx.EXPAND | flag)
            self.__gridSizer.Show(lblPanel, self.__showRowLabels)

            for coli, widget in enumerate(widgets):

                flag = wx.TOP | wx.LEFT

                if rowi == self.__nrows - 1: flag |= wx.BOTTOM
                if coli == self.__ncols - 1: flag |= wx.RIGHT

                self.__gridSizer.Add(widget,
                                     flag=wx.EXPAND | flag,
                                     border=1,
                                     proportion=1)

                if rowi % 2: colour = oddColour
                else:        colour = evenColour

                self.__setBackgroundColour(widget, colour)

        if self.__selected is not None:
            row, col = self.__selected
            self.SetSelection(row, col)
        
        self.FitInside()
        self.Layout()


    def GetGridSize(self):
        """Returns the current grid size as a tuple containing ``(rows, cols)``.
        """
        return self.__nrows, self.__ncols

    
    def SetGridSize(self, nrows, ncols, growCols=None):
        """Set the size of the widdget grid.

        :arg nrows:    Number of rows

        :arg ncols:    Number of columns

        :arg growCols: A sequence specifying which columns should be stretched
                       to fit. 
        """

        if nrows < 0 or ncols < 0:
            raise ValueError('Invalid size ({}, {})'.format(nrows, ncols))

        if growCols is None:
            growCols = []

        self.ClearGrid()

        self.__nrows     = nrows
        self.__ncols     = ncols
        self.__gridSizer = wx.FlexGridSizer(nrows + 1, ncols + 1)

        self.__gridSizer.SetFlexibleDirection(wx.BOTH)

        for col in growCols:
            self.__gridSizer.AddGrowableCol(col + 1)

        # We use empty wx.Panels as placeholders
        # for empty grid cells
        self.__widgets = []
        for rowi in range(nrows):
            self.__widgets.append([])
            for coli in range(ncols):
                self.__widgets[-1].append(wx.Panel(self.__gridPanel))

        for rowi in range(nrows):
            panel = wx.Panel(self)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            lbl   = wx.StaticText(
                panel,
                style=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
            
            panel.SetSizer(sizer)
            sizer.Add(lbl, flag=wx.CENTRE)

            self.__initWidget(panel, rowi, -1)
            self.__initWidget(lbl,   rowi, -1)
            self.__rowLabels.append((panel, lbl))

        for coli in range(ncols):

            panel = wx.Panel(self)
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            lbl   = wx.StaticText(
                panel,
                style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
            
            panel.SetSizer(sizer)
            sizer.Add(lbl, flag=wx.CENTRE)

            self.__initWidget(panel, -1, coli)
            self.__initWidget(lbl,   -1, coli)
            self.__colLabels.append((panel, lbl))
            
        self.__gridPanel.SetSizer(self.__gridSizer)
        self.__refresh()

    
    def ClearGrid(self):
        """Removes and destroys all widgets from the grid, and sets the grid
        size to ``(0, 0)``.
        """

        if self.__gridSizer is not None:
            self.__gridSizer.Clear(True)

        self.__gridSizer = None
        self.__nrows     = 0
        self.__ncols     = 0
        self.__widgets   = []
        self.__rowLabels = []
        self.__colLabels = []
        self.__selected  = None

        self.__gridPanel.SetSizer(None)
        self.__refresh()


    def SetText(self, row, col, text):
        """Convenience method which creates a :class:`wx.StaticText` widget
        with the given text, and passes it to the :meth:`SetWidget` method.

        :arg row:  Row index.

        :arg col:  Column index.

        :arg text: Text to display.
        """

        txt = wx.StaticText(self.__gridPanel, label=text)
        self.SetWidget(row, col, txt)


    def SetWidget(self, row, col, widget):
        """Adds the given widget to the grid.

        The parent of the widget is changed to this ``WidgetGrid``.

         .. note::
            The provided widget may alternately be a :class:`wx.Sizer`.
            However, nested sizers, i.e. sizers which contain other
            sizers, are not supported.

        :arg row:    Row index.

        :arg col:    Column index.

        :arg widget: The widget or sizer to add to the grid.

        Raises an :exc:`IndexError` if the specified grid location ``(row,
        col)`` is invalid.
        """
        if row <  0            or \
           col <  0            or \
           row >= self.__nrows or \
           col >= self.__ncols:
            raise IndexError('Grid location ({}, {}) out of bounds ({}, {})'.
                             format(row, col, self.__nrows, self.__ncols))

        # Embed the widget in a panel,
        # as Linux/GTK has trouble
        # changing the background colour
        # of some controls
        panel = wx.Panel(self.__gridPanel, style=wx.WANTS_CHARS)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)

        self.__reparent(widget, panel)

        self.__initWidget(widget, row, col)
        self.__initWidget(panel,  row, col)

        sizer.Add(widget, flag=wx.EXPAND, proportion=1)

        if self.__widgets[row][col] is not None:
            self.__widgets[row][col].Destroy()

        self.__widgets[row][col] = panel

        self.__refresh()


    def __initWidget(self, widget, row, col):
        """Called by the :meth:`AddWidget` method.

        Performs some initialisation on a widget which has just been added to
        the grid.

        :arg widget: The widget to initialise
        :arg row:    Row index of the widget in the grid.
        :arg col:    Column index of the widget in the grid.
        """

        def scroll(ev):
            posx, posy = self.GetViewStart().Get()
            rotation   = ev.GetWheelRotation()

            if   rotation > 0: delta =  5
            elif rotation < 0: delta = -5
            else:              return
            
            if ev.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL: posy -= delta
            else:                                            posx += delta

            self.Scroll(posx, posy)

        def initWidget(w):
            
            # Under Linux/GTK, we need to bind a mousewheel
            # listener to every child of the panel in order
            # for scrolling to work correctly. This is not
            # necessary under OSX/cocoa.
            if wx.Platform == '__WXGTK__':
                w.Bind(wx.EVT_MOUSEWHEEL, scroll)

            # Listen for mouse down events 
            # if cells are selectable
            if self.__selectable:
                w.Bind(wx.EVT_LEFT_DOWN, self.__onLeftMouseDown)

            # We want keyboard events to propagate
            if self.__keynav:
                w.SetWindowStyle(w.GetWindowStyle() | wx.WANTS_CHARS)

            # Attach the row/column indices
            # to the widget - they are used
            # in the __onLeftDown method
            w._wg_row = row
            w._wg_col = col

        if isinstance(widget, wx.Sizer):
            for c in widget.GetChildren():
                initWidget(c.GetWindow())
        else:
            initWidget(widget)


    def __onLeftMouseDown(self, ev):
        """If this ``WidgetGrid`` is selectable, this method is called
        whenever an left mouse down event occurs on an item in the grid.
        """
        
        ev.Skip()

        widget = ev.GetEventObject() 
        row    = widget._wg_row
        col    = widget._wg_col

        if   self.__selectable == 'rows':    col = -1
        elif self.__selectable == 'columns': row = -1

        event = WidgetGridSelectEvent(row=row, col=col) 

        self.SetSelection(row, col)
        self.SetFocus()

        event.SetEventObject(self)
        wx.PostEvent(self, event)


    def __onKeyboard(self, ev):
        """If the :data:`WG_KEY_NAVIGATION` style is enabled, this method is
        called when the user pushes a key while this ``WidgetGrid`` has focus.
        It changes the currently selected cell, row, or column.
        """
        ev.Skip()

        key = ev.GetKeyCode()

        up    = self.__upKey
        down  = self.__downKey
        left  = self.__leftKey
        right = self.__rightKey

        if key not in (up, down, left, right):
            self.HandleAsNavigationKey(ev)            
            return

        row, col = self.__selected

        if   key == up:    row -= 1
        elif key == down:  row += 1
        elif key == left:  col -= 1
        elif key == right: col += 1

        try:    self.SetSelection(row, col)
        except: return

        ev = WidgetGridSelectEvent(row=row, col=col)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)
        

    def GetSelection(self):
        """Returns the currently selected item, as a tuple of ``(row, col)`` indices.
        If an entire row has been selected, the ``col`` index  will be -1, and
        vice-versa. If nothing is selected, ``None`` is returned.
        """
        return self.__selected


    def SetSelection(self, row, col):
        """Select the given item. A :exc:`ValueError` is raised if the selection
        is invalid.

        :arg row: Row index of item to select. Pass in -1 to select a whole
                  column.

        :arg col: Column index of item to select. Pass in -1 to select a whole
                  row.
        """

        nrows, ncols = self.GetGridSize()

        if self.__selectable == 'rows':
            
            if col != -1 or row < 0 or row >= nrows:
                raise ValueError('Invalid row: {}'.format(row))
            
        elif self.__selectable == 'columns':

            if row != -1 or col < 0 or col >= ncols:
                raise ValueError('Invalid column: {}'.format(col))
            
        elif self.__selectable == 'cells':
            
            if row < 0 or row >= nrows or col < 0 or col >= ncols:
                raise ValueError('Invalid cell: {}, {}'.format(row, col))

        if self.__selected is not None:
            
            lsrow, lscol = self.__selected
            self.__selected = None
            self.__select(lsrow, lscol, self.__selectable, False)

        self.__selected = row, col

        self.__select(row, col, self.__selectable, True)


    def __select(self, row, col, selectType, select=True):
        """Called by the :meth:`__onLeftDown` method. Sets the background
        colour of the specified row/column to the selection colour, or the
        default colour.

        :arg row:        Row index. If -1, the colour of the entire column is
                         toggled.
        
        :arg col:        Column index. If -1, the colour of the entire row is
                         toggled.
        
        :arg selectType: Either ``'rows'``, ``'columns'``, or ``'cells'``.
        
        :arg select:     If ``True``, the item background colour is set to the
                         selected colour, otherwise it is set to its default
                         colour.
        """

        nrows, ncols = self.GetGridSize()

        if row == -1 and col == -1:
            return

        if nrows == 0 or ncols == 0:
            return

        if row == -1:
            rows = range(nrows)
            cols = [col] * nrows

        elif col == -1:
            rows = [row] * ncols
            cols = range(ncols)
            
        else:
            rows = [row]
            cols = [col]

        for row, col in zip(rows, cols):

            if   select:  colour = self.__selectedColour
            elif row % 2: colour = self.__oddColour
            else:         colour = self.__evenColour

            widget = self.__widgets[row][col]
            self.__setBackgroundColour(widget, colour)
            widget.Refresh()
        

    def ShowRowLabels(self, show=True):
        """Shows/hides the grid row labels. """
        self.__showRowLabels = show
        self.__refresh()

    
    def ShowColLabels(self, show=True):
        """Shows/hides the grid column labels. """
        self.__showColLabels = show
        self.__refresh()
    
    
    def SetRowLabel(self, row, label):
        """Sets a label for the specified row.

        Raises an :exc:`IndexError` if the row is invalid.
        """
        if row < 0 or row >= self.__nrows:
            raise IndexError('Row {} out of bounds ({})'.format(
                row, self.__nrows))

        self.__rowLabels[row][1].SetLabel(label)

    
    def SetColLabel(self, col, label):
        """Sets a label for the specified column.

        Raises an :exc:`IndexError` if the column is invalid.
        """
        if col < 0 or col >= self.__ncols:
            raise IndexError('Column {} out of bounds ({})'.format(
                col, self.__ncols))

        self.__colLabels[col][1].SetLabel(label)


WG_SELECTABLE_CELLS = 1
"""If this style is enabled, individual cells can be selected. """


WG_SELECTABLE_ROWS = 2
"""If this style is enabled, whole rows can be selected. """


WG_SELECTABLE_COLUMNS = 4
"""If this style is enabled, whole columns can be selected. """


WG_KEY_NAVIGATION = 8
"""If this style is enabled along with one of the ``*_SELECTABLE_*`` styles,
the user may use the keyboard to navigate between cells, rows, or columns.
"""


_WidgetGridSelectEvent, _EVT_WG_SELECT = wxevent.NewEvent()


EVT_WG_SELECT = _EVT_WG_SELECT
"""Identifier for the :data:`WidgetGridSelectEvent`. """


WidgetGridSelectEvent = _WidgetGridSelectEvent
"""Event generated when an item in a ``WidgetGrid`` is selected. A
``WidgetGridSelectEvent`` has the following attributes:

 - ``row`` Row index of the selected item. If -1, an entire column
   has been selected.

 - ``col`` Column index of the selected item. If -1, an entire row
   has been selected.
"""
