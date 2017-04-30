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

from . import autotextctrl as atc


log = logging.getLogger(__name__)


class StaticTextTag(wx.Panel):
    """The ``StaticTextTag`` class is a ``wx.Panel`` which contains a
    ``StaticText`` control, and a *close* button. The displayed text
    and background colour are configurable.

    When the close button is pushed, an :data:`EVT_STT_CLOSE` is
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
        :arg borderColour: Initial border colour.
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

        self.__closeBtn.Bind(wx.EVT_LEFT_UP,     self.__onCloseButton)
        self.__closeBtn.Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self.__text    .Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self           .Bind(wx.EVT_SET_FOCUS,   self.__onSetFocus)
        self.__closeBtn.Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus)
        self.__text    .Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus)
        self           .Bind(wx.EVT_KILL_FOCUS,  self.__onKillFocus)


    def __str__(self):
        """Returns a string representation of this ``StaticTextTag``. """
        return 'StaticTextTag(\'{}\')'.format(self.GetText())


    @property
    def closeButton(self):
        """Returns a reference to the ``StaticText`` control used as the
        close button.
        """
        return self.__closeBtn


    @property
    def text(self):
        """Returns a reference to the ``StaticText`` control used for
        displaying the tag text.
        """
        return self.__text


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
        if text is None:
            text = ''
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


    def __onKillFocus(self, ev):
        """Called when this ``StaticTextTag`` loses focus. Clears the border
        colour.
        """
        ev.Skip()
        if ev.GetWindow() not in (self, self.__text, self.__closeBtn):
            wx.Panel.SetBackgroundColour(self, self.__bgColour)
            self.Refresh()


    def __onCloseButton(self, ev):
        """Called when the close button is pushed. Generates an
        :data:`EVT_STT_CLOSE`.
        """

        log.debug('{} close button pressed'.format(str(self)))

        ev = StaticTextTagCloseEvent()
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)


_StaticTextTagCloseEvent, _EVT_STT_CLOSE = wxevent.NewEvent()


EVT_STT_CLOSE = _EVT_STT_CLOSE
"""Identifier for the event generated by a :class:`StaticTextTag` when its
close button is pushed.
"""


StaticTextTagCloseEvent = _StaticTextTagCloseEvent
"""Event object created for an :data:`EVT_STT_CLOSE`. """


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

       EVT_TTP_TAG_REMOVED
       EVT_TTP_TAG_ADDED
       EVT_TTP_TAG_SELECT
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
        self.__caseSensitive = style & TTP_CASE_SENSITIVE

        self.__allTags     = []
        self.__tagDisplays = {}
        self.__activeTags  = {}
        self.__tagColours  = {}
        self.__tagWidgets  = []

        if self.__caseSensitive: atcStyle = atc.ATC_CASE_SENSITIVE
        else:                    atcStyle = 0

        self.__newTagCtrl = atc.AutoTextCtrl(self, style=atcStyle)
        self.__mainSizer  = wx.BoxSizer( wx.HORIZONTAL)
        self.__tagSizer   = wx.WrapSizer(wx.HORIZONTAL, 2)

        # ^^ the WrapSizer style flags don't
        # seem to have made it into wxPython:
        #
        #     EXTEND_LAST_ON_EACH_LINE = 1
        #     REMOVE_LEADING_SPACES    = 2

        self.__mainSizer.Add(self.__newTagCtrl)
        self.__mainSizer.Add(self.__tagSizer, flag=wx.EXPAND, proportion=1)

        self.__newTagCtrl.Bind(atc.EVT_ATC_TEXT_ENTER, self.__onTextCtrl)

        if self.__keyboardNav:
            self.__newTagCtrl.Bind(wx.EVT_KEY_DOWN, self.__onNewTagKeyDown)

        self.SetSizer(self.__mainSizer)
        self.Layout()


    @property
    def newTagCtrl(self):
        """Returns a reference to the :class:`.AutoTextCtrl`. """
        return self.__newTagCtrl


    @property
    def tags(self):
        """Returns a list containing all :class:`StaticTextTag` widgets. """
        return list(self.__tagWidgets)


    def FocusNewTagCtrl(self):
        """Gives focus to the new tag control (an :class:`.AutoTextCtrl`).
        """
        self.__newTagCtrl.SetFocus()


    def SelectTag(self, tag):
        """Gives focus to the :class:`StaticTextTag` control with the
        specified tag, if it exists.
        """
        tagIdx = self.GetTagIndex(tag)
        self.__tagWidgets[tagIdx].SetFocus()


    def SetOptions(self, options, colours=None):
        """Sets the tag options made available to the user via the
        :class:`.AutoTextCtrl`.

        :arg options: A sequence of tags that the user can choose from.
        :arg colours: A sequence of corresponding colours for each tag.
        """

        origOptions = options

        if not self.__caseSensitive:
            lowered = [o.lower() for o in options]
            uniq    = []
            orig    = []

            for i, o in enumerate(lowered):
                if o not in uniq:
                    uniq.append(o)
                    orig.append(origOptions[i])

            options     = uniq
            origOptions = orig

        self.__allTags     = list(options)
        self.__tagDisplays = {o : oo for (o, oo) in zip(options, origOptions)}

        self.__updateNewTagOptions()

        if colours is not None:

            for option, colour in zip(options, colours):
                self.SetTagColour(option, colour)

        # TODO delete any active tags
        #      that are no longer valid?


    def GetOptions(self):
        """Returns a list of all the tags that are currently available to the
        user.
        """
        return [self.__tagDisplays[o] for o in self.__allTags]


    def AddTag(self, tag, colour=None):
        """Add a new :class:`StaticTextTag` to this ``TextTagPanel``.

        :arg tag:    The tag text.
        :arg colour: The tag background colour.
        """

        origTag = tag

        if not self.__caseSensitive:
            tag = tag.lower()

        if colour is None:
            colour = self.__tagColours.get(tag, None)

        if colour is None:
            colour = [random.randint(100, 255),
                      random.randint(100, 255),
                      random.randint(100, 255)]

        stt = StaticTextTag(self, origTag, colour)

        stt.Bind(EVT_STT_CLOSE, self.__onTagClose)

        if self.__keyboardNav:
            stt.Bind(wx.EVT_LEFT_DOWN, self.__onTagLeftDown)
            stt.Bind(wx.EVT_KEY_DOWN,  self.__onTagKeyDown)

        self.__tagSizer.Add(stt, flag=wx.ALL, border=3)
        self.Layout()
        self.GetParent().Layout()

        if self.__addNewTags and tag not in self.__allTags:
            log.debug('Adding new tag to options: {}'.format(tag))
            self.__allTags.append(tag)
            self.__tagDisplays[tag] = origTag

        self.__tagWidgets.append(stt)
        self.__tagColours[tag] = colour
        self.__activeTags[tag] = self.__activeTags.get(tag, 0) + 1
        self.__updateNewTagOptions()


    def RemoveTag(self, tag):
        """Removes the specified tag. """

        if not self.__caseSensitive:
            tag = tag.lower()

        tagIdx = self.GetTagIndex(tag)
        stt    = self.__tagWidgets[tagIdx]

        self.__tagSizer  .Detach(stt)
        self.__tagWidgets.remove(stt)

        count = self.__activeTags[tag]

        if count == 1: self.__activeTags.pop(tag)
        else:          self.__activeTags[tag] = count - 1

        stt.Destroy()
        self.Layout()
        self.GetParent().Layout()

        self.__updateNewTagOptions()


    def GetTags(self):
        """Returns a list containing all active tags in this ``TextTagPanel``.
        """
        return [stt.GetText() for stt in self.__tagWidgets]


    def ClearTags(self):
        """Removes all tags from this ``TextTagPanel``. """
        for tag in list(self.__tagWidgets):
            self.RemoveTag(tag.GetText())


    def GetTagIndex(self, tag):
        """Returns the index of the specified tag. """

        tags = self.GetTags()

        if not self.__caseSensitive:
            tag  = tag.lower()
            tags = [t.lower() for t in tags]

        for i, t in enumerate(tags):
            if t == tag:
                return i

        raise IndexError('Unknown tag: "{}"'.format(tag))


    def TagCount(self):
        """Returns the number of tags currently visible. """
        return len(self.__tagWidgets)


    def HasTag(self, tag):
        """Returns ``True`` if the given tag is currently shown, ``False``
        otherwise.
        """
        if not self.__caseSensitive:
            tag = tag.lower()

        return tag in self.__activeTags


    def GetTagColour(self, tag):
        """Returns the background colour of the specified ``tag``, or ``None``
        if there is no default colour for the tag.
        """
        if not self.__caseSensitive:
            tag = tag.lower()

        return self.__tagColours.get(tag, None)


    def SetTagColour(self, tag, colour):
        """Sets the background colour on all :class:`StaticTextTag` items
        which have the given tag text.
        """

        if not self.__caseSensitive:
            tag = tag.lower()

        if tag not in self.__allTags:
            return

        self.__tagColours[tag] = colour

        for stt in self.__tagWidgets:

            if self.__caseSensitive: sttText = stt.GetText()
            else:                    sttText = stt.GetText().lower()

            if sttText == tag:
                stt.SetBackgroundColour(colour)


    def __selectTag(self, stt):
        """Called by event handlers which listen for mouse/keyboard activity
        on :class:`StaticTextTag` widgets. Focuses the given ``StaticTextTag``,
        and generates an :data:`EVT_TTP_TAG_SELECT` event.
        """

        tag = stt.GetText()
        stt.SetFocus()

        log.debug('Posting tag select event ("{}")'.format(tag))

        ev = TextTagPanelTagSelectEvent(tag=tag)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)


    def __onTagLeftDown(self, ev):
        """Called on left mouse down events on :class:`StaticTextTag`
        objects (only if the :data:`TTP_KEYBOARD_NAV` style is set).
        Gives the tag focus.
        """

        stt = ev.GetEventObject()
        tag = stt.GetText()

        log.debug('Mouse down on tag: "{}"'.format(tag))
        self.__selectTag(stt)


    def __onTagClose(self, ev):
        """Called when the user pushes the close button on a
        :class:`StaticTextTag`. Removes the tag, and generates a
        :data:`EVT_TTP_TAG_REMOVED` event.
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
        """Called on key down events from the new tag control (if the
        :data:`TTP_KEYBOARD_NAV` style is set). If the right
        arrow key is pushed, the first :class:`StaticTextTag` is given input
        focus.
        """

        key = ev.GetKeyCode()

        log.debug('TextTagPanel key down [new tag control] ({})'.format(key))

        # Only process right arrows if the text
        # control cursor is on the far right
        value  = self.__newTagCtrl.GetValue()
        cursor = self.__newTagCtrl.GetInsertionPoint()

        if key != wx.WXK_RIGHT         or \
           len(self.__tagWidgets) == 0 or \
           cursor != len(value):
            ev.Skip()
            return

        log.debug('Right arrow key on new tag control - focusing tags')

        self.__selectTag(self.__tagWidgets[0])


    def __onTagKeyDown(self, ev):
        """Called on key down events from a :class:`StaticTextTag` object. If
        the left/right arrow keys are pushed, the focus is shifted accordingly.
        """

        left      = wx.WXK_LEFT
        right     = wx.WXK_RIGHT
        delete    = wx.WXK_DELETE
        backspace = wx.WXK_BACK
        key       = ev.GetKeyCode()
        stt       = ev.GetEventObject()

        log.debug('TextTagPanel key event ({})'.format(key))

        if key not in (left, right, delete, backspace):
            ev.ResumePropagation(wx.EVENT_PROPAGATE_MAX)
            ev.Skip()
            return

        if key in (delete, backspace):
            self.__onTagClose(ev)
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

        log.debug('Arrow key on tag ({}) - selecting '
                  'adjacent tag ({})'.format(
                      stt.GetText(), self.__tagWidgets[sttIdx].GetText()))

        self.__selectTag(self.__tagWidgets[sttIdx])


    def __onTextCtrl(self, ev):
        """Called when the user enters a new value via the ``TextCtrl`` (if
        this ``TextTagPanel`` allows new tags). Adds the new tag, and generates
        an :data:`EVT_TTP_TAG_ADDED` event.
        """

        tag = self.__newTagCtrl.GetValue().strip()

        self.__newTagCtrl.ChangeValue('')

        if tag == '':
            return

        # If we don't care about case, and
        # this is a known option, use the
        # 'display' version of the tag.
        origTag = tag
        if not self.__caseSensitive:
            tag     = tag.lower()
            origTag = self.__tagDisplays.get(tag, origTag)

        if self.__noDuplicates and self.HasTag(tag):
            log.debug('New tag {} ignored (noDuplicates is True)'.format(tag))
            return

        if not self.__allowNewTags and tag not in self.__allTags:
            log.debug('New tag {} ignored (allowNewTags is False)'.format(tag))
            return

        log.debug('New tag from text control: {}'.format(origTag))

        self.__newTagCtrl.Refresh()

        self.AddTag(origTag)

        ev = TextTagPanelTagAddedEvent(tag=origTag)
        ev.SetEventObject(self)
        wx.PostEvent(self, ev)


    def __updateNewTagOptions(self):
        """Updates the options shown on the new tag control."""

        tags = list(self.__allTags)

        if self.__noDuplicates:
            tags = [t for t in tags if t not in self.__activeTags]

        tags = [self.__tagDisplays[t] for t in tags]

        self.__newTagCtrl.AutoComplete(tags)


TTP_ALLOW_NEW_TAGS  = 1
"""Style flag for use with a :class:`TextTagPanel` - if set, the user is able
to type in tag names that are not known by the :class:`.AutoTextCtrl`.
"""


TTP_ADD_NEW_TAGS = 2
"""Style flag for use with a :class:`TextTagPanel` - if set, when the user
types in a tag name that is not known by the ``AutoTextCtrl``, that name is
added to its list of options. This flag only has an effect if the
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


_TextTagPanelTagAddedEvent,   _EVT_TTP_TAG_ADDED   = wxevent.NewEvent()
_TextTagPanelTagRemovedEvent, _EVT_TTP_TAG_REMOVED = wxevent.NewEvent()
_TextTagPanelTagSelectEvent,  _EVT_TTP_TAG_SELECT  = wxevent.NewEvent()


EVT_TTP_TAG_ADDED = _EVT_TTP_TAG_ADDED
"""Identifier for the event generated when a tag is added to a
:class:`TextTagPanel`.
"""


TextTagPanelTagAddedEvent = _TextTagPanelTagAddedEvent
"""Event generated when a tag is added to a :class:`TextTagPanel`. A
``TextTagPanelTagAddedEvent`` has a single attribute called ``tag``, which
contains the tag text.
"""


EVT_TTP_TAG_REMOVED = _EVT_TTP_TAG_REMOVED
"""Identifier for the event generated when a tag is removed from a
:class:`TextTagPanel`.
"""


TextTagPanelTagRemovedEvent = _TextTagPanelTagRemovedEvent
"""Event generated when a tag is removed from a :class:`TextTagPanel`. A
``TextTagPanelTagRemovedEvent`` has a single attribute called ``tag``, which
contains the tag text.
"""


EVT_TTP_TAG_SELECT = _EVT_TTP_TAG_SELECT
"""Identifier for the event generated when a tag is selected in a
:class:`TextTagPanel`.
"""


TextTagPanelTagSelectEvent = _TextTagPanelTagSelectEvent
"""Event generated when a tag is selected in  a :class:`TextTagPanel`. A
``TextTagPanelTagSelectEvent`` has a single attribute called ``tag``, which
contains the tag text.
"""
