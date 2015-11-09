#!/usr/bin/env python
#
# tagtext.py - The StaticTextTag and TextTagPanel classes.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides two classes:

.. autosummary::
   :nosignatures:

   StaticTextTag
   TextTagPanel


.. image:: images/texttagpanel.png
   :scale: 50%
   :align: center
"""


import logging
import random

import wx
import wx.lib.newevent as wxevent

import autotextctrl as atc


log = logging.getLogger(__name__)


class StaticTextTag(wx.Panel):
    """The ``StaticTextTag`` class is a ``wx.Panel`` which contains a
    ``StaticText`` control, and a *close* button. The displayed text
    and background colour are configurable.

    When the close button is pushed, an :data:`EVT_SST_CLOSE_EVENT` is
    generated.
    """

    
    def __init__(self,
                 parent,
                 text=None,
                 bgColour='#aaaaaa',
                 borderColour='#ffcdcd'):
        """Create a ``StaticTextTag``.

        :arg parent:       The :mod:`wx` parent object.
        :arg text:         Initial text to display.
        :arg bgColour:     Initial background colour.
        :arg borderColour: Initial background colour.
        """

        self.__bgColour     = None
        self.__borderColour = None

        wx.Panel.__init__(self, parent)

        self.__sizer    = wx.BoxSizer(wx.HORIZONTAL)
        self.__closeBtn = wx.StaticText(self,
                                        label='X',
                                        style=(wx.SUNKEN_BORDER         |
                                               wx.ALIGN_CENTRE_VERTICAL |
                                               wx.ALIGN_CENTRE_HORIZONTAL))
        self.__text     = wx.StaticText(self,
                                        style=(wx.ALIGN_CENTRE_VERTICAL |
                                               wx.ALIGN_CENTRE_HORIZONTAL))

        self.__closeBtn.SetFont(self.__closeBtn.GetFont().Smaller())
 
        self.__sizer.Add(self.__closeBtn,
                         border=2,
                         flag=(wx.EXPAND |
                               wx.LEFT   |
                               wx.TOP    |
                               wx.BOTTOM))
        self.__sizer.Add(self.__text,
                         border=2,
                         flag=(wx.EXPAND |
                               wx.RIGHT  |
                               wx.TOP    |
                               wx.BOTTOM))
        self.SetSizer(self.__sizer)
        
        self           .SetBackgroundColour(bgColour)
        self           .SetBorderColour(    borderColour)
        self.__closeBtn.SetForegroundColour('#404040')
        self.SetText(text)

        self.__text    .Bind(wx.EVT_LEFT_DOWN,   self.__onLeftDown)
        self           .Bind(wx.EVT_LEFT_DOWN,   self.__onLeftDown) 
        self.__closeBtn.Bind(wx.EVT_LEFT_UP,     self.__onCloseButton)
        
        self           .Bind(wx.EVT_KEY_DOWN,    self.__onKeyDown)

        self.__closeBtn.Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self.__text    .Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self           .Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self.__closeBtn.Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus)
        self.__text    .Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus)
        self           .Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus) 

        
    def __str__(self):
        """Returns a string representation of this ``StaticTextTag``. """
        return 'StaticTextTag(\'{}\')'.format(self.GetText())


    def SetBackgroundColour(self, colour):
        """Sets the background colour of this ``StaticTextTag``. """
        
        wx.Panel.SetBackgroundColour(self,  colour) 
        self.__text    .SetBackgroundColour(colour)
        self.__closeBtn.SetBackgroundColour(colour)

        self.__bgColour = colour
        
        self.Refresh()


    def SetBorderColour(self, colour):
        """Sets the border colour of this ``StaticTextTag``, for when it
        has focus.
        """
        self.__borderColour = colour


    def SetText(self, text):
        """Sets the text shown on this ``StaticTextTag``. """
        self.__text.SetLabel(text)
        self.Layout()
        self.Fit() 


    def GetText(self):
        """Returns the text shown on this ``StaticTextTag``. """
        return self.__text.GetLabel()


    def __onSetFocus(self, ev):
        """Called when this ``StaticTextTag`` gains focus. Changes the border
        colour.
        """ 
        ev.Skip() 
        wx.Panel.SetBackgroundColour(self, self.__borderColour)
        self.Refresh()


    def __onLeftDown(self, ev):
        """Called on left mouse events on this ``StaticTextTag``. Makes sure
        that this ``StaticTextTag`` has focus.
        """ 
        self.SetFocus()

    
    def __onKillFocus(self, ev):
        """Called when this ``StaticTextTag`` loses focus. Clears the border
        colour.
        """
        ev.Skip()
        if ev.GetWindow() not in (self, self.__text, self.__closeBtn):
            wx.Panel.SetBackgroundColour(self, self.__bgColour)
            self.Refresh()


    def __onKeyDown(self, ev):
        """Called when a key is pushed. If delete or backspace was pushed,
        an :data:`EVT_STT_CLOSE_EVENT` is generated.
        """ 
        
        key       = ev.GetKeyCode()
        delete    = wx.WXK_DELETE
        backspace = wx.WXK_BACK
        
        if key not in (delete, backspace):
            ev.ResumePropagation(wx.EVENT_PROPAGATE_MAX)
            ev.Skip()
            return

        self.__onCloseButton(None)

        
    def __onCloseButton(self, ev):
        """Called when the close button is pushed. Generates an
        :data:`EVT_STT_CLOSE_EVENT`.
        """

        log.debug('{} close button pressed'.format(str(self)))
        
        ev = StaticTextTagCloseEvent()
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)


_StaticTextTagCloseEvent, _EVT_STT_CLOSE_EVENT = wxevent.NewEvent()


EVT_STT_CLOSE_EVENT = _EVT_STT_CLOSE_EVENT
"""Identifier for the event generated by a :class:`StaticTextTag` when its
close button is pushed.
"""


StaticTextTagCloseEvent = _StaticTextTagCloseEvent
"""Event object created for an :data:`EVT_STT_CLOSE_EVENT`. """


class TextTagPanel(wx.Panel):
    """The ``TextTagPanel`` is a panel which contains a control allowing
    the user to add new tags, and a collection of :class:`StaticTextTag`
    controls. 
    
    The ``TextTagPanel`` supports the following styles:

    .. autosummary::
    
       TTP_ALLOW_NEW_TAGS
       TTP_ADD_NEW_TAGS
       TTP_NO_DUPLICATES
       TTP_CASE_SENSITIVE
       TTP_KEYBOARD_NAV

    
    The ``TextTagPanel`` generates the following events:

    .. autosummary::

       EVT_TTP_TAG_REMOVED_EVENT
       EVT_TTP_TAG_ADDED_EVENT
    """

    
    def __init__(self, parent, style=None):
        """Create a ``TextTagPanel``.

        :arg parent: The :mod:`wx` parent object.
        :arg style:  Style flags. Defaults to
                     ``TTP_ALLOW_NEW_TAGS | TTP_ADD_NEW_TAGS``.
        """
        
        wx.Panel.__init__(self, parent)

        if style is None:
            style = TTP_ALLOW_NEW_TAGS | TTP_ADD_NEW_TAGS

        self.__allowNewTags  = style & TTP_ALLOW_NEW_TAGS
        self.__addNewTags    = style & TTP_ADD_NEW_TAGS and self.__allowNewTags
        self.__noDuplicates  = style & TTP_NO_DUPLICATES
        self.__keyboardNav   = style & TTP_KEYBOARD_NAV

        self.__allTags    = []
        self.__activeTags = {}
        self.__tagColours = {}
        self.__tagWidgets = []

        if self.__allowNewTags:
            
            if style & TTP_CASE_SENSITIVE: atcStyle = atc.ATC_CASE_SENSITIVE
            else:                          atcStyle = 0
            
            self.__newTagCtrl = atc.AutoTextCtrl(self, style=atcStyle)
        else:
            self.__newTagCtrl = wx.Choice(self)
            
        self.__mainSizer    = wx.BoxSizer( wx.HORIZONTAL)
        self.__tagSizer     = wx.WrapSizer(wx.HORIZONTAL, 2)
        
        # ^^ the WrapSizer style flags don't 
        # seem to have made it into wxPython:
        #
        #     EXTEND_LAST_ON_EACH_LINE = 1
        #     REMOVE_LEADING_SPACES    = 2

        self.__mainSizer.Add(self.__newTagCtrl)
        self.__mainSizer.Add(self.__tagSizer, flag=wx.EXPAND, proportion=1)

        if self.__allowNewTags:
            self.__newTagCtrl.Bind(atc.EVT_ATC_TEXT_ENTER, self.__onTextCtrl)
        else:
            self.__newTagCtrl.Bind(wx.EVT_CHOICE,          self.__onChoice)

        if self.__keyboardNav:
            self.__newTagCtrl.Bind(wx.EVT_KEY_DOWN, self.__onNewTagKeyDown)
            self             .Bind(wx.EVT_KEY_DOWN, self.__onTagKeyDown)

        self.SetSizer(self.__mainSizer)
        self.Layout()

        
    def FocusNewTagCtrl(self):
        """Gives focus to the new tag control (either an :class:`.AutoTextCtrl`
        or a ``wx.Choice``, depending on whether the :data:`ATC_ALLOW_NEW_TAGS`
        style is set.
        """
        self.__newTagCtrl.SetFocus()


    def SetOptions(self, options, colours=None):
        """Sets the tag options made available to the user via the
        ``ComboBox``.

        :arg options: A sequence of tags that the user can choose from.
        :arg colours: A sequence of corresponding colours for each tag.
        """

        self.__allTags = list(options)
        self.__updateNewTagOptions()

        if colours is not None:
            
            for option, colour in zip(options, colours):
                self.__tagColours[option] = colour
        
        # TODO delete any active tags
        #      that are no longer valid?

    
    def GetOptions(self):
        """Returns a list of all the tags that are currently available to the
        user.
        """
        return list(self.__allTags)


    def AddTag(self, tag, colour=None):
        """Add a new :class:`StaticTextTag` to this ``TextTagPanel``.

        :arg tag:    The tag text.
        :arg colour: The tag background colour.
        """

        if colour is None:
            colour = self.__tagColours.get(tag, None)

        if colour is None:
            colour = [random.randint(100, 255),
                      random.randint(100, 255),
                      random.randint(100, 255)]

        stt      = StaticTextTag(self, tag, colour)
        
        stt.Bind(EVT_STT_CLOSE_EVENT, self.__onTagClose)

        self.__tagSizer.Add(stt, flag=wx.ALL, border=3)
        self.Layout()
        self.GetParent().Layout()

        if self.__addNewTags and tag not in self.__allTags:
            log.debug('Adding new tag to options: {}'.format(tag))
            self.__allTags.append(tag)
            self.__updateNewTagOptions()

        self.__tagWidgets.append(stt)
        self.__tagColours[tag] = colour
        self.__activeTags[tag] = self.__activeTags.get(tag, 0) + 1
        self.__updateNewTagOptions()


    def RemoveTag(self, tag):
        """Removes the specified tag. """

        tagIdx   = self.GetTagIndex(tag)
        stt      = self.__tagWidgets[tagIdx]
        
        self.__tagSizer  .Detach(stt)
        self.__tagWidgets.remove(stt)

        count = self.__activeTags[tag]

        if count == 1: self.__activeTags.pop(tag)
        else:          self.__activeTags[tag] = count - 1
        
        stt.Destroy()
        self.Layout()
        self.GetParent().Layout()

        self.__updateNewTagOptions() 


    def GetTagIndex(self, tag):
        """Returns the index of the specified tag. """
        for i, stt in enumerate(self.__tagWidgets):
            if stt.GetText() == tag:
                return i

        raise IndexError('Unknown tag: "{}"'.format(tag))
            

    def HasTag(self, tag):
        """Returns ``True`` if the given tag is currently shown, ``False``
        otherwise.
        """
        return tag in self.__activeTags


    def GetTagColour(self, tag):
        """Returns the background colour of the specified ``tag``, or ``None``
        if there is no default colour for the tag.
        """
        return self.__tagColours.get(tag, None)


    def SetTagColour(self, tag, colour):
        """Sets the background colour on all :class:`StaticTextTag` items
        which have the given tag text.
        """
        if tag not in self.__activeTags:
            return

        self.__tagColours[tag] = colour

        for stt in self.__tagWidgets:

            if stt.GetText() == tag:
                stt.SetBackgroundColour(colour)


    def __onTagClose(self, ev):
        """Called when the user pushes the close button on a
        :class:`StaticTextTag`. Removes the tag, and generates a
        :data:`EVT_TTP_TAG_REMOVED_EVENT`.
        """
        stt = ev.GetEventObject()
        tag = stt.GetText()

        idx = self.GetTagIndex(tag)

        self.RemoveTag(tag)

        if len(self.__tagWidgets) == 0:
            self.FocusNewTagCtrl()
        else:
            if idx == len(self.__tagWidgets):
                idx -= 1

            self.__tagWidgets[idx].SetFocus()

        log.debug('Tag removed: "{}"'.format(tag))

        ev = TextTagPanelTagRemovedEvent(tag=tag)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)

        
    def __onNewTagKeyDown(self, ev):
        """Called on key down events from the new tag control. If the right
        arrow key is pushed, the first :class:`StaticTextTag` is given input
        focus.
        """

        if ev.GetKeyCode() != wx.WXK_RIGHT or len(self.__tagWidgets) == 0:
            ev.Skip()
            return

        log.debug('Right arrow key on new tag control - focusing tags')

        self.__tagWidgets[0].SetFocus()

        
    def __onTagKeyDown(self, ev):
        """Called on key down events from a :class:`StaticTextTag` object. If
        the left/right arrow keys are pushed, the focus is shifted accordingly.
        """

        left      = wx.WXK_LEFT
        right     = wx.WXK_RIGHT
        key       = ev.GetKeyCode()
        stt       = ev.GetEventObject()

        if key not in (left, right):
            ev.Skip()
            return

        sttIdx = self.__tagWidgets.index(stt)
        
        if   key == left:  sttIdx -= 1
        elif key == right: sttIdx += 1

        if sttIdx == -1:
            log.debug('Arrow key on tag ({}) - focusing new '
                      'tag control'.format(stt.GetText()))
            self.FocusNewTagCtrl()
            return

        elif sttIdx == len(self.__tagWidgets):
            ev.Skip()
            return

        log.debug('Arrow key on tag ({}) - focusing '
                  'adjacent tag ({})'.format(
                      stt.GetText(), self.__tagWidgets[sttIdx].GetText()))
        self.__tagWidgets[sttIdx].SetFocus()

        
    def __onTextCtrl(self, ev):
        """Called when the user enters a new value via the ``TextCtrl`` (if
        this ``TextTagPanel`` allows new tags). Adds the new tag, and generates
        an :data:`EVT_TTP_TAG_ADDED_EVENT`.
        """

        tag = self.__newTagCtrl.GetValue()

        log.debug('New tag from text control: {}'.format(tag))
        
        self.AddTag(tag)
        self.__newTagCtrl.SetValue('')

        ev = TextTagPanelTagAddedEvent(tag=tag)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)        

    
    def __onChoice(self, ev):
        """Called when the user enters a new value via the ``wx.Choice`` (if
        this ``TextTagPanel`` does not allow new tags). Adds the new tag, and
        generates an :data:`EVT_TTP_TAG_ADDED_EVENT`.
        """ 

        tag = self.__newTagCtrl.GetString(self.__newTagCtrl.GetSelection())

        log.debug('New tag from choice control: {}'.format(tag))
        
        self.AddTag(tag)

        ev = TextTagPanelTagAddedEvent(tag=tag)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev) 


    def __updateNewTagOptions(self):
        """Updates the options shown on the new tag control."""

        tags = list(self.__allTags)

        if self.__noDuplicates:
            tags = [t for t in tags if t not in self.__activeTags]

        # The new tag control is either
        # a wx.Choice, or a atc.AutoTextCtrl
        if not self.__allowNewTags: self.__newTagCtrl.Set(         tags)
        else:                       self.__newTagCtrl.AutoComplete(tags)

        
TTP_ALLOW_NEW_TAGS  = 1
"""Style flag for use with a :class:`TextTagPanel` - if set, the user is able
to type in tag names that are not in the ``ComboBox``.
"""


TTP_ADD_NEW_TAGS = 2
"""Style flag for use with a :class:`TextTagPanel` - if set, when the user
types in a tag name that is not in the ``ComboBox``, that name is added to the
list of options in the ``ComboBox``. This flag only has an effect if the
:data:`TTP_ALLOW_NEW_TAGS` flag is also set.
"""


TTP_NO_DUPLICATES = 4
"""Style flag for use with a :class:`TextTagPanel` - if set, the user will be
prevented from adding the same tag more than once.
"""


TTP_CASE_SENSITIVE = 8
"""Style flag for use with a :class:`TextTagPanel` - if set, the
auto-completion options will be case sensitive. This flag only has an effect
if the :data:`TTP_ALLOW_NEW_TAGS` flag is also set.
"""


TTP_KEYBOARD_NAV = 16
"""Style flag for use with a :class:`TextTagPanel` - if set, the user
can use the left and right arrow keys to move between the new tag control
and the tags and, when a tag is focused can use the delete/backspace keys to
remove it.
"""


_TextTagPanelTagAddedEvent,   _EVT_TTP_TAG_ADDED_EVENT   = wxevent.NewEvent()
_TextTagPanelTagRemovedEvent, _EVT_TTP_TAG_REMOVED_EVENT = wxevent.NewEvent()


EVT_TTP_TAG_ADDED_EVENT = _EVT_TTP_TAG_ADDED_EVENT
"""Identifier for the event generated when a tag is added to a
:class:`TextTagPanel`.
"""


TextTagPanelTagAddedEvent = _TextTagPanelTagAddedEvent
"""Event generated when a tag is added to a :class:`TextTagPanel`. A
``TextTagPanelTagAddedEvent`` has a single attribute called ``tag``, which
contains the tag text.
"""


EVT_TTP_TAG_REMOVED_EVENT = _EVT_TTP_TAG_REMOVED_EVENT
"""Identifier for the event generated when a tag is removed from a
:class:`TextTagPanel`.
"""


TextTagPanelTagRemovedEvent = _TextTagPanelTagRemovedEvent
"""Event generated when a tag is removed from a :class:`TextTagPanel`. A
``TextTagPanelTagRemovedEvent`` has a single attribute called ``tag``, which
contains the tag text.
"""
