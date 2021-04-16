fsleyes-widgets
===============


.. image:: https://img.shields.io/pypi/v/fsleyes-widgets.svg
   :target: https://pypi.python.org/pypi/fsleyes-widgets/

.. image:: https://anaconda.org/conda-forge/fsleyes-widgets/badges/version.svg
   :target: https://anaconda.org/conda-forge/fsleyes-widgets

.. image:: https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets/badges/master/coverage.svg
   :target: https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets/commits/master/


The ``fsleyes-widgets`` package contains a collection of GUI widgets and
utilities, based on `wxPython <http://www.wxpython.org>`_. These widgets are
used by `fsleyes-props <https://git.fmrib.ox.ac.uk/fsl/fsleyes/props>`_ and
`FSLeyes <https://git.fmrib.ox.ac.uk/fsl/fsleyes/fsleyes>`_,


Installation
------------


You can install ``fsleyes-widgets`` via pip. If you are using Linux, you need
to install wxPython first, as binaries are not available on PyPI. Change the
URL for your specific platform::

    pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/ wxpython


Then install ``fsleyes-widgets`` like so::

    pip install fsleyes-widgets


``fsleyes-widgets`` is also available on
`conda-forge <https://conda-forge.org/>`_::

    conda install -c conda-forge fsleyes-widgets


Dependencies
------------


All of the dependencies of ``fsleyes-widgets`` are listed in the
`requirements.txt <requirements.txt>`_ file.

Requirements for running tests and building the documentation are listed in the
`requirements-dev.txt <requirements-dev.txt>`_ file.


Documentation
-------------


API documentation for ``fsleyes-widgets`` can be found at
https://open.win.ox.ac.uk/pages/fsl/fsleyes/widgets/.

``fsleyes-widgets`` is documented using `sphinx
<http://http://sphinx-doc.org/>`_. You can build the API documentation by
running::

    pip install -r requirements-dev.txt
    python setup.py doc

The HTML documentation will be generated and saved in the ``doc/html/``
directory.


Tests
-----

Run the test suite via::

    pip install -r requirements-dev.txt
    python setup.py test


Many of the tests assume that a display is accessible - if you are running on
a headless machine, you may need to run the tests using ``xvfb-run``.


Contributing
------------

If you would like to contribute to ``fsleyes-widgets``, take a look at the
``fslpy`` `contributing guide
<https://git.fmrib.ox.ac.uk/fsl/fslpy/blob/master/doc/contributing.rst>`_.
