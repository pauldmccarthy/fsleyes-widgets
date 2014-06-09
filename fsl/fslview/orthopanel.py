#!/usr/bin/env python
#
# orthopanel.py - A wx/OpenGL widget for displaying and interacting with a
# collection of 3D images. Displays three canvases, each of which shows the
# same image(s) on a different orthogonal plane.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import fsl.props               as props
import fsl.data.fslimage       as fslimage
import fsl.fslview.slicecanvas as slicecanvas


class OrthoPanel(wx.Panel, props.HasProperties):

    # Properties which toggle display of each of
    # the three canvases, and the cursors on them.
    showXCanvas = props.Boolean(default=True)
    showYCanvas = props.Boolean(default=True)
    showZCanvas = props.Boolean(default=True)
    showCursor  = props.Boolean(default=True)

    # Properties which set the current displayed
    # position (in real world coordinates)
    xpos  = props.Double(clamped=True)
    ypos  = props.Double(clamped=True)
    zpos  = props.Double(clamped=True)

    # Properties which set the current zoom
    # factor on each of the canvases
    xzoom = props.Double(minval=1.0,
                         maxval=10.0, 
                         default=1.0,
                         clamped=True)
    yzoom = props.Double(minval=1.0,
                         maxval=10.0, 
                         default=1.0,
                         clamped=True)
    zzoom = props.Double(minval=1.0,
                         maxval=10.0, 
                         default=1.0,
                         clamped=True)

    _view = props.HGroup((
        props.VGroup(('showCursor',
                      'showXCanvas',
                      'showYCanvas',
                      'showZCanvas')),
        props.VGroup(('xpos',  'ypos',  'zpos')),
        props.VGroup(('xzoom', 'yzoom', 'zzoom'))
    ))

    _labels = {
        'showCursor'  : 'Show cursor',
        'showXCanvas' : 'Show X canvas',
        'showYCanvas' : 'Show Y canvas',
        'showZCanvas' : 'Show Z canvas',
        'xzoom'       : 'X zoom',
        'yzoom'       : 'Y zoom',
        'zzoom'       : 'Z zoom',
        'xpos'        : 'X position',
        'ypos'        : 'Y position',
        'zpos'        : 'Z position'
    }


    def __init__(self, parent, imageList, glContext=None):
        """
        Creates three SliceCanvas objects, each displaying the images
        in the given image list along a different axis. 
        """

        if not isinstance(imageList, fslimage.ImageList):
            raise TypeError(
                'imageList must be a fsl.data.fslimage.ImageList instance')

        self.imageList = imageList
        self.name      = 'OrthoPanel_{}'.format(id(self))

        wx.Panel.__init__(self, parent)

        self.SetMinSize((600, 200))

        self.xcanvas = slicecanvas.SliceCanvas(self, imageList, zax=0,
                                               glContext=glContext)

        if glContext is None:
            glContext = self.xcanvas.glContext
        
        self.ycanvas = slicecanvas.SliceCanvas(self, imageList, zax=1,
                                               glContext=glContext)
        self.zcanvas = slicecanvas.SliceCanvas(self, imageList, zax=2,
                                               glContext=glContext)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self.sizer.Add(self.xcanvas, flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.ycanvas, flag=wx.EXPAND, proportion=1)
        self.sizer.Add(self.zcanvas, flag=wx.EXPAND, proportion=1)

        self.Layout()

        self.xcanvas.Bind(wx.EVT_LEFT_DOWN, self._onMouseEvent)
        self.ycanvas.Bind(wx.EVT_LEFT_DOWN, self._onMouseEvent)
        self.zcanvas.Bind(wx.EVT_LEFT_DOWN, self._onMouseEvent)
        self.xcanvas.Bind(wx.EVT_MOTION,    self._onMouseEvent)
        self.ycanvas.Bind(wx.EVT_MOTION,    self._onMouseEvent)
        self.zcanvas.Bind(wx.EVT_MOTION,    self._onMouseEvent)

        bounds = imageList.bounds

        self.xpos = bounds.xmin + bounds.xlen / 2.0
        self.ypos = bounds.ymin + bounds.ylen / 2.0
        self.zpos = bounds.zmin + bounds.zlen / 2.0
        
        self.imageList.addListener(
            'bounds',
            self.name,
            self._updateImageBounds)
        self._updateImageBounds()

        self._configPosListeners()
        self._configShowListeners()
        self._configZoomListeners()


    def _configPosListeners(self):
        """
        Configures listeners on the xpos/ypos/zpos properties - when they
        are changed, the displayed position is changed.
        """

        def moveX(value, *a):
            self.setPosition(value, self.ypos, self.zpos) 
        def moveY(value, *a):
            self.setPosition(self.xpos, value, self.zpos) 
        def moveZ(value, *a):
            self.setPosition(self.xpos, self.ypos, value) 

        self.addListener('xpos', self.name, moveX)
        self.addListener('ypos', self.name, moveY)
        self.addListener('zpos', self.name, moveZ)


    def _configShowListeners(self):
        """
        Configures listeners on the show* properties, so they can
        be used to toggle visibility of various things.
        """
        def showCursor(ctx, value, valid):
            self.xcanvas.showCursor = value
            self.ycanvas.showCursor = value
            self.zcanvas.showCursor = value

        def showXCanvas(value, *a):
            self.sizer.Show(self.xcanvas, value)
            self.Layout()
        def showYCanvas(value, *a):
            self.sizer.Show(self.ycanvas, value)
            self.Layout()
        def showZCanvas(value, *a):
            self.sizer.Show(self.zcanvas, value)
            self.Layout() 

        self.addListener('showCursor',  self.name, showCursor)
        self.addListener('showXCanvas', self.name, showXCanvas)
        self.addListener('showYCanvas', self.name, showYCanvas)
        self.addListener('showZCanvas', self.name, showZCanvas)

            
    def _configZoomListeners(self):
        """
        Configures listeners on the x/y/zzoom properties so when
        they are changed, the zoom factor on the corresponding canvas
        is changed.
        """

        def zoom(canvas, xax, yax, value):
            value      = 1.0 / value
            bounds     = self.imageList.bounds
            dispBounds = canvas.displayBounds
            
            xlen = value * bounds.getlen(xax)
            ylen = value * bounds.getlen(yax)

            if value == 1:
                xcentre = bounds.getmin(xax) + 0.5 * xlen
                ycentre = bounds.getmin(yax) + 0.5 * ylen
            else:
                xcentre = dispBounds.xmin + dispBounds.xlen / 2.0
                ycentre = dispBounds.ymin + dispBounds.ylen / 2.0

            dispBounds.all = [xcentre - 0.5 * xlen,
                              xcentre + 0.5 * xlen,
                              ycentre - 0.5 * ylen,
                              ycentre + 0.5 * ylen]

        def xzoom(value, *a): zoom(self.xcanvas, 1, 2, value)
        def yzoom(value, *a): zoom(self.ycanvas, 0, 2, value)
        def zzoom(value, *a): zoom(self.zcanvas, 0, 1, value)
            
        self.addListener('xzoom', self.name, xzoom)
        self.addListener('yzoom', self.name, yzoom)
        self.addListener('zzoom', self.name, zzoom)

        
    def _updateImageBounds(self, *a):
        """
        Called when the list of displayed images changes. Updates the
        minimum/maximum bounds on the x/y/zpos properties.
        """
        bounds = self.imageList.bounds

        self.setConstraint('xpos', 'minval', bounds.xmin)
        self.setConstraint('xpos', 'maxval', bounds.xmax)
        self.setConstraint('ypos', 'minval', bounds.ymin)
        self.setConstraint('ypos', 'maxval', bounds.ymax)
        self.setConstraint('zpos', 'minval', bounds.zmin)
        self.setConstraint('zpos', 'maxval', bounds.zmax)
        
        # reset the cursor and min/max values in
        # case the old values were out of bounds
        self.xpos = self.xpos
        self.ypos = self.ypos
        self.zpos = self.zpos


    def _shiftCanvas(self, canvas, newx, newy):
        """
        Called when the position has changed, and zooming is enabled on
        the given canvas. Updates the display bounds on the canvas so that
        the current position is within them.
        """
        dispBounds = canvas.displayBounds

        if newx >= dispBounds.xmin and \
           newx <= dispBounds.xmax and \
           newy >= dispBounds.ymin and \
           newy <= dispBounds.ymax:
            return

        xax = canvas.xax
        yax = canvas.yax

        xshift = 0
        yshift = 0

        imgxmin = self.imageList.bounds.getmin(xax)
        imgxmax = self.imageList.bounds.getmax(xax)
        imgymin = self.imageList.bounds.getmin(yax)
        imgymax = self.imageList.bounds.getmax(yax)

        if   newx < dispBounds.xmin: xshift = newx - dispBounds.xmin
        elif newx > dispBounds.xmax: xshift = newx - dispBounds.xmax
        if   newy < dispBounds.ymin: yshift = newy - dispBounds.ymin 
        elif newy > dispBounds.ymax: yshift = newy - dispBounds.ymax 
            
        newxmin = dispBounds.xmin + xshift 
        newxmax = dispBounds.xmax + xshift
        newymin = dispBounds.ymin + yshift 
        newymax = dispBounds.ymax + yshift 

        if newxmin < imgxmin:
            newxmin = imgxmin
            newxmax = imgxmin + dispBounds.xlen
        elif newxmax > imgxmax:
            newxmax = imgxmax
            newxmin = imgxmax - dispBounds.xlen
        
        if newymin < imgymin:
            newymin = imgymin
            newymax = imgymin + dispBounds.ylen
        elif newymax > imgymax:
            newymax = imgymax
            newymin = imgymax - dispBounds.ylen

        dispBounds.all = [newxmin, newxmax, newymin, newymax]

        
    def setPosition(self, xpos, ypos, zpos):
        """
        Sets the currently displayed x/y/z position (in real world
        coordinates).
        """

        self.xpos = xpos
        self.ypos = ypos
        self.zpos = zpos

        self.xcanvas.xpos = ypos
        self.xcanvas.ypos = zpos
        self.xcanvas.zpos = xpos

        self.ycanvas.xpos = xpos
        self.ycanvas.ypos = zpos
        self.ycanvas.zpos = ypos

        self.zcanvas.xpos = xpos
        self.zcanvas.ypos = ypos
        self.zcanvas.zpos = zpos 

        if self.xzoom != 1: self._shiftCanvas(self.xcanvas, ypos, zpos)
        if self.yzoom != 1: self._shiftCanvas(self.ycanvas, xpos, zpos)
        if self.zzoom != 1: self._shiftCanvas(self.zcanvas, xpos, ypos)


    def _onMouseEvent(self, ev):
        """
        Called on mouse movement and left clicks. The currently
        displayed slices and cursor positions on each of the
        canvases follow mouse clicks and drags.
        """

        if not ev.LeftIsDown():      return
        if len(self.imageList) == 0: return

        mx, my  = ev.GetPositionTuple()
        source  = ev.GetEventObject()
        w, h    = source.GetClientSize()

        my = h - my

        xpos = source.canvasToWorldX(mx)
        ypos = source.canvasToWorldY(my)

        if   source == self.xcanvas: self.setPosition(self.xpos, xpos, ypos)
        elif source == self.ycanvas: self.setPosition(xpos, self.ypos, ypos)
        elif source == self.zcanvas: self.setPosition(xpos, ypos, self.zpos)
 
            
class OrthoFrame(wx.Frame):
    """
    Convenience class for displaying an OrthoPanel in a standalone window.
    """

    def __init__(self, parent, imageList, title=None):
        
        wx.Frame.__init__(self, parent, title=title)
        self.panel = OrthoPanel(self, imageList)
        self.Layout()


class OrthoDialog(wx.Dialog):
    """
    Convenience class for displaying an OrthoPanel in a (possibly modal)
    dialog window.
    """

    def __init__(self, parent, imageList, title=None, style=None):

        if style is None: style =  wx.DEFAULT_DIALOG_STYLE
        else:             style |= wx.DEFAULT_DIALOG_STYLE
        
        wx.Dialog.__init__(self, parent, title=title, style=style)
        self.panel = OrthoPanel(self, imageList)
        self.Layout()
