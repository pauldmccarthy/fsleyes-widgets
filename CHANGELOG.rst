This document contains the ``fsleyes-widgets`` release history in reverse
chronological order.


0.14.4 (Thursday April 4th 2024)
--------------------------------


Changed
^^^^^^^


* Changed the initial directory used by the ``$FSLDIR`` selection dialog to
  ``$HOME`` (previously ``/usr/local/``).


0.14.3 (Thursday July 6th 2023)
-------------------------------


Changed
^^^^^^^

* Updated the :class:`.WidgetList` to allow empty/spacer elements within
  embedded ``Sizer`` objects.


Fixed
^^^^^

* Fixed some issues with API documentation.


0.14.2 (Tuesday June 7th 2023)
------------------------------


Changed
^^^^^^^


* Change the default ``spinWidth`` to ``6`` for the :class:`.SliderSpinPanel`
  and :class:`.RangeSliderSpinPanel`.


0.14.1 (Monday April 17th 2023)
-------------------------------


Changed
^^^^^^^


* Use ``numpy`` rather than ``scipy`` for interpolation to keep the
  dependencies of ``fsleyes-widgets`` minimal.


0.14.0 (Monday April 17th 2023)
-------------------------------


Changed
^^^^^^^


* Added support for interpolation and logarithmic scaling to the functions in
  the :mod:`.colourbarbitmap` module.


0.13.0 (Monday February 20th 2023)
----------------------------------


Changed
^^^^^^^


* ``fsleyes-widgets`` now requires ``matplotlib >= 3.5.0``, and has been
  updated to use the new ``matplotlib.colormaps`` registry.


0.12.3 (Friday April 29th 2022)
-------------------------------


Added
^^^^^


* New ``halign`` option for the :func:`.textBitmap` functionm, controlling
  horizontal alignment.
* The :func:`.textBitmap` function now accepts multi-line strings.


0.12.2 (Wednesday October 6th 2021)
-----------------------------------


Added
^^^^^


* New :data:`.ATC_NO_PROPAGATE_ENTER` style flag for the
  :class:`.AutoTextCtrl`.


0.12.1 (Wednesday April 21st 2021)
----------------------------------


Changed
^^^^^^^


* Removed some hard-coded colours to improve support for dark themes.


0.12.0 (Tuesday April 20th 2021)
--------------------------------


Changed
^^^^^^^


* The :class:`.wxPlatform` function now differentiates between GTK2 and GTK3
  ``wxPython`` builds.



0.11.3 (Friday April 16th 2021)
-------------------------------


Changed
^^^^^^^


* Added the :meth:`.EditableListBox.MoveItem` method (it was previously a
  private method called ``__moveItem``).


0.11.2 (Saturday March 27th 2021)
---------------------------------


Changed
^^^^^^^


* The :class:`.BitmapRadioBox` now allows all items to be de-selected,
  by using the :attr:`.BMPRADIO_ALLOW_DESELECTED` style.


0.11.1 (Tuesday March 9th 2021)
-------------------------------


Changed
^^^^^^^

* The ``fsleyes-widgets`` API documentation is now hosted at
  https://open.win.ox.ac.uk/pages/fsl/fsleyes/widgets/
* Removed some uses of the deprecated :func:`.wxversion` function.


0.11.0 (Thursday February 18th 2021)
------------------------------------


Added
^^^^^


* New functions for querying the environment at runtime, including,
  :func:`.wxVersion` (not to be confused with the deprecated
  :func:`.wxversion`), :func:`.wxPlatform`, :func:`.wxFlavour`,
  :func:`.frozen`, :func:`.canHaveGui`, :func:`.haveGui`,
  :func:`.inSSHSession`, and :func:`.inVNCSession`.


Deprecated
^^^^^^^^^^


* The :func:`.wxversion` function has been replaced by :func:`wxFlavour`.


0.10.0 (Wednesday February 10th 2021)
-------------------------------------


Changed
^^^^^^^


* The `.textBitmap` function has been made more flexible, and can
  automatically infer the width/height of the bitmap given just a font size.


0.9.0 (Thursday June 4th 2020)
------------------------------


Added
^^^^^


* The :class:`.FloatSpinCtrl` has a new ``precision`` option, allowing
  the displayed precision to be specified (!52, !54).


Fixed
^^^^^


* Fixed a bug in the :class:`.AutoCompletePopup`, which could cause a
  segmentation fault on GTK (!53).


0.8.4 (Wednesday October 9th 2019)
----------------------------------


Added
^^^^^


* New :meth:`.status.ClearThreaad.die` method, used for testing purposes.



0.8.3 (Friday October 4th 2019)
-------------------------------


Added
^^^^^


* New ``vgap`` option for the :class:`.EditableListBox`.
* New ``minHeight`` option for the :class:`.WidgetList`.


Changed
^^^^^^^


* Minor GTK3 compatibility fixes.


0.8.2 (Wednesday September 18th 2019)
-------------------------------------


Changed
^^^^^^^


* ``fsleyes-widgets`` is now tested against Python 3.6, 3.7 and 3.8, and GTK3.


Fixed
^^^^^


* Fixed minor mis-usage of ``wx.BoxSizer`` in the :class:`.Notebook` class.


0.8.1 (Tuesday September 10th 2019)
-----------------------------------


Fixed
^^^^^


* Fixed a bug in the :class:`.WidgetGrid` where scrolling behaviour was not
  being initialised correctly.


0.8.0 (Wednesday August 21st 2019)
----------------------------------


Added
^^^^^


* New :meth:`.EditableListBox.GetWidgets` method.
* New :meth:`.WidgetList.GetWidgets` method.
* New :data:`.WG_DRAGGABLE_COLUMNS` style and
  :meth:`.WidgetGrid.ReorderColumns` and :meth:`.WidgetGrid.SetDragLimits`
  methods, allowing columns to be re-ordered by clicking and dragging the
  column labels.
* New :meth:`.WidgetGrid.GetRowLabels`, :meth:`.WidgetGrid.GetColLabels`,
  :meth:`.WidgetGrid.SetRowLabels`, :meth:`.WidgetGrid.SetColLabels`,
  :meth:`.WidgetGrid.GetRowLabel`, and :meth:`.WidgetGrid.GetColLabel`
  accessor methods.
* New :mod:`.b64icon` module, for loading base64-encoded images.
* New :mod:`.overlay` module, for drawing overlays on any widget. Currently
  only one function - :func:`.textOverlay` - is available.


Changed
^^^^^^^


* ``fsleyes-widgets`` is no longer tested against Python 2.7 or 3.4.


Fixed
^^^^^


* Fixed a bug in the :class:`.ImagePanel` aspect ratio calculation.


0.7.3 (Monday January 7th 2019)
-------------------------------


Changed
^^^^^^^


* Removed ``deprecation`` as a dependency.


0.7.2 (Friday November 23rd 2018)
---------------------------------


Fixed
^^^^^


* Fixed a small regression in the :func:`.colourBarBitmap` function.


0.7.1 (Friday November 23rd 2018)
---------------------------------


Changed
^^^^^^^


* Refactored the :func:`.colourBarBitmap` function to better handle larger
  font sizes.


0.7.0 (Sunday October 21st 2018)
--------------------------------


Added
^^^^^


* The :class:`.Notebook` class allows the text colour of buttons for
  disabled pages to be changed.
* The :class:`.ImagePanel` has a new option to preserve the aspect
  ratio of the displayed image.


0.6.6 (Saturday October 13th 2018)
----------------------------------


Changed
^^^^^^^


* Made some more tests a little more lenient.



0.6.5 (Monday October 8th 2018)
-------------------------------


Changed
^^^^^^^


* Made some tests more lenient due to tiny cross-platform differences..


0.6.4 (Friday October 5th 2018)
-------------------------------


Changed
^^^^^^^


* Development (test and documentation dependencies) are no longer listed
  in ``setup.py`` - they now need to be installed manually.
* Removed conda build infrastructure.


0.6.3 (Tuesday August 28th 2018)
--------------------------------


Changed
^^^^^^^


* The :func:`.reportIfError` function no longer emits a stack trace when
  logging errors.


0.6.2 (Tuesday June 5th 2018)
-----------------------------


Changed
^^^^^^^


* The :class:`.ImagePanel` does not update its minimum size based on the image
  size - this is left entirely up to application code.


Fixed
^^^^^


* Fixed some minor bugs in the :mod:`.colourbarbitmap`.


0.6.1 (Friday May 11th 2018)
----------------------------


Added
^^^^^


* The :func:`.colourBarBitmap` function accepts a new ``scale`` parameter,
  to allow scaling for high-DPI displays.


0.6.0 (Wednesday May 2nd 2018)
------------------------------


Added
^^^^^


* New ``gamma`` option to the :func:`.colourbarbitmap` function, allowing
  an exponential weighting to be applied to colour bars.


Changed
^^^^^^^


* :meth:`.BitmapRadioBox.Enable` and :meth:`.BitmapRadioBox.Disable` renamed
  to :meth:`.BitmapRadioBox.EnableChoice` and
  :meth:`.BitmapRadioBox.DisableChoice`. The former methods were masking,
  and had different semantics to, ``wx.Panel.Enable`` and ``wx.Panel.Disable``.


0.5.4 (Tuesday March 6th 2018)
------------------------------


* Small adjustment to conda build and deployment process.


0.5.3 (Monday March 5th 2018)
-----------------------------


* Added CI infrastructure for building conda packages.


0.5.2 (Tuesday February 27th 2018)
----------------------------------


* Fixed a regression in the :func:`.isalive` function.



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
