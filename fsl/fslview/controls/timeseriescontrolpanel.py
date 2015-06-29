#!/usr/bin/env python
#
# timeseriescontrolpanel.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import props

import fsl.fslview.panel as fslpanel
import fsl.data.strings  as strings
import                      plotcontrolpanel


class TimeSeriesControlPanel(fslpanel.FSLViewPanel):

    def __init__(self, parent, overlayList, displayCtx, tsPanel):

        fslpanel.FSLViewPanel.__init__(self, parent, overlayList, displayCtx)

        self.__tsPanel   = tsPanel

        self.__tsControl = plotcontrolpanel.PlotControlPanel(
            self, overlayList, displayCtx, tsPanel)

        self.__tsControl.SetWindowStyleFlag(wx.SUNKEN_BORDER)

        self.__demean    = props.makeWidget(self, tsPanel, 'demean')
        self.__usePixdim = props.makeWidget(self, tsPanel, 'usePixdim')

        self.__demean   .SetLabel(strings.properties[tsPanel, 'demean'])
        self.__usePixdim.SetLabel(strings.properties[tsPanel, 'usePixdim'])

        self.__optSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__optSizer.Add(self.__demean,    flag=wx.EXPAND)
        self.__optSizer.Add(self.__usePixdim, flag=wx.EXPAND)
 
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__sizer.Add(self.__optSizer,
                         flag=wx.EXPAND)
        self.__sizer.Add(self.__tsControl,
                         flag=wx.EXPAND | wx.ALL,
                         border=5,
                         proportion=1)

        self.Layout()

        self.SetMinSize(self.__sizer.GetMinSize())
        self.SetMaxSize(self.__sizer.GetMinSize())
