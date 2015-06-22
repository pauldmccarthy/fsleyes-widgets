#!/usr/bin/env python
#
# wxglslicecanvas.py - A SliceCanvas which is rendered using a
# wx.glcanvas.GLCanvas panel.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :class:`WXGLSliceCanvas` class is both a :class:`.SliceCanvas` and a
:class:`wx.glcanvas.GLCanvas` panel.

It is the main class used for on-screen orthographic rendering of 3D image
data (although most of the functionality is provided by the
:class:`.SliceCanvas` class).
"""

import logging

import wx
import wx.glcanvas              as wxgl

import slicecanvas              as slicecanvas
import fsl.fslview.gl.resources as glresources
import fsl.fslview.gl           as fslgl


log = logging.getLogger(__name__)


class WXGLSliceCanvas(slicecanvas.SliceCanvas,
                      wxgl.GLCanvas,
                      fslgl.WXGLCanvasTarget):
    """A :class:`wx.glcanvas.GLCanvas` and a :class:`.SliceCanvas`, for 
    on-screen interactive 2D slice rendering from a collection of 3D
    overlays.
    """

    def __init__(self, parent, overlayList, displayCtx, zax=0):
        """Configures a few event handlers for cleaning up property
        listeners when the canvas is destroyed, and for redrawing on
        paint/resize events.
        """

        wxgl.GLCanvas          .__init__(self, parent)
        slicecanvas.SliceCanvas.__init__(self, overlayList, displayCtx, zax)
        fslgl.WXGLCanvasTarget .__init__(self)
        
        # the image list is probably going to outlive
        # this SliceCanvas object, so we do the right
        # thing and remove our listeners when we die
        def onDestroy(ev):
            ev.Skip()

            if ev.GetEventObject() is not self:
                return

            self.removeListener('zax',           self.name)
            self.removeListener('pos',           self.name)
            self.removeListener('displayBounds', self.name)
            self.removeListener('showCursor',    self.name)
            self.removeListener('invertX',       self.name)
            self.removeListener('invertY',       self.name)
            self.removeListener('zoom',          self.name)
            self.removeListener('renderMode',    self.name)
            
            self.overlayList.removeListener('overlays',     self.name)
            self.displayCtx .removeListener('bounds',       self.name)
            self.displayCtx .removeListener('overlayOrder', self.name)
            
            for overlay in self.overlayList:
                disp  = self.displayCtx.getDisplay(overlay)
                globj = self._glObjects[overlay]
                    
                disp.removeListener('overlayType',  self.name)
                disp.removeListener('enabled',      self.name)
                disp.removeListener('softwareMode', self.name)

                globj.destroy()

                rt, rtName = self._prerenderTextures.get(overlay, (None, None))
                ot         = self._offscreenTextures.get(overlay, None)

                if rt is not None: glresources.delete(rtName)
                if ot is not None: ot   .destroy()

        self.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)

        # When the canvas is resized, we have to update
        # the display bounds to preserve the aspect ratio
        def onResize(ev):
            self._updateDisplayBounds()
            ev.Skip()
        self.Bind(wx.EVT_SIZE, onResize)
