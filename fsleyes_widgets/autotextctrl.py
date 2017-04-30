#!/usr/bin/env python
#
# autotextctrl.py - The AutoTextCtrl class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`AutoTextCtrl` class, an alternative to the
``wx.TextCtrl``, which has auto-completion capability.

I wrote this class because ``wx.TextCtrl`` auto-completion does not work under
OSX, and the ``wx.ComboBox`` does not give me enough fine-grained control with
respect to managing focus.
"""


import logging

import wx
import wx.lib.newevent as wxevent


log = logging.getLogger(__name__)


class AutoTextCtrl(wx.Panel):
    """The ``AutoTextCtrl`` class is essentially a ``wx.TextCtrl`` which is able
    to dynamically show a list of options to the user, with a
    :class:`AutoCompletePopup`.
    """


    def __init__(self, parent, style=0):
        """Create an ``AutoTextCtrl``.

        :arg parent: The ``wx`` parent object.
        :arg style:  Can be :data:`ATC_CASE_SENSITIVE` to restrict the
                     auto-completion options to case sensitive matches.
        """

        self.__caseSensitive = style & ATC_CASE_SENSITIVE

        wx.Panel.__init__(self, parent)

        self.__textCtrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.__sizer    = wx.BoxSizer(wx.HORIZONTAL)

        self.__sizer.Add(self.__textCtrl, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)

        # The takeFocus flag is set by SetTakeFocus,
        # and used in __showPopup. The options array
        # contains the auto complete options.
        self.__takeFocus = False
        self.__options   = []

        self.__textCtrl.Bind(wx.EVT_TEXT,        self.__onText)
        self.__textCtrl.Bind(wx.EVT_LEFT_DCLICK, self.__onDoubleClick)
        self.__textCtrl.Bind(wx.EVT_TEXT_ENTER,  self.__onEnter)
        self.__textCtrl.Bind(wx.EVT_KEY_DOWN,    self.__onKeyDown)
        self.__textCtrl.Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self           .Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)


    def __onSetFocus(self, ev):
        """Called when this ``AutoTextCtrl`` or any of its children gains
        focus. Makes sure that the text control insertion point is at the
        end of its current contents.
        """

        ev.Skip()

        log.debug('Text control gained focus: {}'.format(
            wx.Window.FindFocus()))

        # Under wx/GTK, when a text control gains focus,
        # it seems to select its entire contents, meaning
        # that when the user types  something, the current
        # contents are replaced with the new contents. To
        # prevent this, here we make sure that no text is
        # selected, and the insertion point is at the end
        # of the current contents.
        text = self.__textCtrl.GetValue()
        self.__textCtrl.SetSelection(len(text) - 1, len(text) - 1)
        self.__textCtrl.SetInsertionPointEnd()


    @property
    def textCtrl(self):
        """Returns a reference to the internal ``wx.TextCtrl``. """
        return self.__textCtrl


    def AutoComplete(self, options):
        """Set the list of options to be shown to the user. """
        self.__options = list(options)


    def GetValue(self):
        """Returns the current value shown on this ``AutoTextCtrl``. """
        return self.__textCtrl.GetValue()


    def SetValue(self, value):
        """Sets the current value shown on this ``AutoTextCtrl``.

        .. note:: Calling this method will result in an ``wx.EVT_TEXT``
                  event being generated - use :meth:`ChangeValue` if you
                  do not want this to occur.
        """
        self.__textCtrl.SetValue(value)


    def ChangeValue(self, value):
        """Sets the current value shown on this ``AutoTextCtrl``. """
        self.__textCtrl.ChangeValue(value)


    def GetInsertionPoint(self):
        """Returns the cursor location in this ``AutoTextCtrl``. """
        return self.__textCtrl.GetInsertionPoint()


    def SetInsertionPoint(self, idx):
        """Sets the cursor location in this ``AutoTextCtrl``. """
        self.__textCtrl.SetInsertionPoint(idx)


    def GenEnterEvent(self):
        """Programmatically generates an :data:`EVT_ATC_TEXT_ENTER` event. """
        self.__onEnter(None)


    def SetTakeFocus(self, takeFocus):
        """If ``takeFocus`` is ``True``, this ``AutoTextCtrl`` will give
        itself focus when its ``AutoCompletePopup`` is closed.
        """
        self.__takeFocus = takeFocus


    def __onKeyDown(self, ev):
        """Called on ``EVT_KEY_DOWN`` events in the text control. """

        enter = wx.WXK_RETURN
        key   = ev.GetKeyCode()

        log.debug('Key event on text control: {}'.format(key))

        # Make sure the event is propagated
        # up the window hierarchy, if we skip it
        ev.ResumePropagation(wx.EVENT_PROPAGATE_MAX)

        if key != enter:
            ev.Skip()
            return

        if self.GetValue() == '':
            log.debug('Enter/right arrow - displaying all options')
            self.__showPopup('')

        # Let the text control handle the event normally
        else:
            ev.Skip()


    def __onDoubleClick(self, ev):
        """Called when the user double clicks in this ``AutoTextCtrl``.
        Creates an :class:`AutoCompletePopup`.
        """
        log.debug('Double click on text control - simulating text entry')
        self.__onText(None)


    def __onText(self, ev):
        """Called when the user changes the text shown on this ``AutoTextCtrl``.
        Creates an :class:`AutoCompletePopup`.
        """

        text = self.__textCtrl.GetValue()
        log.debug('Text - displaying options matching "{}"'.format(text))
        self.__showPopup(text)


    def __onEnter(self, ev):
        """Called when the user presses enter in this ``AutoTextCtrl``. Generates
        an :data:`EVT_ATC_TEXT_ENTER` event.
        """
        value = self.__textCtrl.GetValue()
        ev = AutoTextCtrlEnterEvent(text=value)

        log.debug('Enter - generating ATC enter '
                  'event (text: "{}")'.format(value))

        wx.PostEvent(self, ev)


    def __showPopup(self, text):
        """Creates an :class:`AutoCompletePopup` which displays a list of
        auto-completion options, matching the given prefix text, to the user.

        The popup is not displayed if there are no options with the given
        prefix.
        """

        text            = text.strip()
        style           = 0

        if self.__caseSensitive:
            style |= ATC_CASE_SENSITIVE

        popup = AutoCompletePopup(
            self,
            self,
            text,
            self.__options,
            style)

        if popup.GetCount() == 0:
            popup.Destroy()
            return

        # Don't take focus unless the AutoCompletePopup
        # tells us to (it will call the SetTakeFocus method)
        self.__takeFocus = False

        # Make sure we get the focus back
        # when the popup is destroyed
        def refocus(ev):

            # A call to Raise is required under
            # GTK, as otherwise the main window
            # won't be given focus.
            if wx.Platform == '__WXGTK__':
                self.GetTopLevelParent().Raise()

            if self.__takeFocus:
                self.__textCtrl.SetFocus()

        popup.Bind(wx.EVT_WINDOW_DESTROY, refocus)

        # The popup has its own textctrl - we
        # position the popup so that its textctrl
        # is displayed on top of our textctrl,
        # with the option list underneath.
        posx, posy = self.__textCtrl.GetScreenPosition().Get()

        popup.SetSize((-1, -1))
        popup.SetPosition((posx,  posy))
        popup.Show()


ATC_CASE_SENSITIVE = 1
"""Syle flag for use with the :class:`AutoTextCtrl` class. If set, the
auto-completion pattern matching will be case sensitive.
"""


_AutoTextCtrlEnterEvent, _EVT_ATC_TEXT_ENTER = wxevent.NewEvent()


EVT_ATC_TEXT_ENTER = _EVT_ATC_TEXT_ENTER
"""Identifier for the :data:`AutoTextCtrlEnterEvent`, which is generated
when the user presses enter in an :class:`AutoTextCtrl`.
"""


AutoTextCtrlEnterEvent = _AutoTextCtrlEnterEvent
"""Event generated when the user presses enter in an :class:`AutoTextCtrl`.
Contains a single attribute, ``text``, which contains the text in the
``AutoTextCtrl``.
"""


class AutoCompletePopup(wx.Frame):
    """The ``AutoCompletePopup`` class is used by the :class:`AutoTextCtrl`
    to display a list of completion options to the user.
    """

    def __init__(self, parent, atc, text, options, style=0):
        """Create an ``AutoCompletePopup``.

        :arg parent:  The ``wx`` parent object.
        :arg atc:     The :class:`AutoTextCtrl` that is using this popup.
        :arg text:    Initial text value.
        :arg options: A list of all possible auto-completion options.
        :arg style:   Set to :data:`ATC_CASE_SENSITIVE` to make the
                      pattern matching case sensitive.
        """

        wx.Frame.__init__(self, parent, style=wx.NO_BORDER)

        self.__caseSensitive = style & ATC_CASE_SENSITIVE
        self.__atc           = atc
        self.__options       = options
        self.__textCtrl      = wx.TextCtrl(self,
                                           value=text,
                                           style=wx.TE_PROCESS_ENTER)
        self.__listBox       = wx.ListBox( self,
                                           style=(wx.LB_SINGLE))

        self.__listBox.Set(self.__getMatches(text))

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self.__textCtrl, flag=wx.EXPAND)
        self.__sizer.Add(self.__listBox,  flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)

        self.Layout()
        self.Fit()

        self.__textCtrl.Bind(wx.EVT_TEXT,           self.__onText)
        self.__textCtrl.Bind(wx.EVT_TEXT_ENTER,     self.__onEnter)
        self.__textCtrl.Bind(wx.EVT_KEY_DOWN,       self.__onKeyDown)
        self.__listBox .Bind(wx.EVT_KEY_DOWN,       self.__onListKeyDown)
        self.__listBox .Bind(wx.EVT_LISTBOX_DCLICK, self.__onListMouseDblClick)

        # Under GTK, the SetFocus/KillFocus event
        # objects often don't have a reference to
        # the window that received/is about to
        # receive focus. In particular, if the
        # list box is clicked, a killFocus event
        # is triggered, but the list box is not
        # passed in. So on mouse down events, we
        # force the list box to have focus.
        if wx.Platform == '__WXGTK__':
            self.__listBox .Bind(wx.EVT_LEFT_DOWN,  self.__onListMouseDown)
            self.__listBox .Bind(wx.EVT_RIGHT_DOWN, self.__onListMouseDown)

        self           .Bind(wx.EVT_KILL_FOCUS,     self.__onKillFocus)
        self.__textCtrl.Bind(wx.EVT_KILL_FOCUS,     self.__onKillFocus)
        self.__listBox .Bind(wx.EVT_KILL_FOCUS,     self.__onKillFocus)

        self           .Bind(wx.EVT_SET_FOCUS,     self.__onSetFocus)
        self.__textCtrl.Bind(wx.EVT_SET_FOCUS,     self.__onSetFocus)
        self.__listBox .Bind(wx.EVT_SET_FOCUS,     self.__onSetFocus)


    def GetCount(self):
        """Returns the number of auto-completion options currently available.
        """
        return self.__listBox.GetCount()


    def __onSetFocus(self, ev):
        """Called when this ``AutoCompletePopup`` or any of its children gains
        focus. Makes sure that the text control insertion point is at the end
        of its current contents.
        """

        ev.Skip()

        log.debug('Popup gained focus: {}'.format(ev.GetWindow()))

        # See note in AutoTextCtrl.__onSetFocus
        text = self.__textCtrl.GetValue()
        self.__textCtrl.SetSelection(len(text) - 1, len(text) - 1)
        self.__textCtrl.SetInsertionPointEnd()


    def __onKillFocus(self, ev):
        """Called when this ``AutoCompletePopup`` loses focus. Calls
        :meth:`__destroy`.
        """

        ev.Skip()

        focused = ev.GetWindow()

        log.debug('Kill focus event on popup: {}'.format(focused))

        objs = (self, self.__textCtrl, self.__listBox)

        if focused not in objs:
            log.debug('Focus lost - destroying popup')
            self.__destroy(False, False)


    def __destroy(self, genEnter=True, returnFocus=True):
        """Called by various event handlers. Copies the current value in
        this ``AutoCompletePopup`` to the owning :class:`AutoTextCtrl`,
        and then (asynchronously) destroys this ``AutoCompletePopup``.
        """
        value = self.__textCtrl.GetValue()
        idx   = self.__textCtrl.GetInsertionPoint()
        atc   = self.__atc

        # Under wx/GTK, we might still receive focus
        # events, which will trigger another call to
        # __destroy. So we remove all callbacks to
        # prevent this from happening.
        self           .Bind(wx.EVT_SET_FOCUS,  None)
        self.__textCtrl.Bind(wx.EVT_SET_FOCUS,  None)
        self.__listBox .Bind(wx.EVT_SET_FOCUS,  None)
        self           .Bind(wx.EVT_KILL_FOCUS, None)
        self.__textCtrl.Bind(wx.EVT_KILL_FOCUS, None)
        self.__listBox .Bind(wx.EVT_KILL_FOCUS, None)

        atc.ChangeValue(      value)
        atc.SetInsertionPoint(idx)

        # Tell the atc whether or not it
        # should take the focus when this
        # popup is destroyed.
        atc.SetTakeFocus(returnFocus)

        if genEnter:
            atc.GenEnterEvent()

        def destroy():
            try:
                self.Close()
                self.Destroy()

            except wx.PyDeadObjectError:
                pass

        wx.CallAfter(destroy)


    def __getMatches(self, prefix):
        """Returns a list of auto-completion options which match the given
        prefix.
        """

        prefix  = prefix.strip()
        options = self.__options

        if not self.__caseSensitive:
            prefix  = prefix.lower()
            options = [o.lower() for o in options]

        matches = [o.startswith(prefix) for o in options]

        return [o for o, m in zip(self.__options, matches) if m]


    def __onKeyDown(self, ev):
        """Called on an ``EVT_KEY_DOWN`` event from the text control. """

        up    = wx.WXK_UP
        down  = wx.WXK_DOWN
        esc   = wx.WXK_ESCAPE
        enter = wx.WXK_RETURN
        key   = ev.GetKeyCode()

        log.debug('Key down event on popup text control: {}'.format(key))

        if key not in (up, down, enter, esc):
            ev.ResumePropagation(wx.EVENT_PROPAGATE_MAX)
            ev.Skip()
            return

        # Absorb the up arrow
        if key == up:
            return

        # The user hitting enter/escape will result
        # in this popup being destroyed
        if key in (esc, enter):
            log.debug('Enter/escape on popup text '
                      'control - destroying popup')
            self.__destroy(key == enter)
            return

        # If the user hits the down
        # arrow, focus the listbox
        self.__listBox.SetFocus()
        self.__listBox.SetSelection(0)


    def __onText(self, ev):
        """Called on an ``EVT_TEXT`` event from the text control."""

        text    = self.__textCtrl.GetValue().strip()
        matches = self.__getMatches(text)

        if text == '' or len(matches) == 0:
            log.debug('Text on popup text control ("{}") - '
                      'no matches, destroying popup'.format(text))
            self.__destroy(False)
        else:
            log.debug('Text on popup text control ("{}") - '
                      'displaying {} matches'.format(text, len(matches)))
            self.__listBox.Set(matches)


    def __onEnter(self, ev):
        """Called on an ``EVT_TEXT_ENTER`` event from the text control."""

        log.debug('Enter on popup text control - destroying popup')
        self.__destroy()


    def __onListKeyDown(self, ev):
        """Called on an ``EVT_KEY_DOWN`` event from the list box.
        """
        key       = ev.GetKeyCode()
        enter     = wx.WXK_RETURN
        esc       = wx.WXK_ESCAPE
        backspace = wx.WXK_BACK
        delete    = wx.WXK_DELETE
        up        = wx.WXK_UP

        log.debug('Key event on popup list box: {}'.format(key))

        if key not in (enter, esc, up, backspace, delete):
            ev.Skip()
            return

        sel = self.__listBox.GetSelection()
        val = self.__listBox.GetString(sel)

        # If the user pushed the up arrow,
        # and we're at the top of the list,
        # give the focus to the text control
        if key == up:
            if sel == 0:
                log.debug('Up arrow on popup list box - '
                          'shifting focus to text control')
                self.__textCtrl.SetFocus()
                self.__textCtrl.SetInsertionPointEnd()
            else:
                ev.Skip()
            return

        # If the user pushed enter, copy
        # the current list selection to
        # the text control.
        if key == enter:
            log.debug('Enter on popup list box ("{}") - destroying '
                      'popup (and submitting value)'.format(val))
            self.__textCtrl.ChangeValue(val)
            self.__textCtrl.SetInsertionPointEnd()
            genEnter = True

        elif key in (esc, backspace, delete):
            log.debug('Escape on popup list box ("{}") '
                      '- destroying popup'.format(val))
            genEnter = False

        # The user hitting enter or escape
        # will result in this popup being
        # destroyed
        self.__destroy(genEnter)


    def __onListMouseDown(self, ev):
        """Called on GTK when the user clicks in the list box. Forces
        the list box to have focus.
        """
        ev.Skip()
        self.__listBox.SetFocus()


    def __onListMouseDblClick(self, ev):
        """Called when the user double clicks an item in the list box. """
        ev.Skip()

        sel = self.__listBox.GetSelection()
        val = self.__listBox.GetString(sel)

        log.debug('Double click on popup list box ("{}") - '
                  'destroying popup (and submitting value)'.format(val))

        self.__textCtrl.ChangeValue(val)
        self.__textCtrl.SetInsertionPointEnd()
        self.__destroy()
