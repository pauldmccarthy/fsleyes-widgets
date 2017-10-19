 ``fsleyes-widgets`` release history
====================================


0.1.0 (Thursday October 19th 2017)
----------------------------------


* Fixes to the ``AutoTextCtrl`` and ``AutoCompletePopup`` so they work correctly
  in floating dialogs.
* New ``fsleyes_widgets.utils.progress`` module, which contains convenience
  classes and functions based on the ``wx.ProgressDialog``.
* New package-level function ``isalive`` to test whether a widget is alive or
  not.


0.0.6 (Thursday August 10th 2017)
---------------------------------


* New class ``togglepanel.TogglePanel`` used by ``WidgetList`` in place of
  ``wx.CollapsiblePane``
* ``TypeDict.get`` method has option to ignore class hierarchy, and only
  return hits for the specifie type.


0.0.5 (Friday July 14th 2017)
-----------------------------


* New style flag on ``WidgetList`` which allows at most one group to be
  expanded at any one time.


0.0.4 (Sunday June 11th 2017)
-----------------------------


* wxPython/Phoenix compatibility fixes in ``ColourButton`` and
  ``WidgetList``
* Removed obsolete code in ``WidgetGrid``.
* Removed python2/3 checks in favour of wxPython/Phoenix checks in
  ``textpanel``, ``floatspin``, and ``dialog``.


0.0.3 (Thursday June 8th 2017)
------------------------------


* Added CI build script
* Added ``wxversion`` function.
* wxPython/Phoenix compatibilty fix in ``WidgetGrid``.


0.0.2 (Sunday June 4th 2017)
----------------------------


* Adjustments to pypi package metadata.



0.0.1 (Saturday May 27th 2017)
------------------------------


* First public release as part of FSLeyes 0.11.0