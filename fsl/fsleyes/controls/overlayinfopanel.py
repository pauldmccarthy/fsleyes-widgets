#!/usr/bin/env python
#
# overlayinfopanel.py - The OverlayInfoPanel class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the ``OverlayInfoPanel`` class, a *FSLeyes control*
panel which displays information about the currently selected overlay.
"""


import collections

import wx
import wx.html as wxhtml

import fsl.data.strings   as strings
import fsl.data.constants as constants
import fsl.fsleyes.panel  as fslpanel


class OverlayInfoPanel(fslpanel.FSLEyesPanel):
    """An ``OverlayInfoPanel`` is a :class:`.FSLEyesPanel` which displays
    information about the currently selected overlay in a
    ``wx.html.HtmlWindow``. The currently selected overlay is defined by the
    :attr:`.DisplayContext.selectedOverlay` property. An ``OverlayInfoPanel``
    looks something like the following:

    .. image:: images/overlayinfopanel.png
       :scale: 50%
       :align: center

    Slightly different information is shown depending on the overlay type,
    and is generated by the following methods:

    ====================== =============================
    :class:`.Image`        :meth:`__getImageInfo`
    :class:`.FEATImage`    :meth:`__getFEATImageInfo`
    :class:`.MelodicImage` :meth:`__getMelodicImageInfo`
    :class:`.Model`        :meth:`__getModelInfo`
    ====================== =============================
    """


    def __init__(self, parent, overlayList, displayCtx):
        """Create an ``OverlayInfoPanel``.

        :arg parent:      The :mod:`wx` parent object.
        :arg overlayList: The :class:`.OverlayList` instance.
        :arg displayCtx:  The :class:`.DisplayContext` instance.
        """

        fslpanel.FSLEyesPanel.__init__(self, parent, overlayList, displayCtx)

        self.__info  = wxhtml.HtmlWindow(self)
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer.Add(self.__info, flag=wx.EXPAND, proportion=1)

        self.__info.SetStandardFonts(self.GetFont().GetPointSize())
        
        self.SetSizer(self.__sizer)

        displayCtx .addListener('selectedOverlay',
                                self._name,
                                self.__selectedOverlayChanged)
        overlayList.addListener('overlays',
                                self._name,
                                self.__selectedOverlayChanged)

        self.__currentOverlay = None
        self.__currentDisplay = None
        self.__selectedOverlayChanged()

        self.SetMinSize((300, 200))
        self.Layout()

        
    def destroy(self):
        """Must be called when this ``OverlayInfoPanel`` is no longer
        needed. Removes some property listeners, and calls the
        :meth:`.FSLEyesPanel.destroy` method.
        """
        
        self._displayCtx .removeListener('selectedOverlay', self._name)
        self._overlayList.removeListener('overlays',        self._name)

        if self.__currentDisplay is not None:
            self.__currentDisplay.removeListener('name', self._name)

        self.__currentOverlay = None
        self.__currentDisplay = None

        fslpanel.FSLEyesPanel.destroy(self)


    def __selectedOverlayChanged(self, *a):
        """Called when the :class:`.OverlayList` or
        :attr:`.DisplayContext.selectedOverlay` changes. Refreshes the
        information shown on this ``OverlayInfoPanel``.
        """

        overlay = self._displayCtx.getSelectedOverlay()

        # Overlay list is empty
        if overlay is None:
            self.__info.SetPage('')
            self.__info.Refresh()
            return

        # Info for this overlay
        # is already being shown
        if overlay == self.__currentOverlay:
            return
        
        if self.__currentDisplay is not None:
            self.__currentDisplay.removeListener('name', self._name)
            
        self.__currenOverlay = None
        self.__currenDisplay = None
        
        if overlay is not None:
            self.__currentOverlay = overlay
            self.__currentDisplay = self._displayCtx.getDisplay(overlay)

            self.__currentDisplay.addListener('name',
                                              self._name,
                                              self.__overlayNameChanged)
        
        self.__updateInformation()

        
    def __overlayNameChanged(self, *a):
        """Called when the :attr:`.Display.name` for the current overlay
        changes. Updates the information display.
        """
        self.__updateInformation()


    def __updateInformation(self):
        """Refreshes the information shown on this ``OverlayInfoPanel``.
        Called by the :meth:`__selectedOverlayChanged` and
        :meth:`__overlayNameChanged` methods.
        """

        overlay   = self.__currentOverlay
        display   = self.__currentDisplay
        infoFunc  = '_{}__get{}Info'.format(type(self)   .__name__,
                                            type(overlay).__name__)
        infoFunc  = getattr(self, infoFunc, None)

        # Try and preserve the
        # current scroll position 
        scrollPos = self.__info.GetViewStart()

        # Overlay is none, or the overlay 
        # type is not supported
        if infoFunc is None:
            self.__info.SetPage('')
            self.__info.Refresh()
            return

        info = infoFunc(overlay, display)

        self.__info.SetPage(self.__formatOverlayInfo(info))

        self.__info.Refresh()
        self.__info.Scroll(scrollPos)


    def __getImageInfo(self, overlay, display):
        """Creates and returns an :class:`OverlayInfo` object containing
        information about the given :class:`.Image` overlay.

        :arg overlay: A :class:`.Image` instance.
        :arg display: The :class:`.Display` instance assocated with the
                      ``Image``.
        """
        
        info = OverlayInfo('{} - {}'.format(
            display.name, strings.labels[self, overlay]))
        img  = overlay.nibImage
        hdr  = img.get_header()

        voxUnits, timeUnits = hdr.get_xyzt_units()
        qformCode           = int(hdr['qform_code'])
        sformCode           = int(hdr['sform_code'])
        
        dimSect    = strings.labels[self, overlay, 'dimensions']
        xformSect  = strings.labels[self, overlay, 'transform']
        orientSect = strings.labels[self, overlay, 'orient']

        info.addSection(dimSect)
        info.addSection(xformSect)
        info.addSection(orientSect)

        info.addInfo(strings.labels[self, 'dataSource'], overlay.dataSource)
        info.addInfo(strings.nifti['datatype'],
                     strings.nifti['datatype', int(hdr['datatype'])])
        info.addInfo(strings.nifti['descrip'], hdr['descrip'])
        info.addInfo(strings.nifti['intent_code'],
                     strings.nifti['intent_code', int(hdr['intent_code'])])
        info.addInfo(strings.nifti['intent_name'], hdr['intent_name'])
        
        info.addInfo(strings.nifti['dimensions'],
                     '{}D'.format(len(overlay.shape)),
                     section=dimSect)

        for i in range(len(overlay.shape)):
            info.addInfo(strings.nifti['dim{}'.format(i + 1)],
                         str(overlay.shape[i]),
                         section=dimSect)

        for i in range(len(overlay.shape)):
            
            pixdim = hdr['pixdim'][i + 1]

            if   i  < 3: pixdim = '{} {}'.format(pixdim, voxUnits)
            elif i == 3: pixdim = '{} {}'.format(pixdim, timeUnits)
                
            info.addInfo(
                strings.nifti['pixdim{}'.format(i + 1)],
                pixdim,
                section=dimSect)

        info.addInfo(strings.nifti['qform_code'],
                     strings.anatomy['Image', 'space', qformCode],
                     section=xformSect)
        info.addInfo(strings.nifti['sform_code'],
                     strings.anatomy['Image', 'space', sformCode],
                     section=xformSect)

        if qformCode != constants.NIFTI_XFORM_UNKNOWN:
            info.addInfo(strings.nifti['qform'],
                         self.__formatArray(img.get_qform()),
                         section=xformSect)
            
        if sformCode != constants.NIFTI_XFORM_UNKNOWN:
            info.addInfo(strings.nifti['sform'],
                         self.__formatArray(img.get_sform()),
                         section=xformSect) 

        for i in range(3):
            orient = overlay.getVoxelOrientation(i)
            orient = '{} - {}'.format(
                strings.anatomy['Image', 'lowlong',  orient],
                strings.anatomy['Image', 'highlong', orient])
            info.addInfo(strings.nifti['voxOrient.{}'.format(i)],
                         orient,
                         section=orientSect)

        for i in range(3):
            orient = overlay.getWorldOrientation(i, code='sform')
            orient = '{} - {}'.format(
                strings.anatomy['Image', 'lowlong',  orient],
                strings.anatomy['Image', 'highlong', orient])
            info.addInfo(strings.nifti['sformOrient.{}'.format(i)],
                         orient,
                         section=orientSect)

        for i in range(3):
            orient = overlay.getWorldOrientation(i, code='qform')
            orient = '{} - {}'.format(
                strings.anatomy['Image', 'lowlong',  orient],
                strings.anatomy['Image', 'highlong', orient])
            info.addInfo(strings.nifti['qformOrient.{}'.format(i)],
                         orient,
                         section=orientSect) 

        return info


    def __getFEATImageInfo(self, overlay, display):
        """Creates and returns an :class:`OverlayInfo` object containing
        information about the given :class:`.FEATImage` overlay.

        :arg overlay: A :class:`.FEATImage` instance.
        :arg display: The :class:`.Display` instance assocated with the
                      ``FEATImage``.
        """ 
        info = self.__getImageInfo(overlay, display)

        featInfo = collections.OrderedDict([
            ('analysisName', overlay.getAnalysisName()),
            ('numPoints',    overlay.numPoints()),
            ('numEVs',       overlay.numEVs()),
            ('numContrasts', overlay.numContrasts()),
        ])

        secName = strings.labels[self, overlay, 'featInfo']
        info.addSection(secName)

        for k, v in featInfo.items():
            info.addInfo(strings.feat[k], v, section=secName)

        return info


    def __getMelodicImageInfo(self, overlay, display):
        """Creates and returns an :class:`OverlayInfo` object containing
        information about the given :class:`.MelodicImage` overlay.

        :arg overlay: A :class:`.MelodicImage` instance.
        :arg display: The :class:`.Display` instance assocated with the
                      ``MelodicImage``.
        """

        info = self.__getImageInfo(overlay, display)

        melInfo = collections.OrderedDict([
            ('tr',             overlay.tr),
            ('dataFile',       overlay.getDataFile()),
            ('partOfAnalysis', overlay.getTopLevelAnalysisDir()),
            ('numComponents',  overlay.numComponents()),
        ])

        secName = strings.labels[self, overlay, 'melodicInfo']
        info.addSection(secName)

        for k, v in melInfo.items():
            info.addInfo(strings.melodic[k], v, section=secName)

        return info

    
    def __getModelInfo(self, overlay, display):
        """Creates and returns an :class:`OverlayInfo` object containing
        information about the given :class:`.Model` overlay.

        :arg overlay: A :class:`.Model` instance.
        :arg display: The :class:`.Display` instance assocated with the
                      ``Model``.
        """ 
        info = OverlayInfo('{} - {}'.format(
            display.name,
            strings.labels[self, overlay]))

        info.addInfo(strings.labels[self, 'dataSource'], overlay.dataSource)
        info.addInfo(
            strings.labels[self, overlay, 'numVertices'],
            overlay.vertices.shape[0])
        info.addInfo(
            strings.labels[self, overlay, 'numIndices'],
            overlay.indices.shape[0]) 

        return info


    def __formatArray(self, array):
        """Creates and returns a string containing a HTML table which
        formats the data in the given ``numpy.array``.
        """

        lines = []

        lines.append('<table border="0">')

        for rowi in range(array.shape[0]):

            lines.append('<tr>')

            for coli in range(array.shape[1]):
                lines.append('<td>{}</td>'.format(array[rowi, coli]))
            lines.append('</tr>')
            
        return ''.join(lines)


    def __formatOverlayInfo(self, info):
        """Creates and returns a string containing some HTML which formats
        the information in the given ``OverlayInfo`` instance.
        """
        lines = []

        lines.append('<h3>{}</h3>'.format(info.title))

        sections = []
        sections.append((None, info.info))
        
        for secName, secInf in info.sections.items():
            sections.append((secName, secInf))

        for i, (secName, secInf) in enumerate(sections):

            if secName is not None:
                lines.append('<h4>{}</h4>'.format(secName))

            lines.append('<table border="0">')

            for i, (infName, infData) in enumerate(secInf):

                if i % 2: bgColour = '#ffffff'
                else:     bgColour = '#ffeeee'

                lines.append('<tr bgcolor="{}">'
                             '<td><b>{}</b></td>'
                             '<td>{}</td></tr>'.format(
                                 bgColour,
                                 infName,
                                 infData))

            lines.append('</table>')

        return '\n'.join(lines)


class OverlayInfo(object):
    """A little class which encapsulates human-readable information about
    one overlay. ``OverlayInfo`` objects are created and returned by the
    ``OverlayInfoPanel.__get*Info`` methods.

    The information stored in an ``OverlayInfo`` instance is organised into
    *sections*. Within each section, information is organised into key-value
    pairs. The order in which both ``OverlayInfo`` sections, and information,
    is ultimately output, is the order in which the sections/information are
    added, via the :meth:`addSection` and :meth:`addInfo` methods.
    """

    def __init__(self, title):
        """Create an ``OverlayInfo`` instance.

        :arg title: The ``OverlaytInfo`` title.
        """
        
        self.title    = title
        self.info     = []
        self.sections = collections.OrderedDict()

        
    def addSection(self, section):
        """Add a section to this ``OverlayInfo`` instance.

        :arg section: The section name.
        """
        self.sections[section] = []

        
    def addInfo(self, name, info, section=None):
        """Add some information to this ``OverlayInfo`` instance.

        :arg name:    The information name.
        :arg info:    The information value.
        :arg section: Section to place the information in.
        """ 
        if section is None: self.info             .append((name, info))
        else:               self.sections[section].append((name, info))
