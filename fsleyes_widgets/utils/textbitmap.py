#!/usr/bin/env python
#
# textbitmap.py - A function which renders some text using matplotlib, and
# returns it as an RGBA bitmap.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides a single function, :func:`textBitmap`, which renders
some text off-screen using :mod:`matplotlib`, and returns it as an RGBA bitmap.
"""


def textBitmap(text,
               width=None,
               height=None,
               fontSize=None,
               fgColour=None,
               bgColour=None,
               alpha=1.0,
               fontFamily=None,
               dpi=96):
    """Draw some text using :mod:`matplotlib`.

    The rendered text is returned as a RGBA bitmap within a ``numpy.uint8``
    array of size :math:`h \\times w \\times 4`, with the top-left pixel
    located at index ``[0, 0, :]``.

    At least one of the ``fontSize`` or the ``height`` arguments need to be
    specified - if one of these is provided, the other size options will be
    inferred, although the inference procedure does not support multi-line
    text.

    :arg text:       Text to render.

    :arg width:      Width in pixels.

    :arg height:     Height in pixels.

    :arg fontSize:   Font size in points.

    :arg fgColour:   Foreground (text) colour - can be any colour specification
                     that is accepted by :mod:`matplotlib`.

    :arg bgColour:   Background colour  - can be any colour specification that
                     is accepted by :mod:`matplotlib`..

    :arg alpha:      Text transparency, in the range ``[0.0 - 1.0]``.

    :arg fontFamily: Font family, e.g. ``'monospace'`` or ``'sans-serif'``,
                     defaults to matplotlib default.

    :arg dpi:        Dots per inch, defaults to 96.

    :returns:        ``numpy.uint8`` array of size
                     :math:`h \\times w \\times 4`
    """

    if text is None or text.strip() == '':
        raise ValueError('Some text must be specified.')

    if (fontSize is None) and (height is None):
        raise ValueError('One of fontSize or height must be specified.')

    # Imports are expensive
    import numpy                           as np
    import matplotlib.backends.backend_agg as mplagg
    import matplotlib.figure               as mplfig

    # convert points to pixels or vice versa -
    # one point is 0,0138889 inches. Estimate
    # width from font size if not provided -
    # we will crop the result afterwards.
    crop = width is None
    if fontSize is None: fontSize = height   / 0.0138889 / dpi
    if height   is None: height   = fontSize * 0.0138889 * dpi
    if width    is None: width    = max(fontSize, fontSize * len(text))
    if fgColour is None: fgColour = '#000000'

    fig    = mplfig.Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    canvas = mplagg.FigureCanvasAgg(fig)
    ax     = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    if bgColour is not None: fig.patch.set_facecolor(bgColour)
    else:                    fig.patch.set_alpha(0)

    ax.set_xticks([])
    ax.set_yticks([])

    textobj = ax.text(0.5,
                      0.5,
                      text,
                      fontsize=fontSize,
                      verticalalignment='center',
                      horizontalalignment='center',
                      transform=ax.transAxes,
                      color=fgColour,
                      alpha=alpha,
                      fontfamily=fontFamily)

    # if a width wasn't specified, we auto-
    # fit the bitmap to the rendered text
    if crop:
        bbox = textobj.get_window_extent(renderer=canvas.get_renderer())
        if bbox.width < width:
            fig.set_size_inches((bbox.width / dpi, height / dpi))

    # no padding
    fig.subplots_adjust(
        bottom=0,
        top=1,
        left=0,
        right=1)

    canvas.draw()

    # get the bitmap data and reshape
    # and transpose it to (H, W, [RGBA])
    ncols, nrows = canvas.get_width_height()
    bitmap       = canvas.tostring_argb()
    bitmap       = np.frombuffer(bitmap, dtype=np.uint8)
    bitmap       = bitmap.reshape(nrows, ncols, 4)
    rgb          = bitmap[:, :, 1:]
    a            = bitmap[:, :, 0]
    bitmap       = np.dstack((rgb, a))

    return bitmap
