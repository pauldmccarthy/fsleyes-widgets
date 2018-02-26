This document contains the ``fsleyes-widgets`` release history in reverse
chronological order.



0.5.1 (Monday February 26th 2018)
---------------------------------


* Small adjustment to the :class:`.Notebook` minimum size calculation.


0.5.0 (Monday February 26th 2018)
---------------------------------


* The :class:`.Notebook` class now emits an :data:`.EVT_PAGE_CHANGED` event
  when the selected page is changed.
* Various bug-fixes to the :class:`.Notebook` class.
* :class:`.FloatSpinCtrl` widgets should now accept numbers in scientific
  notation.


0.4.1 (Thursday January 25th 2018)
----------------------------------


* Minor internal adjustment to the :class:`.FloatSpin` class.


0.4.0 (Monday January 8th 2018)
-------------------------------


* The :class:`.TextPanel` class now honours background and foreground colours.
* The :class:`.Notebook` class now allows customisation of its style, border,
  and button side, orientation and colours.


0.3.2 (Tuesday January 2nd 2018)
--------------------------------


* More adjustments to :func:`.progress.runWithBounce` function.


0.3.1 (Thursday December 14th 2017)
-----------------------------------


* Further internal adjustments to :func:`.progress.runWithBounce` function.


0.3.0 (Thursday December 14th 2017)
-----------------------------------


* New :func:`.progress.bounce` function which allows a :class:`.Bounce`
  dialog to be used within a context manager.
* Deprecated the :meth:`.Bounce.runWithBounce` method, in favour of a
  new standalone :func:`.progress.runWithBounce` function.
* :func:`.progress.runWithBounce` modified to be non-blocking, as
  ``wx.Yield`` loops are very unreliable.


0.2.1 (Monday December 5th 2017)
--------------------------------


* :class:`.Bounce` class can now be manually or automatically controlled.
* Some adjustments to the :class:`.EditableListBox` - it was potentially
  calculating item heights incorrectly.
* Unit tests are now run against wxPython 3.0.2.0.


0.2.0 (Monday October 30th 2017)
--------------------------------


* :class:`.AutoTextCtrl` and :class:`.AutoCompletePopup` have properties to
  allow access to their internal ``wx`` controls - these are used for unit
  testing.
* The :class:`.AutoCompletePopup` runs its own ``wx`` event loop while it is
  displayed, so that events are not caught by other active modal dialogs.
* Fixed issue with :class:`.NumberDialog` returning a value when it has
  been shown non-modally and cancelled.
* Fixed python 2/3 compatibility issue with :class:`.TogglePanel`.
* Fixed issue with :class:`.WidgetGrid` not initialising colours correctly.
* Deprecated the :meth:`.TogglePanel.GetToggleButton` method, in favour of a
  new ``button`` property.
* Added the  ``deprecation`` library as a new dependency.


0.1.0 (Thursday October 19th 2017)
----------------------------------


* Fixes to the :class:`.AutoTextCtrl` and :class:`.AutoCompletePopup` so they
  work correctly in floating dialogs.
* New :mod:`fsleyes_widgets.utils.progress` module, which contains convenience
  classes and functions based on the ``wx.ProgressDialog``.
* New package-level function :func:`.isalive` to test whether a widget is
  alive or not.


0.0.6 (Thursday August 10th 2017)
---------------------------------


* New class :class:`.togglepanel.TogglePanel` used by :class:`.WidgetList` in
  place of ``wx.CollapsiblePane``.
* :meth:`.TypeDict.get` method has option to ignore class hierarchy, and only
  return hits for the specifie type.


0.0.5 (Friday July 14th 2017)
-----------------------------


* New style flag on :class:`.WidgetList` which allows at most one group to be
  expanded at any one time.


0.0.4 (Sunday June 11th 2017)
-----------------------------


* wxPython/Phoenix compatibility fixes in :class:`.ColourButton` and
  :class:`.WidgetList`.
* Removed obsolete code in :class:`.WidgetGrid`.
* Removed python2/3 checks in favour of wxPython/Phoenix checks in
  :mod:`.textpanel`, :mod:`.floatspin`, and :mod:`.dialog`.


0.0.3 (Thursday June 8th 2017)
------------------------------


* Added CI build script
* Added :func:`.wxversion` function.
* wxPython/Phoenix compatibilty fix in :class:`.WidgetGrid`.


0.0.2 (Sunday June 4th 2017)
----------------------------


* Adjustments to pypi package metadata.



0.0.1 (Saturday May 27th 2017)
------------------------------


* First public release as part of FSLeyes 0.11.0
