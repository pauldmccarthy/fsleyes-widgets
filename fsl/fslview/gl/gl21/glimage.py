#!/usr/bin/env python

# glimage.py - A class which encapsulates the data required to render
#              a 2D slice of a 3D image in an OpenGL 2.1 compatible
#              manner.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""A GLImage object encapsulates the OpenGL information necessary
to render 2D slices of a 3D image, in an OpenGL 2.1 compatible manner.

This class makes use of the functions in the :mod:`fsl.fslview.gl.glimage`
module, which actually generates the vertex and texture information necessary
to render an image.

The image data itself is stored as a 3D texture. Data for signed or unsigned
8, 16, or 32 bit integer images is stored on the GPU in the same format; all
other data types are stored as 32 bit floating point.

This implementation is dependent upon one OpenGL ARB extension - `texture_rg`,
which allows us to store and retrieve un-clamped floating point values in the
3D image texture.
"""

import logging
log = logging.getLogger(__name__)

import numpy as np

import OpenGL.GL         as gl
import OpenGL.arrays.vbo as vbo

# This extension provides some texture data format identifiers
# which are standard in more modern OpenGL versions.
import OpenGL.GL.ARB.texture_rg as arbrg

import fsl.fslview.gl.glimage as glimage


class GLImage(object):

    def __init__(self, image, xax, yax, imageDisplay):
        """Initialise the OpenGL data required to render the given image.

        After initialisation, all of the data requirted to render a slice
        is available as attributes of this object:

          - :attr:`imageTexture:`  An OpenGL texture handle to a 3D texture
                                   containing the image data.

          - :attr:`colourTexture`: An OpenGL texture handle to a 1D texture
                                   containing the colour map used to colour
                                   the image data.
        
          - :attr:`worldCoords`:   A `(3,4*N)` numpy array (where `N` is the
                                   number of pixels to be drawn). See the
                                   :func:`fsl.fslview.gl.glimage.genVertexData`
                                   function.

          - :attr:`texCoords`:     A `(3,N)` numpy array (where `N` is the
                                   number of pixels to be drawn). See the
                                   :func:`fsl.fslview.gl.glimage.genVertexData`
                                   function.

        As part of initialisation, this object registers itself as a listener
        on several properties of the given
        :class:`~fsl.fslview.displaycontext.ImageDisplay` object so that, when
        any display properties change, the image data, colour texture, and
        vertex data are automatically updated.
        
        :arg image:        A :class:`~fsl.data.image.Image` object.
        
        :arg xax:          The image world axis which corresponds to the
                           horizontal screen axis.

        :arg xax:          The image world axis which corresponds to the
                           vertical screen axis.        
        
        :arg imageDisplay: A :class:`~fsl.fslview.displaycontext.ImageDisplay`
                           object which describes how the image is to be
                           displayed. 
        """
        
        self.image   = image
        self.display = imageDisplay

        # Initialise the image texture, and
        # generate vertex/texture coordinates
        self.imageTexture = self.genImageData()
        self.genVertexData(xax, yax)

        # The colour texture, containing a map of
        # colours (stored on the GPU as a 1D texture)
        # This is initialised in the updateColourBuffer
        # method
        self.colourTexture = gl.glGenTextures(1) 
        self.genColourTexture()

        # Add listeners to this image so the view can be
        # updated when its display properties are changed
        self._configDisplayListeners()


    def genVertexData(self, xax, yax):
        """Generates vertex and texture coordinates required to render
        the image. See :func:`fsl.fslview.gl.glimage.genVertexData`.
        """ 
        self.xax = xax
        self.yax = yax

        worldCoords, texCoords = glimage.genVertexData(
            self.image, self.display, xax, yax)

        worldCoords = worldCoords[:, [xax, yax]]
        texCoords   = texCoords[  :, [xax, yax]]

        worldCoordBuffer = vbo.VBO(worldCoords.ravel('C'), gl.GL_STATIC_DRAW)
        texCoordBuffer   = vbo.VBO(texCoords  .ravel('C'), gl.GL_STATIC_DRAW)

        self.worldCoords = worldCoordBuffer
        self.texCoords   = texCoordBuffer
        self.nVertices   = worldCoords.shape[0]

        
    def _checkDataType(self):
        """This method determines the appropriate OpenGL texture data
        format to use for the image managed by this :class`GLImage`
        object. 
        """

        dtype = self.image.data.dtype

        if   dtype == np.uint8:  self.texExtFmt = gl.GL_UNSIGNED_BYTE
        elif dtype == np.int8:   self.texExtFmt = gl.GL_UNSIGNED_BYTE
        elif dtype == np.uint16: self.texExtFmt = gl.GL_UNSIGNED_SHORT
        elif dtype == np.int16:  self.texExtFmt = gl.GL_UNSIGNED_SHORT
        elif dtype == np.uint32: self.texExtFmt = gl.GL_UNSIGNED_INT
        elif dtype == np.int32:  self.texExtFmt = gl.GL_UNSIGNED_INT
        else:                    self.texExtFmt = gl.GL_FLOAT

        if   dtype == np.uint8:  self.texIntFmt = gl.GL_INTENSITY
        elif dtype == np.int8:   self.texIntFmt = gl.GL_INTENSITY
        elif dtype == np.uint16: self.texIntFmt = gl.GL_INTENSITY
        elif dtype == np.int16:  self.texIntFmt = gl.GL_INTENSITY
        elif dtype == np.uint32: self.texIntFmt = gl.GL_INTENSITY
        elif dtype == np.int32:  self.texIntFmt = gl.GL_INTENSITY
        else:                    self.texIntFmt = arbrg.GL_R32F

        if   dtype == np.int8:   self.signed = True
        elif dtype == np.int16:  self.signed = True
        elif dtype == np.int32:  self.signed = True
        else:                    self.signed = False

        if   dtype == np.uint8:  normFactor = 255.0
        elif dtype == np.int8:   normFactor = 255.0
        elif dtype == np.uint16: normFactor = 65535.0
        elif dtype == np.int16:  normFactor = 65535.0
        elif dtype == np.uint32: normFactor = 4294967295.0
        elif dtype == np.int32:  normFactor = 4294967295.0
        else:                    normFactor = 1.0

        if   dtype == np.int8:   normOffset = 128.0
        elif dtype == np.int16:  normOffset = 32768.0
        elif dtype == np.int32:  normOffset = 2147483648.0
        else:                    normOffset = 0.0

        xform = np.identity(4)
        xform[0, 0] =  normFactor
        xform[0, 3] = -normOffset

        self.dataTypeXform = xform.transpose()

        log.debug('Image {} (data type {}) is to be '
                  'stored as a 3D texture with '
                  'internal format {}, external format {}, '
                  'norm factor {}, norm offset {}'.format(
                      self.image.name,
                      dtype,
                      self.texIntFmt,
                      self.texExtFmt,
                      normFactor,
                      normOffset))

        
    def genImageData(self):
        """Generates the OpenGL image texture used to store the data for the
        given image. The texture handle is stored as an attribute of the image
        and, if it has already been created (e.g. by another :class:`GLImage`
        object which is managing the same image), the existing texture handle
        is returned.
        """

        # figure out how to store
        # the image as a 3D texture.
        self._checkDataType()

        image   = self.image
        display = self.display
        volume  = display.volume

        if display.interpolation: interp = gl.GL_LINEAR
        else:                     interp = gl.GL_NEAREST

        # we only store a single 3D image
        # in GPU memory at any one time
        if len(image.shape) > 3: imageData = image.data[:, :, :, volume]
        else:                    imageData = image.data

        # Check to see if the image texture
        # has already been created
        try:
            displayHash, imageTexture = image.getAttribute('glImageTexture')
        except:
            displayHash  = None
            imageTexture = None

        # otherwise, create a new one
        if imageTexture is None:
            imageTexture = gl.glGenTextures(1)

        # The image buffer already exists, and it
        # contains the data for the requested volume.  
        elif displayHash == hash(display):
            return imageTexture

        log.debug('Creating 3D texture for '
                  'image {} (data shape: {})'.format(
                      image.name,
                      imageData.shape))

        # The image data is flattened, with fortran dimension
        # ordering, so the data, as stored on the GPU, has its
        # first dimension as the fastest changing.
        imageData = imageData.ravel(order='F')

        # Enable storage of tightly packed data of any size (i.e.
        # our texture shape does not have to be divisible by 4).
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT,   1)
        
        # Set up image texture sampling thingos
        # with appropriate interpolation method
        gl.glBindTexture(gl.GL_TEXTURE_3D, imageTexture)
        gl.glTexParameteri(gl.GL_TEXTURE_3D,
                           gl.GL_TEXTURE_MAG_FILTER,
                           interp)
        gl.glTexParameteri(gl.GL_TEXTURE_3D,
                           gl.GL_TEXTURE_MIN_FILTER,
                           interp)
        gl.glTexParameteri(gl.GL_TEXTURE_3D,
                           gl.GL_TEXTURE_WRAP_S,
                           gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_3D,
                           gl.GL_TEXTURE_WRAP_T,
                           gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_3D,
                           gl.GL_TEXTURE_WRAP_R,
                           gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameterfv(gl.GL_TEXTURE_3D,
                            gl.GL_TEXTURE_BORDER_COLOR,
                            [0, 0, 0, 0])

        # create the texture according to the format
        # calculated by the checkDataType method.
        gl.glTexImage3D(gl.GL_TEXTURE_3D,
                        0,
                        self.texIntFmt,
                        image.shape[0], image.shape[1], image.shape[2],
                        0,
                        gl.GL_RED,
                        self.texExtFmt,
                        imageData)

        # Add the ImageDisplay hash, and a reference to the
        # texture as an attribute of the image, so other
        # things which want to render the same volume of the
        # image don't need to duplicate all of that data.
        image.setAttribute('glImageTexture', (hash(display), imageTexture))

        return imageTexture

        
    def genColourTexture(self):
        """Generates the colour texture used to colour image voxels. See
        :func:`fsl.fslview.gl.glimage.genVertexData`.
        """ 

        # OpenGL does different things to 3D texture data
        # depending on its type - integer types are
        # normalised from [0, INT_MAX] to [0, 1], whereas
        # floating point types are left un-normalised
        # (because we are using the ARB.texture_rg.GL_R32F
        # data format - without this, floating point data
        # is *clamped*, not normalised, to the range
        # [0, 1]!). The checkDataType method calculates
        # an appropriate transformation matrix to transform
        # the image data to the appropriate texture coordinate
        # range.
        texCoordXform = glimage.genColourTexture(self.image,
                                                 self.display,
                                                 self.colourTexture,
                                                 xform=self.dataTypeXform)
        self.texCoordXform = texCoordXform


    def _configDisplayListeners(self):
        """Adds a bunch of listeners to the
        :class:`~fsl.fslview.displaycontext.ImageDisplay` object which defines
        how the given image is to be displayed.

        This is done so we can update the colour, vertex, and image data when
        display properties are changed.
        """ 

        def vertexUpdate(*a):
            self.genVertexData(self.xax, self.yax)

        def imageUpdate(*a):
            self.genImageData()
        
        def colourUpdate(*a):
            self.genColourTexture()

        display = self.display
        lnrName = 'GlImage_{}'.format(id(self))

        display.addListener('transform',       lnrName, vertexUpdate)
        display.addListener('interpolation',   lnrName, imageUpdate)
        display.addListener('alpha',           lnrName, colourUpdate)
        display.addListener('displayRange',    lnrName, colourUpdate)
        display.addListener('clipLow',         lnrName, colourUpdate)
        display.addListener('clipHigh',        lnrName, colourUpdate)
        display.addListener('cmap',            lnrName, colourUpdate)
        display.addListener('voxelResolution', lnrName, vertexUpdate)
        display.addListener('worldResolution', lnrName, vertexUpdate)
        display.addListener('volume',          lnrName, imageUpdate)
