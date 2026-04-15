#!/usr/bin/env python
#
# __init__.py - fsleyes-widgets
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
# ruff: noqa: F401
#
"""The ``fsleyes_widgets`` package contains various custom :mod:`wx` widgets
and utilities used by FSLeyes.


Some of the controls in ``fsleyes_widgets`` are duplicates of controls which
are already available in ``wx`` or ``wx.lib.agw``. In these instances, I wrote
my own implementations to work around annoying, quirky, and/or downright buggy
behaviour in the existing controls.


This file is used to store the current ``fsleyes-widgets`` version.
"""

from fsleyes_widgets.utils                import (WX_PYTHON,
                                                  WX_PHOENIX,
                                                  WX_UNKNOWN,
                                                  WX_MAC_COCOA,
                                                  WX_MAC_CARBON,
                                                  WX_GTK,
                                                  WX_GTK2,
                                                  WX_GTK3,
                                                  wxversion,
                                                  wxVersion,
                                                  wxFlavour,
                                                  wxPlatform,
                                                  frozen,
                                                  canHaveGui,
                                                  haveGui,
                                                  inSSHSession,
                                                  inVNCSession,
                                                  isalive)
from fsleyes_widgets.autotextctrl         import (AutoTextCtrl,
                                                  AutoCompletePopup,
                                                  AutoTextCtrlEnterEvent,
                                                  ATCPopupDestroyEvent,
                                                  ATC_CASE_SENSITIVE,
                                                  ATC_NO_PROPAGATE_ENTER,
                                                  EVT_ATC_TEXT_ENTER,
                                                  EVT_ATC_POPUP_DESTROY)
from fsleyes_widgets.bitmapradio          import (BitmapRadioBox,
                                                  BitmapRadioEvent,
                                                  BMPRADIO_ALLOW_DESELECTED,
                                                  EVT_BITMAP_RADIO_EVENT)
from fsleyes_widgets.bitmaptoggle         import (BitmapToggleButton,
                                                  BitmapToggleEvent,
                                                  EVT_BITMAP_TOGGLE)
from fsleyes_widgets.colourbutton         import (ColourButton,
                                                  ColourButtonEvent,
                                                  EVT_COLOUR_BUTTON_EVENT)
from fsleyes_widgets.dialog               import (SimpleMessageDialog,
                                                  SMD_KEEP_CENTERED,
                                                  TimeoutDialog,
                                                  ProcessingDialog,
                                                  TextEditDialog,
                                                  FSLDirDialog,
                                                  CheckBoxMessageDialog,
                                                  TED_READONLY,
                                                  TED_MULTILINE,
                                                  TED_OK,
                                                  TED_CANCEL,
                                                  TED_OK_CANCEL,
                                                  TED_COPY,
                                                  TED_COPY_MESSAGE)
from fsleyes_widgets.elistbox             import (EditableListBox,
                                                  ListSelectEvent,
                                                  ListAddEvent,
                                                  ListRemoveEvent,
                                                  ListMoveEvent,
                                                  ListDblClickEvent,
                                                  EVT_ELB_SELECT_EVENT,
                                                  EVT_ELB_ADD_EVENT,
                                                  EVT_ELB_REMOVE_EVENT,
                                                  EVT_ELB_MOVE_EVENT,
                                                  EVT_ELB_DBLCLICK_EVENT,
                                                  ELB_NO_SCROLL,
                                                  ELB_NO_ADD,
                                                  ELB_NO_REMOVE,
                                                  ELB_NO_MOVE,
                                                  ELB_REVERSE,
                                                  ELB_TOOLTIP,
                                                  ELB_EDITABLE,
                                                  ELB_NO_LABELS,
                                                  ELB_WIDGET_RIGHT,
                                                  ELB_TOOLTIP_DOWN,
                                                  ELB_SCROLL_BUTTONS)
from fsleyes_widgets.filepanel            import (FilePanel,
                                                  FilePanelEvent,
                                                  EVT_FILE_PANEL_EVENT)
from fsleyes_widgets.floatslider          import (FloatSlider,
                                                  SliderSpinPanel,
                                                  SliderSpinLimitEvent,
                                                  SliderSpinValueEvent,
                                                  FS_MOUSEWHEEL,
                                                  FS_INTEGER,
                                                  SSP_SHOW_LIMITS,
                                                  SSP_EDIT_LIMITS,
                                                  SSP_MOUSEWHEEL,
                                                  SSP_INTEGER,
                                                  SSP_NO_LIMITS,
                                                  EVT_SSP_VALUE,
                                                  EVT_SSP_LIMIT)
from fsleyes_widgets.floatspin            import (FloatSpinCtrl,
                                                  FloatSpinEvent,
                                                  FSC_MOUSEWHEEL,
                                                  FSC_INTEGER,
                                                  EVT_FLOATSPIN)
from fsleyes_widgets.imagepanel           import (ImagePanel,)
from fsleyes_widgets.notebook             import (Notebook,
                                                  PageChangeEvent,
                                                  EVT_PAGE_CHANGE)
from fsleyes_widgets.numberdialog         import (NumberDialog,)
from fsleyes_widgets.placeholder_textctrl import (PlaceholderTextCtrl,)
from fsleyes_widgets.rangeslider          import (RangePanel,
                                                  RangeSliderSpinPanel,
                                                  RangeEvent,
                                                  LowRangeEvent,
                                                  HighRangeEvent,
                                                  RangeLimitEvent,
                                                  RP_INTEGER,
                                                  RP_MOUSEWHEEL,
                                                  RP_SLIDER,
                                                  RP_NO_LIMIT,
                                                  RSSP_INTEGER,
                                                  RSSP_MOUSEWHEEL,
                                                  RSSP_SHOW_LIMITS,
                                                  RSSP_EDIT_LIMITS,
                                                  RSSP_NO_LIMIT,
                                                  EVT_RANGE,
                                                  EVT_LOW_RANGE,
                                                  EVT_HIGH_RANGE,
                                                  EVT_RANGE_LIMIT)
from fsleyes_widgets.textpanel            import (TextPanel,)
from fsleyes_widgets.texttag              import (StaticTextTag,
                                                  TextTagPanel,
                                                  StaticTextTagCloseEvent,
                                                  TextTagPanelTagAddedEvent,
                                                  TextTagPanelTagRemovedEvent,
                                                  TextTagPanelTagSelectEvent,
                                                  EVT_STT_CLOSE,
                                                  TTP_ADD_NEW_TAGS,
                                                  TTP_ALLOW_NEW_TAGS,
                                                  TTP_NO_DUPLICATES,
                                                  TTP_CASE_SENSITIVE,
                                                  TTP_KEYBOARD_NAV,
                                                  EVT_TTP_TAG_ADDED,
                                                  EVT_TTP_TAG_REMOVED,
                                                  EVT_TTP_TAG_SELECT)
from fsleyes_widgets.togglepanel          import (TogglePanel,
                                                  TogglePanelEvent,
                                                  EVT_TOGGLEPANEL_EVENT)
from fsleyes_widgets.widgetgrid           import (WidgetGrid,
                                                  WidgetGridSelectEvent,
                                                  WidgetGridReorderEvent,
                                                  WG_SELECTABLE_CELLS,
                                                  WG_SELECTABLE_ROWS,
                                                  WG_SELECTABLE_COLUMNS,
                                                  WG_KEY_NAVIGATION,
                                                  WG_DRAGGABLE_COLUMNS,
                                                  EVT_WG_SELECT,
                                                  EVT_WG_REORDER)
from fsleyes_widgets.widgetlist           import (WidgetList,
                                                  WidgetListChangeEvent,
                                                  WidgetListExpandEvent,
                                                  WL_ONE_EXPANDED,
                                                  EVT_WL_CHANGE_EVENT,
                                                  EVT_WL_EXPAND_EVENT)


from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("fsleyes-widgets")
except PackageNotFoundError:
    __version__ = '<unknown>'

del version, PackageNotFoundError
