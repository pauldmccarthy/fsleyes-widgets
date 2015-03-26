#!/usr/bin/env python
#
# volumeopts.py - Defines the VolumeOpts class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module defines the :class:`VolumeOpts` class, which contains
display options for rendering :class:`~fsl.fslview.gl.glvolume.GLVolume`
instances.
"""

import logging

import numpy as np

import props

import fsl.data.strings       as strings
import fsl.fslview.colourmaps as fslcm

import display as fsldisplay


log = logging.getLogger(__name__)


# TODO Define a super/mixin class which
# has a displayRange and colour map. This
# will allow other bits of code which
# need display range/cmap options to
# test for their presence without having
# to explicitly test against the VolumeOpts
# class (and other future *Opts classes
# which have a display range/cmap).


class VolumeOpts(fsldisplay.DisplayOpts):
    """A class which describes how an :class:`~fsl.data.image.Image` should
    be displayed.

    This class doesn't have much functionality - it is up to things which
    actually display an :class:`~fsl.data.image.Image` to adhere to the
    properties stored in the associated :class:`ImageDisplay` object.
    """

    
    displayRange = props.Bounds(
        ndims=1,
        labels=[strings.choices['VolumeOpts.displayRange.min'],
                strings.choices['VolumeOpts.displayRange.max']])
    """Image values which map to the minimum and maximum colour map colours."""

    
    clippingRange = props.Bounds(
        ndims=1,
        labels=[strings.choices['VolumeOpts.displayRange.min'],
                strings.choices['VolumeOpts.displayRange.max']]) 

    
    cmap = props.ColourMap(default=fslcm.getDefault(),
                           cmapNames=fslcm.getColourMaps())
    """The colour map, a :class:`matplotlib.colors.Colourmap` instance."""


    invert = props.Boolean(default=False)
    """Invert the colour map."""

    
    _tooltips = {
        'name'          : 'The name of this image',
        'enabled'       : 'Enable/disable this image',
        'alpha'         : 'Opacity, between 0.0 (transparent) '
                          'and 100.0 (opaque)',
        'displayRange'  : 'Minimum/maximum display values',
        'clipLow'       : 'Do not show image values which are '
                          'lower than the display range',
        'clipHigh'      : 'Do not show image values which are '
                          'higher than the display range', 
        'interpolation' : 'Interpolate between voxel values at '
                          'each displayed real world location',
        'resolution'    : 'Data resolution in voxels',
        'volume'        : 'Volume number (for 4D images)',
        'transform'     : 'The transformation matrix which specifies the '
                          'conversion from voxel coordinates to a real '
                          'world location',
        'imageType'     : 'the type of data contained in the image',
        'cmap'          : 'Colour map'}

    
    _propHelp = _tooltips


    def __init__(self, image, display, imageList, displayCtx, parent=None):
        """Create an :class:`ImageDisplay` for the specified image.

        See the :class:`~fsl.fslview.displaycontext.display.DisplayOpts`
        documentation for more details. 
        """

        # Attributes controlling image display. Only
        # determine the real min/max for small images -
        # if it's memory mapped, we have no idea how big
        # it may be! So we calculate the min/max of a
        # sample (either a slice or an image, depending
        # on whether the image is 3D or 4D)
        if np.prod(image.shape) > 2 ** 30:
            sample = image.data[..., image.shape[-1] / 2]
            self.dataMin = float(sample.min())
            self.dataMax = float(sample.max())
        else:
            self.dataMin = float(image.data.min())
            self.dataMax = float(image.data.max())

        dRangeLen    = abs(self.dataMax - self.dataMin)
        dMinDistance = dRangeLen / 10000.0

        self.clippingRange.xmin = self.dataMin - dMinDistance
        self.clippingRange.xmax = self.dataMax + dMinDistance
        
        # By default, the lowest values
        # in the image are clipped
        self.clippingRange.xlo  = self.dataMin + dMinDistance
        self.clippingRange.xhi  = self.dataMax + dMinDistance

        self.displayRange.xlo  = self.dataMin
        self.displayRange.xhi  = self.dataMax

        # The Display.contrast property expands/contracts
        # the display range, by a scaling factor up to
        # approximately 10.
        self.displayRange.xmin = self.dataMin - 10 * dRangeLen
        self.displayRange.xmax = self.dataMax + 10 * dRangeLen
        
        self.setConstraint('displayRange', 'minDistance', dMinDistance)

        fsldisplay.DisplayOpts.__init__(self,
                                        image,
                                        display,
                                        imageList,
                                        displayCtx,
                                        parent,
                                        nounbind=('displayRange'))

        # Bricon values are synchronised with
        # displayRange values on the parent
        # VolumeOpts instance. If these listeners
        # are registered on child instances, and
        # there are multiple children, horrible
        # semi-infniite recursive listener callback
        # madness will entail ...
        #
        # TODO Problem here is that if a child
        #      instance disables synchronisation
        #      on brightness/contrast with the
        #      parent, the bricon-displayRange
        #      synchronsiation no longer occurs
        #      on the child .. This is why
        #      displayRange currently cannot be
        #      unbound between parent/child
        #      instances (constructor above). 
        #      Same goes for Display.bricon
        #      properties
        
        if parent is None:
            display.addListener('brightness', self.name, self.briconChanged)
            display.addListener('contrast',   self.name, self.briconChanged)
            self   .addListener('displayRange',
                                self.name,
                                self.displayRangeChanged)


    def briconChanged(self, *a):
        """Called when the ``brightness``/``contrast`` properties of the
        :class:`~fsl.fslview.displaycontext.display.Display` instance change.
        
        Updates the :attr:`displayRange` property accordingly.
        """

        display = self.display

        # Turn the bricon percentages into
        # values between 1 and 0 (inverted)
        brightness = 1 - self.display.brightness / 100.0
        contrast   = 1 - self.display.contrast   / 100.0

        dmin, dmax = self.dataMin, self.dataMax
        drange     = dmax - dmin
        dmid       = dmin + 0.5 * drange

        # The brightness is applied as a linear offset,
        # with 0.5 equivalent to an offset of 0.0.                
        offset = (brightness * 2 - 1) * drange

        # If the contrast lies between 0.0 and 0.5, it is
        # applied to the colour as a linear scaling factor.
        scale = contrast * 2

        # If the contrast lies between 0.5 and 0.1, it
        # is applied as an exponential scaling factor,
        # so lower values (closer to 0.5) have less of
        # an effect than higher values (closer to 1.0).
        if contrast > 0.5:
            scale += np.exp((contrast - 0.5) * 6) - 1
            
        # Calculate the new display range, keeping it
        # centered in the middle of the data range
        # (but offset according to the brightness)
        dlo = (dmid + offset) - 0.5 * drange * scale 
        dhi = (dmid + offset) + 0.5 * drange * scale

        self   .disableListener('displayRange', self.name)
        display.disableListener('brightness',   self.name)
        display.disableListener('contrast',     self.name)
        
        self.displayRange.x = [dlo, dhi]
        
        self   .enableListener('displayRange', self.name)
        display.enableListener('brightness',   self.name)
        display.enableListener('contrast',     self.name) 

        
    def displayRangeChanged(self, *a):

        display    = self.display
        
        dmin, dmax = self.dataMin, self.dataMax
        drange     = dmax - dmin
        dmid       = dmin + 0.5 * drange

        dlo, dhi = self.displayRange.x

        # Inversions of the equations in briconChanged
        # above, which calculate the display ranges
        # from the bricon offset/scale
        offset = dlo + 0.5 * (dhi - dlo) - dmid
        scale  = (dhi - dlo) / drange

        brightness = 0.5 * (offset / drange + 1)

        if scale <= 1: contrast = scale / 2.0
        else:          contrast = np.log(scale + 1) / 6.0 + 0.5

        self   .disableListener('displayRange', self.name)
        display.disableListener('brightness',   self.name)
        display.disableListener('contrast',     self.name)

        # update bricon
        display.brightness = 100 - brightness * 100
        display.contrast   = 100 - contrast   * 100

        self   .enableListener('displayRange', self.name)
        display.enableListener('brightness',   self.name)
        display.enableListener('contrast',     self.name)
