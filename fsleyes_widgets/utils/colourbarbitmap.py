#!/usr/bin/env python
#
# colourbarbitmap.py - A function which renders a colour bar using
# matplotlib as an RGBA bitmap.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides a single function, :func:`colourBarBitmap`, which uses
:mod:`matplotlib` to plot a colour bar. The colour bar is rendered off-screen
and returned as an RGBA bitmap.
"""


def colourBarBitmap(cmap,
                    width,
                    height,
                    cmapResolution=256,
                    negCmap=None,
                    invert=False,
                    gamma=1,
                    ticks=None,
                    ticklabels=None,
                    tickalign=None,
                    label=None,
                    orientation='vertical',
                    labelside='top',
                    alpha=1.0,
                    fontsize=10,
                    bgColour=None,
                    textColour='#ffffff',
                    scale=1.0,
                    interp=False,
                    logScaleRange=None,
                    modAlpha=False,
                    invModAlpha=False,
                    displayRange=None,
                    modRange=None):
    """Plots a colour bar using :mod:`matplotlib`.


    The rendered colour bar is returned as a RGBA bitmap within a
    ``numpy.uint8`` array of size :math:`w \\times h \\times 4`, with the
    top-left pixel located at index ``[0, 0, :]``.


    A rendered colour bar will look something like this:

    .. image:: images/colourbarbitmap.png
       :scale: 50%
       :align: center


    :arg cmap:           Name of a registered :mod:`matplotlib` colour map.

    :arg width:          Colour bar width in pixels.

    :arg height:         Colour bar height in pixels.

    :arg cmapResolution: Colour map resolution (number of distinct colours).

    :arg negCmap:        If provided, two colour maps are drawn, centered at 0.

    :arg invert:         If ``True``, the colour map is inverted.

    :arg gamma:          Gamma correction factor - exponentially weights the
                         colour map scale towards one end.

    :arg ticks:          Locations of tick labels. Ignored if
                         ``ticklabels is None``.

    :arg ticklabels:     Tick labels.

    :arg tickalign:      Tick alignment (one for each tick, either ``'left'``,
                         ``'right'``, or ``'center'``).

    :arg label:          Text label to show next to the colour bar.

    :arg orientation:    Either ``vertical`` or ``horizontal``.

    :arg labelside:      Side of the colour bar to put the label - ``top``,
                         ``bottom``, ``left`` or ``right``. If
                         ``orientation='vertical'``, then ``top``/``bottom``
                         are interpreted as ``left``/``right`` (and vice-versa
                         when ``orientation='horizontal'``).

    :arg alpha:          Colour bar transparency, in the range ``[0.0 - 1.0]``.

    :arg fontsize:       Label font size in points.

    :arg bgColour:       Background colour - can be any colour specification
                         that is accepted by :mod:`matplotlib`.

    :arg textColour:     Label colour - can be any colour specification that
                         is accepted by :mod:`matplotlib`.

    :arg scale:          DPI scaling factor.

    :arg interp:         If true, and the colour map has fewer colours than
                         ``cmapResolution``, it is linearly interpolated
                         to have ``cmapResolution``.

    :arg logScaleRange:  Tuple containing ``(min, max)`` display range to which
                         the colour bar is mapped to. If provided, the colour
                         bar will be scaled to the natural logarithm of the
                         display range.

    :arg modAlpha:       If ``True``, modulate the colour bar transparency
                         according to the modulate and display ranges, so that
                         colours at or below the low modulation range are
                         fully transparent, and colours at or above the high
                         modulation range have transparency set to ``alpha``.

    :arg invModAlpha:    If ``True``, flips the direction in which the colour
                         bar is modulated by transparency.

    :arg displayRange:   Low/high values corresponding to the low/high colours.
                         Required when ``modAlpha=True``.

    :arg modRange:       Low/high values between which transparency should be
                         modulated. Required when ``modAlpha=True``.
    """

    # These imports are expensive, so we're
    # importing at the function level.
    import numpy                           as np
    import matplotlib.backends.backend_agg as mplagg
    import matplotlib.figure               as mplfig

    if orientation not in ['vertical', 'horizontal']:
        raise ValueError('orientation must be vertical or '
                         f'horizontal ({orientation})')

    if orientation == 'horizontal':
        if   labelside == 'left':  labelside = 'top'
        elif labelside == 'right': labelside = 'bottom'
    else:
        if   labelside == 'top':    labelside = 'left'
        elif labelside == 'bottom': labelside = 'right'

    if labelside not in ['top', 'bottom', 'left', 'right']:
        raise ValueError('labelside must be top, bottom, '
                         f'left or right ({labelside})')

    if modAlpha:
        try:
            _, _ = displayRange
            _, _ = modRange
        except Exception:
            raise ValueError('displayRange and modRange must be '
                             'provided when modAlpha is True')

    # vertical plots are rendered horizontally,
    # and then simply rotated at the end
    if orientation == 'vertical':
        width, height = height, width
        if labelside == 'left': labelside = 'top'
        else:                   labelside = 'bottom'

    # Default is 96 dpi to an inch
    winches   = width  / 96.0
    hinches   = height / 96.0
    dpi       = scale  * 96.0
    ncols     = cmapResolution
    data      = genColours(cmap, ncols, invert, alpha,
                           gamma, interp, logScaleRange,
                           modAlpha, invModAlpha,
                           displayRange, modRange)

    if negCmap is not None:
        ndata  = genColours(negCmap, ncols, not invert, alpha,
                            gamma, interp, logScaleRange,
                            modAlpha, invModAlpha,
                            displayRange, modRange)
        data   = np.concatenate((ndata, data), axis=0)
        ncols *= 2

    # Turn from a 1D rgba vector into a 2D RGBA image
    data = np.dstack((data, data)).transpose((2, 0, 1))

    # force tick positions to
    # the left edge of the
    # corresponding colour
    if ticks is not None:
        ticks = [t - 0.5 / ncols for t in ticks]

    fig     = mplfig.Figure(figsize=(winches, hinches), dpi=dpi)
    canvas  = mplagg.FigureCanvasAgg(fig)
    ax      = fig.add_subplot(111)

    if bgColour is not None:
        fig.patch.set_facecolor(bgColour)
        ax.set_facecolor(bgColour)
    else:
        fig.patch.set_alpha(0)
        ax.set_alpha(0)

    # draw the colour bar
    ax.imshow(data,
              aspect='auto',
              origin='lower',
              interpolation='nearest')

    ax.set_yticks([])
    ax.tick_params(colors=textColour, labelsize=fontsize, length=0)

    if labelside == 'top':
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
    else:
        ax.xaxis.tick_bottom()
        ax.xaxis.set_label_position('bottom')

    if label is not None:
        ax.set_xlabel(label, fontsize=fontsize, color=textColour)
        label = ax.xaxis.get_label()

    if ticks is None or ticklabels is None:
        ax.set_xticks([])
    else:

        ax.set_xticks(np.array(ticks) * ncols)
        ax.set_xticklabels(ticklabels)
        ticklabels = ax.xaxis.get_ticklabels()

    # Resize the colour bar to make
    # space for the ticks and labels
    wpad        = 5 / float(width)
    hpad        = 5 / float(height)
    totalHeight = 1.0

    # Figure out text height in
    # pixels (with 6 pixel padding)
    fontpix    = (fontsize / 72.0) * dpi / scale
    textHeight = (fontpix + 6) / float(height)

    if label      is not None: totalHeight -= textHeight
    if ticklabels is not None: totalHeight -= textHeight

    if labelside == 'top': bottom, top = 0, totalHeight
    else:                  bottom, top = 1 - totalHeight, 1

    fig.subplots_adjust(
        left=wpad,
        right=1.0 - wpad,
        bottom=bottom + hpad,
        top=top - hpad)

    # Divide the vertical height between the
    # colour bar, the label, and the tick labels.
    if label is not None:

        # I don't understand why, but I have
        # to set va to the opposite of what
        # I would have thought.
        if labelside == 'top':
            label.set_va('bottom')
            label.set_position((0.5, 1.0))
        else:
            label.set_va('top')
            label.set_position((0.5, 0))

    # Adjust tick label horizontal alignment. This
    # must be done *after* calling tick_top/tick_bottom,
    # as I think the label objects get recreated.
    if ticklabels is not None and tickalign is not None:
        for l, a in zip(ticklabels, tickalign):
            l.set_horizontalalignment(a)

    ax.set_xlim((-0.5, ncols - 0.5))

    canvas.draw()

    buf = canvas.tostring_argb()
    ncols, nrows = canvas.get_width_height()

    bitmap = np.frombuffer(buf, dtype=np.uint8)
    bitmap = bitmap.reshape(nrows, ncols, 4).transpose([1, 0, 2])

    # the bitmap is in argb order,
    # but we want it in rgba
    rgb = bitmap[:, :, 1:]
    a   = bitmap[:, :, 0]
    bitmap = np.dstack((rgb, a))

    if orientation == 'vertical':
        bitmap = np.flipud(bitmap.transpose([1, 0, 2]))
        bitmap = np.rot90(bitmap, 2)

    return bitmap


def genColours(cmap,
               ncols,
               invert,
               alpha,
               gamma=1,
               interp=False,
               logScaleRange=None,
               modAlpha=False,
               invModAlpha=False,
               displayRange=None,
               modRange=None):
    """Generate an array containing ``ncols`` colours from the given
    colour map object/function.
    """

    import numpy      as np
    import matplotlib as mpl

    # cmap can be a mpl colormap object or name
    if isinstance(cmap, str):
        cmap  = mpl.colormaps[cmap]

    # Map display range to colour map logarithmically
    if logScaleRange is not None:
        dmin, dmax    = logScaleRange
        idxs          = np.linspace(dmin, dmax, ncols)
        idxs          = np.log(idxs)
        finite        = np.isfinite(idxs)
        imax          = idxs[finite].max()
        imin          = idxs[finite].min()
        idxs          = (idxs - imin) / (imax - imin)
        idxs[~finite] = 0

    # Map display range to colour map linearly
    else:
        idxs = np.linspace(0.0, 1.0, ncols)

    if gamma not in (None, 1):
        idxs = idxs ** gamma

    if invert:
        idxs = idxs[::-1]

    # interpolate if requested, and if the
    # number of colours in the cmap does
    # not match the requested resolution
    if interp and (ncols != cmap.N):
        rawidxs = np.linspace(0, 1, cmap.N)
        rawrgbs = cmap(rawidxs)
        rgbs    = np.zeros((ncols, 4), dtype=np.float32)
        for chan in range(3):
            rgbs[:, chan] = np.interp(idxs, rawidxs, rawrgbs[:, chan])
    else:
        rgbs = cmap(idxs)

    if not modAlpha:
        rgbs[:, 3] = alpha

    else:
        dmin, dmax = displayRange
        mmin, mmax = modRange
        amin, amax = 0, alpha

        if invModAlpha:
            amin, amax = amax, amin

        # mod range normalised to the range [0, 1]
        nmmin = (mmin - dmin) / (dmax - dmin)
        nmmax = (mmax - dmin) / (dmax - dmin)
        nmmin = np.clip(nmmin, 0, 1)
        nmmax = np.clip(nmmax, 0, 1)

        # mod range in terms of num colours (ncols)
        immin = int(np.round(ncols * nmmin))
        immax = int(np.round(ncols * nmmax))

        # mod range below or above display range
        if   nmmin == 1: rgbs[:, 3] = amin
        elif nmmax == 0: rgbs[:, 3] = amax

        # mod range overlapping with display range
        else:
            alphas              = np.zeros(ncols, dtype=np.float32)
            alphas[:immin]      = amin
            alphas[immax:]      = amax
            alphas[immin:immax] = np.linspace(amin, amax, abs(immax - immin))

            if invert: rgbs[:, 3] = alphas[::-1]
            else:      rgbs[:, 3] = alphas

    return rgbs
