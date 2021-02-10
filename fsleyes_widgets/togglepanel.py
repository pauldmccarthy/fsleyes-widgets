#!/usr/bin/env python
#
# togglepanel.py - A panel which contains a button, and some content.
# Pushing the button toggles the visibility of the content.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`TogglePanel` class, which is a panel that
contains a button and some content. Pushing the button toggles the visibility
of the content.
"""


import warnings

import wx
import wx.lib.newevent as wxevent


class TogglePanel(wx.Panel):
    """A :class:`TogglePanel` is a ``wx.Panel`` that contains a button and
    some content.

    Pushing the button toggles the visibility of the content.


    All of the content should be added to the panel which is returned by the
    :meth:`GetPane` method.


    The ``TogglePanel`` may be used in place of the ``wx.CollapsiblePane``,
    which is buggy under Linux/GTK.
    """


    def __init__(self,
                 parent,
                 toggleSide=wx.TOP,
                 initialState=True,
                 label=None):
        """Create a :class:`TogglePanel`.

        :arg parent:       The :mod:`wx` parent object.

        :arg toggleSide:   Which side to place the toggle button. Must be one
                           of :attr:`wx.TOP`, :attr:`wx.BOTTOM`,
                           :attr:`wx.LEFT`, or :attr:`wx.RIGHT`.

        :arg initialState: Initial state for the panel content - visible
                           (``True``) or hidden (``False``).

        :arg label:        A label to be displayed on the toggle button.
        """

        wx.Panel.__init__(self, parent)

        self.__contentPanel = wx.Panel(self)

        if toggleSide in (wx.TOP, wx.BOTTOM):
            self.__mainSizer   = wx.BoxSizer(wx.VERTICAL)
            self.__toggleSizer = wx.BoxSizer(wx.HORIZONTAL)

        elif toggleSide in (wx.LEFT, wx.RIGHT):
            self.__mainSizer   = wx.BoxSizer(wx.HORIZONTAL)
            self.__toggleSizer = wx.BoxSizer(wx.VERTICAL)

        else:
            raise ValueError('toggleSide must be one of wx.TOP, '
                             'wx.BOTTOM, wx.LEFT or wx.RIGHT')

        self.__toggleButton = wx.StaticText(
            self,
            style=(wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL))

        if   toggleSide == wx.TOP:    hideLabel = '\u25B2'
        elif toggleSide == wx.BOTTOM: hideLabel = '\u25BC'
        elif toggleSide == wx.LEFT:   hideLabel = '\u25C0'
        elif toggleSide == wx.RIGHT:  hideLabel = '\u25B6'

        if   toggleSide == wx.TOP:    showLabel = '\u25BC'
        elif toggleSide == wx.BOTTOM: showLabel = '\u25B2'
        elif toggleSide == wx.LEFT:   showLabel = '\u25B6'
        elif toggleSide == wx.RIGHT:  showLabel = '\u25C0'

        self.__showLabel = showLabel
        self.__hideLabel = hideLabel
        self.__label     = label
        self.__state     = not initialState

        self.__toggleSizer.Add(self.__toggleButton, flag=wx.EXPAND)
        self.__toggleSizer.Add((1, 1), flag=wx.EXPAND, proportion=1)

        if toggleSide in (wx.TOP, wx.LEFT):
            self.__mainSizer.Add(self.__toggleSizer,
                                 flag=wx.EXPAND | wx.ALL,
                                 border=2)
            self.__mainSizer.Add(self.__contentPanel,
                                 flag=wx.EXPAND,
                                 proportion=1)

        elif toggleSide in (wx.BOTTOM, wx.RIGHT):
            self.__mainSizer.Add(self.__contentPanel,
                                 flag=wx.EXPAND,
                                 proportion=1)
            self.__mainSizer.Add(self.__toggleSizer,
                                 flag=wx.EXPAND | wx.ALL,
                                 border=2)

        self.__toggleButton.Bind(wx.EVT_LEFT_DOWN, self.Toggle)

        self.SetSizer(self.__mainSizer)
        self.Expand(initialState)


    @property
    def button(self):
        """Returns the toggle button (actually a ``wx.StaticText``). This
        is for testing purposes.
        """
        return self.__toggleButton


    def __refresh(self):
        """Refreshes the layout. """
        self.Layout()
        self.__contentPanel.Layout()


    def __expand(self, expand=True, force=False):
        """Expands or collapses the content panel.

        :arg expand: ``True`` to expand, ``False`` to collapse.

        :arg force:  If ``True``, the panel is re-configured, regardless of
                     whether it is already in the requested expanded/collapsed
                     state.
        """

        if not force and self.IsExpanded() == expand:
            return

        self.__mainSizer.Show(self.__contentPanel, expand)

        if expand: label = self.__hideLabel
        else:      label = self.__showLabel

        if self.__label is not None:
            label = '{} {}'.format(label, self.__label)

        self.__state = expand
        self.__toggleButton.SetLabel(label)
        self.__refresh()


    def SetLabel(self, label):
        """Sets the label to show on the toggle button. Pass in ``None``
        for no label.
        """
        self.__label = label
        self.__expand(self.IsExpanded(), force=True)


    def GetLabel(self):
        """Returns the current toggle button label """
        return self.__label


    def GetToggleButton(self):
        """Returns the toggle button (actually a ``wx.StaticText``). This
        is for testing purposes.
        """
        warnings.warn('GetToggleButton is deprecated - use button instead',
                      category=DeprecationWarning,
                      stacklevel=2)

        return self.__toggleButton


    def Expand(self, expand=True):
        """Expand the content pane.

        :arg expand: ``True`` to expand, ``False`` to collapse.
        """
        self.__expand(expand)


    def Collapse(self):
        """Collapse the content pane. """
        self.Expand(False)


    def IsExpanded(self):
        """Return ``True`` if the content pane is currently expanded,
        ``False`` otherwise.
        """
        return self.__state


    def Toggle(self, ev=None):
        """Toggles visibility of the panel content.

        This method is called when the button is pushed. If ``ev`` is not
        ``None``, an ``EVT_TOGGLEPANEL_EVENT`` is generated.
        """

        newState = not self.IsExpanded()

        self.Expand(newState)

        if ev is not None:
            ev = TogglePanelEvent(newState=newState)
            ev.SetEventObject(self)
            wx.PostEvent(self, ev)


    def GetPane(self):
        """Returns the :class:`wx.Panel` to which all content should be
        added.
        """
        return self.__contentPanel


_TogglePanelEvent, _EVT_TOGGLEPANEL_EVENT = wxevent.NewEvent()


EVT_TOGGLEPANEL_EVENT = _EVT_TOGGLEPANEL_EVENT
"""Identifier for the :data:`TogglePanelEvent` event."""


TogglePanelEvent = _TogglePanelEvent
"""Event emitted when the toggle button is pushed. Contains the
following attributes:

  - ``newState``: The new visibility state of the toggle panel - ``True``
                  corresponds to visible, ``False`` to invisible.
"""
