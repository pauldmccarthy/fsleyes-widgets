#!/usr/bin/env python
#
# notebook.py - Re-implementation of the wx.Notebook widget
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""This module provides the :class:`Notebook` class, a notebook control
similar to the :class:`wx.Notebook`.
"""


import wx
import wx.lib.stattext as statictext


class Notebook(wx.Panel):
    """A :class:`wx.Panel` which provides :class:`wx.Notebook`-like
    functionality. Manages the display of multiple child windows. A row of
    buttons along the top allows the user to select which child window to
    display.

    This :class:`Notebook` implementation supports page enabling/disabling, and
    toggling of page visibility.
    """

    def __init__(self, parent):
        """Create a :class:`Notebook` object.

        :arg parent: The :mod:`wx` parent object.
        """

        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)

        self.__buttonPanel = wx.Panel(self)

        self.__sizer       = wx.BoxSizer(wx.VERTICAL)
        self.__buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.              SetSizer(self.__sizer)
        self.__buttonPanel.SetSizer(self.__buttonSizer)

        self.__dividerLine = wx.StaticLine(self, style=wx.LI_HORIZONTAL)

        # a row of buttons along the top
        self.__sizer.Add(
            self.__buttonPanel,
            border=5,
            flag=wx.EXPAND | wx.ALIGN_CENTER | wx.TOP | wx.RIGHT | wx.LEFT)

        # a horizontal line separating the buttons from the pages
        self.__sizer.Add(
            self.__dividerLine,
            border=5,
            flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT)

        # a vertical line at the start of the button row
        self.__buttonSizer.Insert(
            0,
            wx.StaticLine(self.__buttonPanel, style=wx.VERTICAL),
            border=3,
            flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP)

        self.__pages    = []
        self.__buttons  = []
        self.__selected = None


    def __updateMinSize(self):
        """Calculate and return the best (minimum) size for this
        :class:`Notebook` instance.

        The returned size is the minimum size of the largest page, plus the
        size of the button panel.
        """

        buttonSize = self.__buttonPanel.GetBestSize()
        pageSizes  = [p.GetBestSize() for p in self.__pages]

        buttonWidth  = buttonSize[0]
        buttonHeight = buttonSize[1]

        divLineHeight = self.__dividerLine.GetMinSize()[0]

        pageWidths  = [ps[0] for ps in pageSizes]
        pageHeights = [ps[1] for ps in pageSizes]

        myWidth  = max([buttonWidth] + pageWidths)                 + 20
        myHeight = max(pageHeights) + buttonHeight + divLineHeight + 20

        self.SetMinSize((myWidth, myHeight))


    def FindPage(self, page):
        """Returns the index of the given page, or :data:`wx.NOT_FOUND`
        if the page is not in this notebook.
        """
        try:    return self.__pages.index(page)
        except: return wx.NOT_FOUND


    def InsertPage(self, index, page, text):
        """Inserts the given page into the notebook at the specified index. A
        button for the page is also added to the button row, with the specified
        text.
        """

        if (index > len(self.__pages)) or (index < 0):
            raise IndexError('Index out of range: {}'.format(index))

        # index * 2 because we add a vertical
        # line after every button (and + 1 for
        # the line at the start of the button row)
        button    = statictext.GenStaticText(self.__buttonPanel, label=text)
        buttonIdx = index * 2 + 1

        self.__pages.  insert(index, page)
        self.__buttons.insert(index, button)

        # index + 2 to account for the button panel and
        # the horizontal divider line (see __init__)
        self.__sizer.Insert(
            index + 2, page, border=5, flag=wx.EXPAND | wx.ALL, proportion=1)

        self.__buttonSizer.Insert(
            buttonIdx,
            button,
            flag=wx.ALIGN_CENTER)

        # A vertical line at the end of every button
        self.__buttonSizer.Insert(
            buttonIdx + 1,
            wx.StaticLine(self.__buttonPanel, style=wx.VERTICAL),
            border=3,
            flag=wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP)

        # When the button is pushed, show the page
        # (unless the button has been disabled)
        def _showPage(ev):
            if not button.IsEnabled(): return
            self.SetSelection(self.FindPage(page))

        button.Bind(wx.EVT_LEFT_DOWN, _showPage)

        if self.__selected is None:
            self.__selected = 0
        self.SetSelection(self.__selected)

        page.Layout()
        self.__buttonPanel.Layout()
        self.Layout()

        self.__updateMinSize()


    def AddPage(self, page, text):
        """Adds the given page (and a corresponding button with the given
        text) to the end of the notebook.
        """
        self.InsertPage(len(self.__pages), page, text)


    def RemovePage(self, index):
        """Removes the page at the specified index, but does not destroy it.
        """

        if (index >= len(self.__pages)) or (index < 0):
            raise IndexError('Index out of range: {}'.format(index))

        buttonIdx = index * 2 + 1
        pageIdx   = index + 2

        self.__buttons.pop(index)
        self.__pages  .pop(index)

        # Destroy the button for this page (and the
        # vertical line that comes after the button)
        self.__buttonSizer.Remove(buttonIdx)
        self.__buttonSizer.Remove(buttonIdx + 1)

        # Remove the page but do not destroy it
        self.__pagePanel.Detach(pageIdx)

        if len(self.__pages) == 0:
            self.__selected = None

        self.__updateMinSize()


    def DeletePage(self, index):
        """Removes the page at the specified index, and (attempts to) destroy
        it.
        """
        page = self.__pages[index]
        self.RemovePage(index)
        page.Destroy()


    def GetSelection(self):
        """Returns the index of the currently selected page."""
        return self.__selected


    def SetSelection(self, index):
        """Sets the displayed page to the one at the specified index."""

        if index < 0 or index >= len(self.__pages):
            raise IndexError('Index out of range: {}'.format(index))

        self.__selected = index

        for i in range(len(self.__pages)):

            page     = self.__pages[  i]
            button   = self.__buttons[i]
            showThis = i == self.__selected

            if showThis:
                button.SetBackgroundColour('#ffffff')
                page.Show()
            else:
                button.SetBackgroundColour(None)
                page.Hide()

        button.Layout()
        self.__buttonPanel.Layout()
        self.Layout()
        self.Refresh()


    def AdvanceSelection(self, forward=True):
        """Selects the next (or previous, if ``forward``
        is ``False``) enabled page.
        """

        if forward: offset =  1
        else:       offset = -1

        newSelection = (self.GetSelection() + offset) % len(self.__pages)

        while newSelection != self.__selected:

            if self.__buttons[newSelection].IsEnabled():
                break

            newSelection = (self.__selected + offset) % len(self.__pages)

        self.SetSelection(newSelection)


    def EnablePage(self, index):
        """Enables the page at the specified index."""
        self.__buttons[index].Enable()


    def DisablePage(self, index):
        """Disables the page at the specified index."""
        self.__buttons[index].Disable()

        if self.GetSelection() == index:
            self.AdvanceSelection()

        self.Refresh()


    def ShowPage(self, index):
        """Shows the page at the specified index."""
        self.EnablePage(index)
        self.__buttons[index].Show()
        self.__pages[  index].Show()
        self.__buttonPanel.Layout()
        self.Refresh()


    def HidePage(self, index):
        """Hides the page at the specified index."""

        self.__buttons[index].Hide()
        self.__pages[  index].Hide()

        # we disable the page as well as hiding it,, as the
        # AdvanceSelection method, and button handlers, use
        # button.IsEnabled to determine whether a page is
        # active or not.
        self.DisablePage(index)

        self.__buttonPanel.Layout()
        self.__buttonPanel.Refresh()
