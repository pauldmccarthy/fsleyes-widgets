#!/usr/bin/env python
#
# notebook.py - Re-implementation of the wx.Notebook widget
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""This module provides the :class:`Notebook` class, a notebook control
similar to the :class:`wx.Notebook`.
"""


import                              wx
import wx.lib.newevent           as wxevent
import fsleyes_widgets.textpanel as textpanel


class Notebook(wx.Panel):
    """A :class:`wx.Panel` which provides :class:`wx.Notebook`-like
    functionality. Manages the display of multiple child windows. A row of
    buttons along one side allows the user to select which child window to
    display.

    This :class:`Notebook` implementation supports page enabling/disabling, and
    toggling of page visibility.
    """

    def __init__(self, parent, style=None, border=5):
        """Create a :class:`Notebook` object.

        The side on which the notebook page buttons will be displayed can be
        controlled by setting one of ``wx.TOP`` (the default), ``wx.BOTTOM``,
        ``wx.LEFT``, or ``wx.RIGHT`` on the ``style`` flags.

        The orientation of the page buttons can be set to either horizontal
        (the default) or vertical by setting one of ``wx.HORIZONTAL`` or
        ``wx.VERTICAL`` on the ``style`` flags.

        :arg parent: The :mod:`wx` parent object.

        :arg style:  Passed to ``wx.Panel.__init__``. If not provided,
                     defaults to ``wx.TOP | wx.HORIZONTAL | wx.SUNKEN_BORDER``.

        :arg border: Border (in pixels) around pages. Defaults to 5.
        """

        if style is None:
            style = wx.TOP | wx.HORIZONTAL | wx.SUNKEN_BORDER

        if   style & wx.LEFT:   btnside = wx.LEFT
        elif style & wx.RIGHT:  btnside = wx.RIGHT
        elif style & wx.BOTTOM: btnside = wx.BOTTOM
        else:                   btnside = wx.TOP

        if style & wx.VERTICAL: textorient = wx.VERTICAL
        else:                   textorient = wx.HORIZONTAL

        if btnside in (wx.TOP, wx.BOTTOM):
            btnorient    = wx.HORIZONTAL
            invbtnorient = wx.VERTICAL
            borderflags  = btnside | wx.LEFT | wx.RIGHT
        else:
            btnorient    = wx.VERTICAL
            invbtnorient = wx.HORIZONTAL
            borderflags  = btnside | wx.TOP | wx.BOTTOM

        style &= (~textorient & ~btnside)

        wx.Panel.__init__(self, parent, style=style)

        self.__border        = border
        self.__borderflags   = borderflags
        self.__btnside       = btnside
        self.__btnorient     = btnorient
        self.__invbtnorient  = invbtnorient
        self.__textorient    = textorient
        self.__textColour    = None
        self.__defaultColour = None
        self.__selectColour  = '#ffffff'
        self.__buttonPanel   = wx.Panel(self)
        self.__sizer         = wx.BoxSizer(invbtnorient)
        self.__buttonSizer   = wx.BoxSizer(btnorient)

        self.              SetSizer(self.__sizer)
        self.__buttonPanel.SetSizer(self.__buttonSizer)

        self.__dividerLine = wx.StaticLine(self, style=btnorient)

        # a horizontal line separating the buttons from the pages
        self.__sizer.Add(
            self.__dividerLine,
            border=self.__border,
            flag=wx.EXPAND | wx.ALIGN_CENTER | borderflags & ~btnside)

        # a row of buttons for each page
        if btnside in (wx.TOP, wx.LEFT): idx = 0
        else:                            idx = 1
        self.__sizer.Insert(
            idx,
            self.__buttonPanel,
            border=self.__border,
            flag=wx.EXPAND | wx.ALIGN_CENTER | self.__borderflags)

        # a vertical line at the start of the button row
        self.__buttonSizer.Insert(
            0,
            wx.StaticLine(self.__buttonPanel, style=invbtnorient),
            border=3,
            flag=wx.EXPAND | wx.ALIGN_CENTER | borderflags)

        self.__pages    = []
        self.__buttons  = []
        self.__selected = None


    @property
    def pages(self):
        """Returns a list containing references to all of the pages in this
        ``Notebook``.
        """
        return list(self.__pages)


    @property
    def buttons(self):
        """Returns a list containing references to all of the page buttons in
        this ``Notebook``.
        """
        return list(self.__buttons)


    def __updateMinSize(self):
        """Calculate and return the best (minimum) size for this
        :class:`Notebook` instance.

        The returned size is the minimum size of the largest page, plus the
        size of the button panel.
        """

        btnside = self.__btnside
        border  = self.__border

        buttonSize = self.__buttonPanel.GetBestSize()
        pageSizes  = [p.GetBestSize() for p in self.__pages]

        buttonWidth  = buttonSize[0]
        buttonHeight = buttonSize[1]

        divLineWidth, divLineHeight = self.__dividerLine.GetMinSize()

        if len(pageSizes) > 0:
            pageWidths  = [ps[0] for ps in pageSizes]
            pageHeights = [ps[1] for ps in pageSizes]
        else:
            pageWidths  = [0]
            pageHeights = [0]

        if btnside in (wx.TOP, wx.BOTTOM):
            myWidth  = max([buttonWidth] + pageWidths)
            myHeight = max(pageHeights) + buttonHeight + divLineHeight
        else:
            myWidth  = max(pageWidths) + buttonWidth + divLineWidth
            myHeight = max([buttonHeight] + pageHeights)

        # The border is applied once to
        # the button panel, and on both
        # sides of the page. And we add
        # two 2 for good luck.
        self.SetMinSize((myWidth + border, myHeight + border * 3 + 2))


    def SetButtonColours(self, **kwargs):
        """Set the colours used for the notebook page buttons. Set any colour
        to ``None`` to use the default colours.  All arguments must be passed
        as keyword arguments.

        :arg text:     Text colour
        :arg default:  Default (unselected) background colour.
        :arg selected: Selected background colour.
        """

        text     = kwargs.pop('text',     None)
        default  = kwargs.pop('default',  None)
        selected = kwargs.pop('selected', '#ffffff')

        self.__textColour    = text
        self.__defaultColour = default
        self.__selectColour  = selected

        if self.PageCount() > 0:
            self.SetSelection(self.GetSelection())


    def PageCount(self):
        """Returns the number of pages in this ``Notebook``. """
        return len(self.__pages)


    def FindPage(self, page):
        """Returns the index of the given page, or :data:`wx.NOT_FOUND`
        if the page is not in this notebook.
        """
        try:               return self.__pages.index(page)
        except ValueError: return wx.NOT_FOUND


    def InsertPage(self, index, page, text):
        """Inserts the given page into the notebook at the specified index. A
        button for the page is also added to the button row, with the specified
        text.
        """

        if (index > len(self.__pages)) or (index < 0):
            raise IndexError('Index out of range: {}'.format(index))

        page.Reparent(self)

        # index * 2 because we add a vertical
        # line after every button (and + 1 for
        # the line at the start of the button
        # row). We set the button ID to be its
        # index, so the event handler can look
        # up the corresponding notebook page.
        buttonIdx = index * 2 + 1
        button    = textpanel.TextPanel(self.__buttonPanel,
                                        text,
                                        orient=self.__textorient,
                                        id=index)

        self.__pages.  insert(index, page)
        self.__buttons.insert(index, button)

        # index + 2 to account for the button panel and
        # the horizontal divider line (see __init__)
        if self.__btnside in (wx.TOP, wx.LEFT):
            index = index + 2
        self.__sizer.Insert(
            index,
            page,
            border=self.__border,
            flag=wx.EXPAND | wx.ALL, proportion=1)

        self.__buttonSizer.Insert(
            buttonIdx,
            button,
            flag=wx.ALIGN_CENTER)

        # A vertical line at the end of every button
        self.__buttonSizer.Insert(
            buttonIdx + 1,
            wx.StaticLine(self.__buttonPanel, style=self.__invbtnorient),
            border=3,
            flag=wx.EXPAND | wx.ALIGN_CENTER | self.__borderflags)

        button.Bind(wx.EVT_LEFT_DOWN, self.__onButton)

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

        if self.__btnside in (wx.TOP, wx.LEFT):
            pageIdx = index + 2
        else:
            pageIdx = index

        self.__buttons.pop(index)
        self.__pages  .pop(index)

        # Destroy the button for this page (and the
        # vertical line that comes after the button)
        self.__buttonSizer.Remove(buttonIdx)
        self.__buttonSizer.Remove(buttonIdx)

        # Remove the page but do not destroy it
        self.__sizer.Detach(pageIdx)

        npages = self.PageCount()
        newsel = self.__selected

        if npages == 0:
            newsel = None
        elif newsel >= npages:
            newsel = npages - 1

        self.SetSelection(newsel)
        self.__updateMinSize()


    def DeletePage(self, index):
        """Removes the page at the specified index, and (attempts to) destroy
        it.
        """
        page = self.__pages[index]
        self.RemovePage(index)
        page.Destroy()


    def GetSelection(self):
        """Returns the index of the currently selected page, or ``None`` if
        there are no pages.
        """
        return self.__selected


    def SetSelection(self, index):
        """Sets the displayed page to the one at the specified index."""

        if self.PageCount() == 0:
            self.__selected = None
            return

        if index < 0 or index >= len(self.__pages):
            raise IndexError('Index out of range: {}'.format(index))

        self.__selected = index

        for i in range(len(self.__pages)):

            page     = self.__pages[  i]
            button   = self.__buttons[i]
            showThis = i == self.__selected

            button.SetForegroundColour(self.__textColour)

            if showThis:
                button.SetBackgroundColour(self.__selectColour)
                page.Show()
            else:
                button.SetBackgroundColour(self.__defaultColour)
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

            newSelection = (newSelection + offset) % len(self.__pages)

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


    def __onButton(self, ev):
        """Called when a page button is pushed. Selects the respective page,
        and emits a :data:`PageChangeEvent`.
        """

        button  = ev.GetEventObject()
        pageIdx = button.GetId()

        if not button.IsEnabled():             return
        if     self.GetSelection() == pageIdx: return

        self.SetSelection(pageIdx)

        wx.PostEvent(self, PageChangeEvent(index=pageIdx))


_PageChangeEvent, _EVT_PAGE_CHANGE = wxevent.NewEvent()


EVT_PAGE_CHANGE = _EVT_PAGE_CHANGE
"""Identifier for the :data:`PageChangeEvent` event. """


PageChangeEvent = _PageChangeEvent
"""Event emitted when the page is changed by the user. A ``PageChangeEvent``
has the following attributes:

  - ``index`` The index of the page that was selected.
"""
