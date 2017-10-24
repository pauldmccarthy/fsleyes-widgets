#!/usr/bin/env python
#
# test_texttag.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

from . import run_with_wx, simclick, simtext, simkey, addall, realYield

import fsleyes_widgets.texttag as tt


def test_StaticTextTag():
    run_with_wx(_test_StaticTextTag)
def _test_StaticTextTag():
    frame = wx.GetApp().GetTopWindow()
    tag   = tt.StaticTextTag(frame)
    dummy = wx.TextCtrl(frame)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(dummy, flag=wx.EXPAND)
    sizer.Add(tag,   flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    realYield()
    assert tag.GetText() == ''

    tag.SetText('TagText')
    tag.SetBackgroundColour('#bb3333')
    tag.SetBorderColour(    '#3333bb')
    realYield()
    assert tag.GetText() == 'TagText'

    dummy.SetFocus()
    wx.Yield()
    tag.SetFocus()
    wx.Yield()


def test_StaticTextTag_Close():
    run_with_wx(_test_StaticTextTag_Close)
def _test_StaticTextTag_Close():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    tag   = tt.StaticTextTag(frame)

    addall(frame, [tag])

    closeBtn = tag.closeButton

    called = [False]

    def handler(ev):
        called[0] = True

    tag.Bind(tt.EVT_STT_CLOSE, handler)

    tag.SetText('Blah')

    simclick(sim, closeBtn, stype=2)
    assert called[0]


def test_TextTagPanel_create_logic():
    run_with_wx(_test_TextTagPanel_create_logic)
def _test_TextTagPanel_create_logic():
    frame   = wx.GetApp().GetTopWindow()
    panel   = tt.TextTagPanel(frame)

    tags1    = ['Tag1',        'Tag2',        'Tag3']
    colours1 = [(50, 200, 50), (150, 20, 20), (50, 50, 225)]
    tags2    = ['2Tag1',        '2Tag2',         '3Tag3']
    colours2 = [(10, 100, 200), (100, 167, 202), (18, 28, 208)]

    panel.SetOptions(tags1, colours1)
    assert list(panel.GetOptions()) == tags1
    assert len(panel.GetTags()) == 0
    assert panel.TagCount() == 0
    for t, c in zip(tags1, colours1):
        assert tuple(panel.GetTagColour(t))         == c
        assert tuple(panel.GetTagColour(t.lower())) == c
    assert panel.GetTagColour(tags2[0]) is None

    # Replace the options with another set
    panel.SetOptions(tags2, colours2)
    assert list(panel.GetOptions()) == tags2
    assert len(panel.GetTags()) == 0
    assert panel.TagCount() == 0
    for t, c in zip(tags2, colours2):
        assert tuple(panel.GetTagColour(t))         == c
        assert tuple(panel.GetTagColour(t.lower())) == c

    # The ttp caches colours from old options
    # so colours1 should still be in there
    assert panel.GetTagColour(tags1[0]) == colours1[0]


def test_TextTagPanel_add_remove_logic():
    run_with_wx(_test_TextTagPanel_add_remove_logic)
def _test_TextTagPanel_add_remove_logic():
    frame   = wx.GetApp().GetTopWindow()
    panel   = tt.TextTagPanel(frame)

    tags    = ['Tag1',        'Tag2',        'Tag3']
    colours = [(50, 200, 50), (150, 20, 20), (50, 50, 225)]

    panel.SetOptions(tags, colours)

    panel.AddTag(tags[0])
    panel.AddTag(tags[1])

    assert panel.TagCount() == 2
    assert list(panel.GetTags()) == [tags[0], tags[1]]
    assert panel.GetTagIndex(tags[0]) == 0
    assert panel.GetTagIndex(tags[1]) == 1
    assert     panel.HasTag(tags[0])
    assert     panel.HasTag(tags[1])
    assert not panel.HasTag(tags[2])

    panel.SetTagColour(tags[0], (50, 50, 50))

    panel.RemoveTag(tags[0])
    assert panel.TagCount() == 1
    assert list(panel.GetTags()) == [tags[1]]
    assert not panel.HasTag(tags[0])
    assert     panel.HasTag(tags[1])

    panel.ClearTags()
    assert panel.TagCount() == 0
    assert list(panel.GetTags()) == []
    assert not panel.HasTag(tags[0])
    assert not panel.HasTag(tags[1])

    assert tuple(panel.GetTagColour(tags[0])) == (50, 50, 50)


def test_TextTagPanel_nostyle():
    run_with_wx(_test_TextTagPanel_nostyle)
def _test_TextTagPanel_nostyle():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = tt.TextTagPanel(frame, style=0)

    addall(frame, [panel])

    result = [None]

    def handler(ev):
        result[0] = ev.tag

    panel.Bind(tt.EVT_TTP_TAG_ADDED, handler)

    tags = ['Tag1', 'Tag2', 'Tag3']

    panel.SetOptions(tags)

    # Add an existing tag
    realYield()
    simtext(sim, panel.newTagCtrl.textCtrl, tags[0])
    assert panel.GetTags() == [tags[0]]
    assert result[0] == tags[0]

    simtext(sim, panel.newTagCtrl.textCtrl, tags[2])
    assert panel.GetTags() == [tags[0], tags[2]]
    assert result[0] == tags[2]

    # Duplicate
    result[0] = None
    simtext(sim, panel.newTagCtrl.textCtrl, tags[2])
    assert panel.GetTags() == [tags[0], tags[2], tags[2]]
    assert result[0] == tags[2]

    # Case insensitive
    simtext(sim, panel.newTagCtrl.textCtrl, tags[1].lower())
    assert panel.GetTags() == [tags[0], tags[2], tags[2], tags[1]]
    assert result[0] == tags[1]

    # Not in known tags
    result[0] = None
    simtext(sim, panel.newTagCtrl.textCtrl, 'notag')
    assert panel.GetTags() == [tags[0], tags[2], tags[2], tags[1]]
    assert result[0] is None


def test_TextTagPanel_close_event():
    run_with_wx(_test_TextTagPanel_close_event)
def _test_TextTagPanel_close_event():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=0)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    result = [None]

    def handler(ev):
        result[0] = ev.tag

    panel.Bind(tt.EVT_TTP_TAG_REMOVED, handler)

    panel.AddTag('MyTag1')
    panel.AddTag('MyTag2')
    wx.Yield()

    simclick(sim, panel.tags[1].closeButton, stype=2)
    assert result[0]       == 'MyTag2'
    assert panel.GetTags() == ['MyTag1']

    simclick(sim, panel.tags[0].closeButton, stype=2)
    assert result[0]       == 'MyTag1'
    assert panel.GetTags() == []


def test_TextTagPanel_allow_new_tags():
    run_with_wx(_test_TextTagPanel_allow_new_tags)
def _test_TextTagPanel_allow_new_tags():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=tt.TTP_ALLOW_NEW_TAGS)

    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    realYield()
    simtext(sim, panel.newTagCtrl.textCtrl, 'MyNewTag')

    assert panel.GetTags()    == ['MyNewTag']
    assert panel.GetOptions() == []


def test_TextTagPanel_add_new_tags():
    run_with_wx(_test_TextTagPanel_add_new_tags)
def _test_TextTagPanel_add_new_tags():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=(tt.TTP_ALLOW_NEW_TAGS |
                                          tt.TTP_ADD_NEW_TAGS))

    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    realYield()
    simtext(sim, panel.newTagCtrl.textCtrl, 'MyNewTag')

    assert panel.GetTags()    == ['MyNewTag']
    assert panel.GetOptions() == ['MyNewTag']


def test_TextTagPanel_no_duplicates():
    run_with_wx(_test_TextTagPanel_no_duplicates)
def _test_TextTagPanel_no_duplicates():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=tt.TTP_NO_DUPLICATES)

    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    tags = ['Tag1', 'Tag2']
    panel.SetOptions(tags)
    realYield()
    simtext(sim, panel.newTagCtrl.textCtrl, tags[0])
    assert panel.GetTags() == [tags[0]]

    # Duplicate should not be added
    simtext(sim, panel.newTagCtrl.textCtrl, tags[0])
    assert panel.GetTags() == [tags[0]]

    simtext(sim, panel.newTagCtrl.textCtrl, tags[1])
    assert panel.GetTags() == [tags[0], tags[1]]


def test_TextTagPanel_case_sensitive():
    run_with_wx(_test_TextTagPanel_case_sensitive)
def _test_TextTagPanel_case_sensitive():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=(tt.TTP_CASE_SENSITIVE |
                                          tt.TTP_NO_DUPLICATES  |
                                          tt.TTP_ALLOW_NEW_TAGS))

    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    tags = ['Tag1', 'Tag2', 'Tag3', 'tag3']
    panel.SetOptions(tags)
    assert panel.GetOptions() == tags

    realYield()
    for i in range(len(tags)):
        simtext(sim, panel.newTagCtrl.textCtrl, tags[i])
        assert panel.GetTags() == tags[:i + 1]
        assert panel.HasTag(tags[i])

    panel.RemoveTag(tags[3])
    assert panel.GetTags() == tags[:3]

    panel.SetTagColour(tags[2], ( 50,  50,  50))
    panel.SetTagColour(tags[3], (100, 100, 100))

    assert panel.GetTagColour(tags[2]) == ( 50,  50,  50)
    assert panel.GetTagColour(tags[3]) == (100, 100, 100)


def test_TextTagPanel_mouse_focus():
    run_with_wx(_test_TextTagPanel_mouse_focus)
def _test_TextTagPanel_mouse_focus():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    panel = tt.TextTagPanel(frame, style=tt.TTP_KEYBOARD_NAV)

    addall(frame, [panel])

    result = [None]

    def handler(ev):
        print('Gaaaargh')
        result[0] = ev.tag

    panel.Bind(tt.EVT_TTP_TAG_SELECT, handler)

    panel.SetOptions(['tag1', 'tag2'])
    panel.AddTag('tag1')

    simclick(sim, panel.tags[0], stype=2)
    assert result[0] == 'tag1'


def test_TextTagPanel_keyboard_nav():
    run_with_wx(_test_TextTagPanel_keyboard_nav)
def _test_TextTagPanel_keyboard_nav():

    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=tt.TTP_KEYBOARD_NAV)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    result = [None]

    def handler(ev):
        result[0] = ev.tag

    panel.Bind(tt.EVT_TTP_TAG_SELECT, handler)

    tags = ['tag1', 'tag2', 'tag3']

    panel.SetOptions(tags)
    for t in tags:
        panel.AddTag(t)
    realYield()

    panel.FocusNewTagCtrl()

    realYield()

    simkey(sim, panel.newTagCtrl, wx.WXK_LEFT)
    assert result[0] is None
    simkey(sim, panel.newTagCtrl, wx.WXK_RIGHT)
    assert result[0] == tags[0]

    simkey(sim, panel.tags[0], wx.WXK_RIGHT)
    assert result[0] == tags[1]
    simkey(sim, panel.tags[1], wx.WXK_RIGHT)
    assert result[0] == tags[2]
    result[0] = None
    simkey(sim, panel.tags[2], wx.WXK_RIGHT)
    assert result[0] is None

    simkey(sim, panel.tags[2], wx.WXK_LEFT)
    assert result[0] == tags[1]
    simkey(sim, panel.tags[1], wx.WXK_LEFT)
    assert result[0] == tags[0]
    result[0] = None
    simkey(sim, panel.tags[0], wx.WXK_LEFT)
    assert result[0] is None
    assert panel.newTagCtrl.textCtrl.HasFocus()



def test_TextTagPanel_keyboard_close():
    run_with_wx(_test_TextTagPanel_keyboard_close)
def _test_TextTagPanel_keyboard_close():
    sim   = wx.UIActionSimulator()
    frame = wx.GetApp().GetTopWindow()
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    panel = tt.TextTagPanel(frame, style=tt.TTP_KEYBOARD_NAV)
    sizer.Add(panel, flag=wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Layout()

    result = [None]

    def handler(ev):
        result[0] = ev.tag

    panel.Bind(tt.EVT_TTP_TAG_REMOVED, handler)

    tags = ['tag1', 'tag2', 'tag3']

    panel.SetOptions(tags)
    for t in tags:
        panel.AddTag(t)
    realYield()

    # Give a tag focus
    simclick(sim, panel.tags[0], stype=2)

    # Hit the delete key
    simkey(sim, panel.tags[0], wx.WXK_DELETE)
    assert result[0] == tags[0]

    # Give another tag focus
    simclick(sim, panel.tags[0], stype=2)
    # Hit the backspace key
    simkey(sim, panel.tags[0], wx.WXK_BACK)
    assert result[0] == tags[1]
