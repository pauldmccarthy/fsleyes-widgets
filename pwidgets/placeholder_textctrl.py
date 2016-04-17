#!/usr/bin/env python
#
# placeholder_textctrl.py - The PlaceholderTextCtrl class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`PlaceholderTextCtrl` which is a
``wx.TextCtrl`` that displays some placeholder text when it is empty
and unfocused.
"""


import wx


class PlaceholderTextCtrl(wx.TextCtrl):
    """the :class:`PlaceholderTextCtrl` is a ``wx.TextCtrl`` that displays
    some placeholder text when it is empty and unfocused.

    I wrote this class as a substitute for the ``wx.SearchCtrl`` which, under
    OSX Cocoa (wxPython 3.0.2.0) has focusing bugs that make it unusable.
    """


    def __init__(self, *args, **kwargs):
        """Create a ``PlaceholderTextCtrl``.

        :arg placeholder:       The text to display when the control is empty 
                                and unfocused.

        :arg placeholderColour: Colour to display the placeholder text in.

        All other arguments are passed to ``wx.TextCtrl.__init__``.
        """

        placeholder       = str(kwargs.pop('placeholder', ''))
        placeholderColour =     kwargs.pop('placeholderColour',
                                           (150, 150, 150))

        self.__fgColour = (0, 0, 0)

        wx.TextCtrl.__init__(self, *args, **kwargs)

        self.SetPlaceholder(      placeholder)
        self.SetPlaceholderColour(placeholderColour)

        self.Bind(wx.EVT_SET_FOCUS,  self.__onSetFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.__onKillFocus)

        self.__onKillFocus(None)


    def GetPlaceholder(self):
        """Returns the place holder text. """
        return self.__placeholder


    def GetPlaceholderColour(self):
        """Returns the placeholder text colour."""
        return self.__placeholderColour


    
    def SetPlaceholder(self, placeholder):
        """Sets the placeholder text. """

        if placeholder is None:
            placeholder = ''

        self.__placeholder = str(placeholder)


    def SetPlaceholderColour(self, colour):
        """Sets the placeholder text colour. """

        colour = list(colour)
        
        if len(colour) != 3:
            raise ValueError('Colour must be an RGB sequence')

        for i, c in enumerate(colour):
            
            if c < 0:   c = 0
            if c > 255: c = 255

            colour[i] = c

        self.__placeholderColour = colour


    def __onSetFocus(self, ev):
        """Called when this ``PlaceholderTextCtrl`` gains focus.

        Clears the placeholder text if necessary.
        """
        ev.Skip()
        if self.GetValue() == self.__placeholder:
            self.SetForegroundColour(self.__fgColour)
            self.SetValue(           '')

        
    def __onKillFocus(self, ev):
        """Called when this ``PlaceholderTextCtrl`` loses focus.

        Displays the placeholder text if necessary.
        """ 
        if ev is not None:
            ev.Skip()

        if self.GetValue().strip() == '':
            self.__fgColour = self.GetForegroundColour()
            self.SetValue(           self.__placeholder)
            self.SetForegroundColour(self.__placeholderColour)
