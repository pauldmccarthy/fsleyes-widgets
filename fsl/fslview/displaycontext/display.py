#!/usr/bin/env python
#
# display.py - Definitions of the Display and DisplayOpts classes.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides definitions of an important class - the
:class:`Display` class.

A ``Display`` contains a specification for the way in which any overlays is to
be displayed.

..note:: Put a description of the three coordinate systems which
         exist in the system.
"""

import logging

import props

import fsl.data.image     as fslimage
import fsl.data.strings   as strings
import fsl.utils.typedict as td


log = logging.getLogger(__name__)


class DisplayOpts(props.SyncableHasProperties):


    bounds = props.Bounds(ndims=3)
    """Specifies a bounding box (in display coordinates) which is big enough
    to contain the overlay described by this ``DisplayOpts`` instance. The
    values in this ``bounds`` property  must be maintained by subclass
    implementations.

    Whenever the spatial representation of this overlay changes, but the
    bounds do not change, subclass implementations should force notification
    on this property (via the :meth:`.HasProperties.notify` method). 
    """

    def __init__(
            self,
            overlay,
            display,
            overlayList,
            displayCtx,
            parent=None,
            *args,
            **kwargs):
        
        props.SyncableHasProperties.__init__(self, parent, *args, **kwargs)
        
        self.overlay     = overlay
        self.display     = display
        self.overlayList = overlayList
        self.displayCtx  = displayCtx
        self.overlayType = display.overlayType
        self.name        = '{}_{}'.format(type(self).__name__, id(self))

        log.memory('{}.init ({})'.format(type(self).__name__, id(self)))

        
    def __del__(self):
        log.memory('{}.del ({})'.format(type(self).__name__, id(self)))

        
    def destroy(self):
        """If overridden, this method should be called by the subclass
        implementation.
        """

        self.overlay     = None
        self.display     = None
        self.overlayList = None
        self.displayCtx  = None


    def getReferenceImage(self):
        """Some non-volumetric overlay types (e.g. the :class:`.Model` - see
        :class:`.ModelOpts`) may have a 'reference' :class:`.Image` instance
        associated with them, allowing the overlay to be localised in the
        coordinate space defined by the :class:`.Image`. The
        :class:`.DisplayOpts` class which corresponds to such non-volumetric
        overlays should override this method to return the reference image.

        :class:`.DisplayOpts` subclasses which are associated with volumetric
        overlays (i.e. :class:`.Image` instances) do not need to override
        this method.
        """

        if isinstance(self.overlay, fslimage.Image):
            return self.overlay
        return None

    
    def transformDisplayLocation(self, coords):
        """This method may be called after the overlay :attr:`bounds` have
        changed.

        If the bounds were changed as a result of a change to the spatial
        representation of the overlay (e.g. the :attr:`.ImageOpts.transform`
        property for :class:`.Image` overlays), this method should return
        a copy of the given coordinates which has been transformed into the
        new space.

        If the bounds were changed for some other reason, this method can
        just return the ``coords`` unchanged.
        """
        return coords


class Display(props.SyncableHasProperties):
    """
    """

    
    name = props.String()
    """The overlay name. """


    overlayType = props.Choice()
    """This property defines the overlay type - how the data is to be
    displayed.

    The options for this property are populated in the :meth:`__init__`
    method. See the :attr:`OVERLAY_TYPES` dictionary.
    """
    
    enabled = props.Boolean(default=True)
    """Should this overlay be displayed at all?"""

    
    alpha = props.Percentage(default=100.0)
    """Opacity - 100% is fully opaque, and 0% is fully transparent."""

    
    brightness = props.Percentage()

    
    contrast   = props.Percentage()


    softwareMode = props.Boolean(default=False)
    """If possible, optimise for software-based rendering."""

    
    def getOverlay(self):
        return self.__overlay


    def __init__(self,
                 overlay,
                 overlayList,
                 displayCtx,
                 parent=None,
                 overlayType=None):
        """Create a :class:`Display` for the specified overlay.

        :arg overlay:     The overlay object.

        :arg overlayList: The :class:`.OverlayList` instance which contains
                          all overlays.

        :arg displayCtx:  A :class:`.DisplayContext` instance describing how
                          the overlays are to be displayed.

        :arg parent:      A parent ``Display`` instance - see
                          :mod:`props.syncable`.

        :arg overlayType: Initial overlay type.
        """
        
        self.__overlay     = overlay
        self.__overlayList = overlayList
        self.__displayCtx  = displayCtx
        self.name          = overlay.name

        # Populate the possible choices
        # for the overlayType property
        overlayTypeProp = self.getProp('overlayType')
        possibleTypes   = list(OVERLAY_TYPES[overlay])

        # Special cases:
        #
        # If the overlay is an image which
        # does not have a fourth dimension
        # of length three, it can't be
        # a vector
        if isinstance(overlay, fslimage.Image) and \
           (len(overlay.shape) != 4 or overlay.shape[-1] != 3):
            possibleTypes.remove('rgbvector')
            possibleTypes.remove('linevector')
            
        for pt in possibleTypes:
            log.debug('Enabling overlay type {} for {}'.format(pt, overlay))
            label = strings.choices[self, 'overlayType', pt]
            overlayTypeProp.addChoice(pt, label, self)

        if overlayType is not None:
            self.overlayType = overlayType

        # Call the super constructor after our own
        # initialisation, in case the provided parent
        # has different property values to our own,
        # and our values need to be updated
        props.SyncableHasProperties.__init__(
            self,
            parent,
            
            # These properties cannot be unbound, as
            # they affect the OpenGL representation
            nounbind=['softwareMode', 'overlayType'])

        # Set up listeners after caling Syncable.__init__,
        # so the callbacks don't get called during
        # synchronisation
        self.addListener(
            'overlayType',
            'Display_{}'.format(id(self)),
            self.__overlayTypeChanged)
        
        # The __overlayTypeChanged method creates
        # a new DisplayOpts instance - for this,
        # it needs to be able to access this
        # Display instance's parent (so it can
        # subsequently access a parent for the
        # new DisplayOpts instance). Therefore,
        # we do this after calling
        # Syncable.__init__.
        self.__displayOpts = None
        self.__overlayTypeChanged()

        log.memory('{}.init ({})'.format(type(self).__name__, id(self)))

        
    def __del__(self):
        log.memory('{}.del ({})'.format(type(self).__name__, id(self)))
        

    def destroy(self):
        """This method should be called when this ``Display`` instance
        is no longer needed.
        """
        
        if self.__displayOpts is not None:
            self.__displayOpts.destroy()

        self.removeListener('overlayType', 'Display_{}'.format(id(self)))

        self.detachFromParent()
        
        self.__displayOpts = None
        self.__overlay     = None
        
        
    def getDisplayOpts(self):
        """
        """

        if (self.__displayOpts             is None) or \
           (self.__displayOpts.overlayType != self.overlayType):

            if self.__displayOpts is not None:
                self.__displayOpts.destroy()
            
            self.__displayOpts = self.__makeDisplayOpts()
            
        return self.__displayOpts


    def __makeDisplayOpts(self):
        """
        """

        if self.getParent() is None:
            oParent = None
        else:
            oParent = self.getParent().getDisplayOpts()

        optType = DISPLAY_OPTS_MAP[self.overlayType]
        
        log.debug('Creating {} instance for overlay {} ({})'.format(
            optType.__name__, self.__overlay, self.overlayType))
        
        return optType(self.__overlay,
                       self,
                       self.__overlayList,
                       self.__displayCtx,
                       oParent)

    
    def __overlayTypeChanged(self, *a):
        """
        """

        # make sure that the display
        # options instance is up to date
        self.getDisplayOpts()


import volumeopts
import vectoropts
import maskopts
import labelopts
import modelopts


OVERLAY_TYPES = td.TypeDict({

    'Image' : ['volume', 'mask', 'rgbvector', 'linevector', 'label'],
    'Model' : ['model']
})
"""This dictionary provides a mapping between the overlay classes, and
the way in which they may be represented.

For each overlay class, the first entry in the corresponding overlay type
list is used as the default overlay type.
"""


DISPLAY_OPTS_MAP = {
    'volume'     : volumeopts.VolumeOpts,
    'rgbvector'  : vectoropts.RGBVectorOpts,
    'linevector' : vectoropts.LineVectorOpts,
    'mask'       : maskopts.  MaskOpts,
    'model'      : modelopts. ModelOpts,
    'label'      : labelopts. LabelOpts,
}
"""This dictionary provides a mapping between each overlay type, and
the :class:`DisplayOpts` subclass which contains overlay type-specific
display options.
"""
