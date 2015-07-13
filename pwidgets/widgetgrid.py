#!/usr/bin/env python
#
# widgetgrid.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import wx
import wx.lib.scrolledpanel as scrolledpanel


class WidgetGrid(scrolledpanel.ScrolledPanel):


    _defaultBorderColour = '#000000'
    _defaultOddColour    = '#ffffff'
    _defaultEvenColour   = '#eeeeee'
    _defaultLabelColour  = '#dddddd'

    def __init__(self, parent):
        scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.SetupScrolling()
        self.SetAutoLayout(1)

        self.__gridPanel = wx.Panel(self)

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.__sizer.Add(self.__gridPanel, flag=wx.EXPAND)

        self.__gridSizer     = None
        self.__nrows         = 0
        self.__ncols         = 0
        self.__widgets       = []
        self.__rowLabels     = []
        self.__colLabels     = []
        self.__showRowLabels = False
        self.__showColLabels = False
        self.__borderColour  = WidgetGrid._defaultBorderColour
        self.__labelColour   = WidgetGrid._defaultLabelColour
        self.__oddColour     = WidgetGrid._defaultOddColour
        self.__evenColour    = WidgetGrid._defaultEvenColour


    def SetColours(self, **kwargs):

        border = kwargs.get('border', self)
        label  = kwargs.get('label',  self)
        odd    = kwargs.get('odd',    self)
        even   = kwargs.get('even',   self)

        if border is not self: self.__borderColour = border
        if label  is not self: self.__labelColour  = label
        if odd    is not self: self.__oddColour    = odd
        if even   is not self: self.__evenColour   = even

        self.__refresh()

        
    def __refresh(self):

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
        self.__gridSizer.Clear(False)

        # empty cell in top left of grid
        self.__gridSizer.Add((-1, -1), flag=wx.EXPAND)

        # column labels
        for coli, colLabel in enumerate(self.__colLabels):

            # 1px border between every column
            if coli == self.__ncols - 1: flag = wx.TOP | wx.LEFT | wx.RIGHT
            else:                        flag = wx.TOP | wx.LEFT

            colLabel.SetBackgroundColour(labelColour)
            
            self.__gridSizer.Add( colLabel, border=1, flag=wx.EXPAND | flag)
            self.__gridSizer.Show(colLabel, self.__showColLabels)


        for rowi in range(self.__nrows):
            rowLabel = self.__rowLabels[rowi]
            widgets  = self.__widgets[  rowi]

            if rowi == self.__nrows - 1: flag = wx.TOP | wx.LEFT | wx.BOTTOM
            else:                        flag = wx.TOP | wx.LEFT

            rowLabel.SetBackgroundColour(labelColour)

            self.__gridSizer.Add( rowLabel, border=1, flag=wx.EXPAND | flag)
            self.__gridSizer.Show(rowLabel, self.__showRowLabels)

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

                widget.SetBackgroundColour(colour)
        
        self.FitInside()
        self.Layout()


    def SetGridSize(self, nrows, ncols):

        if nrows < 0 or ncols < 0:
            raise ValueError('Invalid size ({}, {})'.format(nrows, ncols))

        self.ClearGrid()

        self.__nrows     = nrows
        self.__ncols     = ncols
        self.__gridSizer = wx.FlexGridSizer(nrows + 1, ncols + 1)

        self.__gridSizer.SetFlexibleDirection(wx.HORIZONTAL)

        for coli in range(ncols + 1):
            self.__gridSizer.AddGrowableCol(coli)

        # We use empty wx.Panels as placeholders
        # for empty grid cells
        self.__widgets = []
        for rowi in range(nrows):
            self.__widgets.append([])
            for coli in range(ncols):
                self.__widgets[-1].append(wx.Panel(self.__gridPanel))

        for rowi in range(nrows):
            lbl = wx.StaticText(self)
            self.__rowLabels.append(lbl)

        for coli in range(ncols):
            lbl = wx.StaticText(self)
            self.__colLabels.append(lbl)
        
        self.__gridPanel.SetSizer(self.__gridSizer)
        self.__refresh()

    
    def ClearGrid(self):

        if self.__gridSizer is not None:
            self.__gridSizer.Clear()
            
            for lbl in self.__rowLabels + self.__colLabels:
                lbl.Destroy()
                
            for row in self.__widgets:
                for widget in row:
                    widget.Destroy()

        self.__gridSizer = None
        self.__nrows     = 0
        self.__ncols     = 0
        self.__widgets   = []
        self.__rowLabels = []
        self.__colLabels = []

        self.__gridPanel.SetSizer(None)
        self.__refresh()


    def SetText(self, row, col, text):

        txt = wx.StaticText(self.__gridPanel, label=text)
        self.SetWidget(row, col, txt)


    def SetWidget(self, row, col, widget):
        if row <  0            or \
           col <  0            or \
           row >= self.__nrows or \
           col >= self.__ncols:
            raise ValueError('Grid location ({}, {}) out of bounds ({}, {})'.
                             format(row, col, self.__nrows, self.__ncols))

        widget.Reparent(self.__gridPanel)

        if self.__widgets[row][col] is not None:
            self.__widgets[row][col].Destroy()

        self.__widgets[row][col] = widget

        self.__refresh()
    

    def ShowRowLabels(self, show=True):
        self.__showRowLabels = show
        self.__refresh()

    
    def ShowColLabels(self, show=True):
        self.__showColLabels = show
        self.__refresh()
    
    
    def SetRowLabel(self, row, label):
        if row < 0 or row >= self.__nrows:
            raise ValueError('Row {} out of bounds ({})'.format(
                row, self.__nrows))

        self.__rowLabels[row].SetLabel(label)

    
    def SetColLabel(self, col, label):
        if col < 0 or col >= self.__ncols:
            raise ValueError('Column {} out of bounds ({})'.format(
                col, self.__ncols))

        self.__colLabels[col].SetLabel(label)
