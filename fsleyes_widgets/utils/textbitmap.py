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


POINT_SIZE = 1 / 72
"""Size of one point in inches at 72 dpi. Font sizes are specified in points at
72 dpi - this value is used to convert from font size to inches (and on to
pixels).
"""


def textBitmap(text,
               width=None,
               height=None,
               fontSize=None,
               fgColour=None,
               bgColour=None,
               alpha=1.0,
               fontFamily=None,
               halign=None,
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

    :arg halign:     Horizontal alignment - one of ``'centre'`` (default),
                     ``'center'``, ``'left'`` or ``right'``.

    :returns:        ``numpy.uint8`` array of size
                     :math:`h \\times w \\times 4`
    """

    if text is None or text.strip() == '':
        raise ValueError('Some text must be specified.')

    if (fontSize is None) and (height is None):
        raise ValueError('One of fontSize or height must be specified.')

    if halign in (None, 'centre'):
        halign = 'center'

    # Imports are expensive
    import numpy                           as np
    import matplotlib.backends.backend_agg as mplagg
    import matplotlib.transforms           as mplxf
    import matplotlib.figure               as mplfig

    # convert points to pixels or vice versa.
    # Estimate width from font size if not
    # provided - we will crop the result
    # afterwards.
    crop   = width is None
    nlines = text.count('\n') + 1
    if fontSize is None: fontSize =          height   / POINT_SIZE / dpi
    if height   is None: height   = nlines * fontSize * POINT_SIZE * dpi
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

    if   halign == 'left':  tx = 0.0
    elif halign == 'right': tx = 1.0
    else:                   tx = 0.5

    textobj = ax.text(tx,
                      0.5,
                      text,
                      fontsize=fontSize,
                      verticalalignment='center',
                      horizontalalignment=halign,
                      transform=ax.transAxes,
                      color=fgColour,
                      alpha=alpha,
                      fontfamily=fontFamily)

    # if a width wasn't specified, we auto-
    # fit the bitmap to the rendered text
    if crop:
        # tight bounding box around text
        bbox = textobj.get_window_extent(renderer=canvas.get_renderer())

        # a tiny amount seems to get cropped on the right, for
        # centre/right aligned text. So we shift the text left
        # a little, and add some padding to the figure size.
        if halign == 'left': offset = 0
        else:                offset = POINT_SIZE * 2

        textobj.set_transform(mplxf.offset_copy(
            textobj.get_transform(), fig, -offset, 0))

        fig.set_size_inches((offset + bbox.width / dpi, height / dpi))

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
