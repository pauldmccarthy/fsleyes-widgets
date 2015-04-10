#!/usr/bin/env python
#
# glvolume_funcs.py - Functions used by the fsl.fslview.gl.glvolume.GLVolume
#                     class to render 3D images in an OpenGL 1.4 compatible
#                     manner.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Provides functions which are used by the
:class:`~fsl.fslview.gl.glvolume.GLVolume` class to render 3D images in an
OpenGL 1.4 compatible manner.

This module depends upon two OpenGL ARB extensions, ARB_vertex_program and
ARB_fragment_program which, being ancient (2002) technology, should be
available on pretty much any graphics card in the wild today.

See the :mod:`.gl21.glvolume_funcs` module for more details.

This PDF is quite useful:
 - http://www.renderguild.com/gpuguide.pdf
"""

import logging

import numpy                          as np
import OpenGL.GL                      as gl
import OpenGL.raw.GL._types           as gltypes
import OpenGL.GL.ARB.fragment_program as arbfp
import OpenGL.GL.ARB.vertex_program   as arbvp

import fsl.utils.transform     as transform
import fsl.fslview.gl.globject as globject
import fsl.fslview.gl.shaders  as shaders


log = logging.getLogger(__name__)


def compileShaders(self):

    if self.vertexProgram is not None:
        arbvp.glDeleteProgramsARB(1, gltypes.GLuint(self.vertexProgram))
        
    if self.fragmentProgram is not None:
        arbfp.glDeleteProgramsARB(1, gltypes.GLuint(self.fragmentProgram)) 

    vertShaderSrc = shaders.getVertexShader(  self, fast=self.display.fastMode)
    fragShaderSrc = shaders.getFragmentShader(self, fast=self.display.fastMode)

    vertexProgram, fragmentProgram = shaders.compilePrograms(
        vertShaderSrc, fragShaderSrc)

    self.vertexProgram   = vertexProgram
    self.fragmentProgram = fragmentProgram    


def init(self):
    """Compiles the vertex and fragment programs used for rendering."""

    self.vertexProgram   = None
    self.fragmentProgram = None
    
    compileShaders(   self)
    updateShaderState(self)

    
def destroy(self):
    """Deletes handles to the vertex/fragment programs."""

    arbvp.glDeleteProgramsARB(1, gltypes.GLuint(self.vertexProgram))
    arbfp.glDeleteProgramsARB(1, gltypes.GLuint(self.fragmentProgram))


def updateShaderState(self):
    opts = self.displayOpts

    # enable the vertex and fragment programs
    gl.glEnable(arbvp.GL_VERTEX_PROGRAM_ARB) 
    gl.glEnable(arbfp.GL_FRAGMENT_PROGRAM_ARB)

    arbvp.glBindProgramARB(arbvp.GL_VERTEX_PROGRAM_ARB,
                           self.vertexProgram)
    arbfp.glBindProgramARB(arbfp.GL_FRAGMENT_PROGRAM_ARB,
                           self.fragmentProgram)

    # The voxValXform transformation turns
    # an image texture value into a raw
    # voxel value. The colourMapXform
    # transformation turns a raw voxel value
    # into a value between 0 and 1, suitable
    # for looking up an appropriate colour
    # in the 1D colour map texture
    voxValXform = transform.concat(self.imageTexture.voxValXform,
                                   self.colourTexture.getCoordinateTransform())
    
    # The fragment program needs to know the image shape
    shape = list(self.image.shape[:3])

    # And the clipping range, normalised
    # to the image texture value range
    clipLo = opts.clippingRange[0]             * \
        self.imageTexture.invVoxValXform[0, 0] + \
        self.imageTexture.invVoxValXform[3, 0]
    clipHi = opts.clippingRange[1]             * \
        self.imageTexture.invVoxValXform[0, 0] + \
        self.imageTexture.invVoxValXform[3, 0]
    
    shaders.setFragmentProgramMatrix(0, voxValXform)
    shaders.setFragmentProgramVector(4, shape + [0])
    shaders.setFragmentProgramVector(5, [clipLo, clipHi, 0, 0])

    gl.glDisable(arbvp.GL_VERTEX_PROGRAM_ARB) 
    gl.glDisable(arbfp.GL_FRAGMENT_PROGRAM_ARB) 


def preDraw(self):
    """Prepares to draw a slice from the given
    :class:`~fsl.fslview.gl.glvolume.GLVolume` instance.
    """


    # enable drawing from a vertex array
    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

    gl.glClientActiveTexture(gl.GL_TEXTURE0)
    gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

    gl.glClientActiveTexture(gl.GL_TEXTURE1)
    gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY) 

    # enable the vertex and fragment programs
    gl.glEnable(arbvp.GL_VERTEX_PROGRAM_ARB) 
    gl.glEnable(arbfp.GL_FRAGMENT_PROGRAM_ARB)

    arbvp.glBindProgramARB(arbvp.GL_VERTEX_PROGRAM_ARB,
                           self.vertexProgram)
    arbfp.glBindProgramARB(arbfp.GL_FRAGMENT_PROGRAM_ARB,
                           self.fragmentProgram)


def draw(self, zpos, xform=None):
    """Draws a slice of the image at the given Z location. """

    vertices, _ = globject.slice2D(
        self.image.shape[:3],
        self.xax,
        self.yax,
        self.display.getTransform('voxel', 'display'))

    vertices[:, self.zax] = zpos
    
    voxCoords = transform.transform(
        vertices,
        self.display.getTransform('display', 'voxel'))

    if xform is not None: 
        vertices = transform.transform(vertices, xform)

    texCoords = voxCoords / self.image.shape[:3]

    # Vox coords are texture 0 coords
    # Tex coords are texture 1 coords
    vertices  = np.array(vertices,  dtype=np.float32).ravel('C')
    voxCoords = np.array(voxCoords, dtype=np.float32).ravel('C')
    texCoords = np.array(texCoords, dtype=np.float32).ravel('C')

    gl.glClientActiveTexture(gl.GL_TEXTURE0)
    gl.glTexCoordPointer(3, gl.GL_FLOAT, 0, voxCoords)
    
    gl.glClientActiveTexture(gl.GL_TEXTURE1)
    gl.glTexCoordPointer(3, gl.GL_FLOAT, 0, texCoords)
    
    gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)

    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

    
def drawAll(self, zposes, xforms):
    """Draws mutltiple slices of the given image at the given Z position,
    applying the corresponding transformation to each of the slices.
    """

    # Don't use a custom world-to-world
    # transformation matrix.
    shaders.setVertexProgramMatrix(4, np.eye(4))
    
    # Instead, tell the vertex
    # program to use texture coordinates
    shaders.setFragmentProgramVector(8, -np.ones(4))

    # worldCoords = np.array(self.worldCoords)
    # indices     = np.array(self.indices)

    # Replicate the world coordinates
    # across all z positions, and with
    # each corresponding transformation
    worldCoords, texCoords, indices = globject.broadcast(
        self.worldCoords, self.indices, zposes, xforms, self.zax)

    worldCoords = worldCoords.ravel('C')
    texCoords   = texCoords  .ravel('C')

    # Draw all of the slices with 
    # these four function calls.
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glTexCoordPointer(3, gl.GL_FLOAT, 0, texCoords)
    gl.glVertexPointer(  3, gl.GL_FLOAT, 0, worldCoords)
    gl.glDrawElements(gl.GL_TRIANGLES,
                      len(indices),
                      gl.GL_UNSIGNED_INT,
                      indices)


def postDraw(self):
    """Cleans up the GL state after drawing from the given
    :class:`~fsl.fslview.gl.glvolume.GLVolume` instance.
    """

    gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    gl.glClientActiveTexture(gl.GL_TEXTURE0)
    gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    
    gl.glClientActiveTexture(gl.GL_TEXTURE1)
    gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY) 

    gl.glDisable(arbfp.GL_FRAGMENT_PROGRAM_ARB)
    gl.glDisable(arbvp.GL_VERTEX_PROGRAM_ARB)
