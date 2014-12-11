#!/usr/bin/env python
#
# editor.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging
log = logging.getLogger(__name__)

import collections

import numpy as np


class Change(object):
    
    def __init__(self, image, selection, oldVals, newVals):
        self.image     = image
        self.selection = selection
        self.oldVals   = oldVals
        self.newVals   = newVals


class Selection(object):
    
    def __init__(self, image):
        
        self.image     = image
        self.selection = np.zeros(image.shape, dtype=np.bool)

        self._selectedCache = None
        

        
    def addToSelection(self, xyzs):
        xyzs = xyzs.T
        xs   = xyzs[0]
        ys   = xyzs[1]
        zs   = xyzs[2]

        self.selection[xs, ys, zs] = True
        self._selectedCache        = None

    
    def clearSelection(self):
        self.selection[:]   = False
        self._selectedCache = None



    def getSelection(self):
        
        if self._selectedCache is None:
            xs, ys, zs          = np.where(self.selection)
            self._selectedCache = np.vstack((xs, ys, zs)).T

        return self._selectedCache


        
    def getSelectionSize(self):
        return self.selection.sum()


class Editor(object):

    def __init__(self, imageList, displayCtx):

        self._name       = '{}_{}'.format(self.__class__.__name__, id(self))
        self._imageList  = imageList
        self._displayCtx = displayCtx
        self._selection  = None
 
        # Two stacks of Change objects, providing
        # records of what has been done and undone
        self._doneStack   = []
        self._undoneStack = []

        self._displayCtx.addListener('selectedImage',
                                     self._name,
                                     self._selectedImageChanged)
        self._imageList .addListener('images',
                                     self._name,
                                     self._selectedImageChanged) 

        self._selectedImageChanged()

        
    def __del__(self):
        self._displayCtx.removeListener('selectedImage', self._name)
        self._imageList .removeListener('images',        self._name)


    def _selectedImageChanged(self, *a):

        if len(self._imageList) == 0:
            self._selection       = None
            self.addToSelection   = None 
            self.clearSelection   = None
            self.getSelection     = None
            self.getSelectionSize = None
            return
        
        image = self._displayCtx.getSelectedImage()
        
        self._selection       = Selection(image)
        self.addToSelection   = self._selection.addToSelection
        self.clearSelection   = self._selection.clearSelection
        self.getSelection     = self._selection.getSelection
        self.getSelectionSize = self._selection.getSelectionSize


    def makeChange(self, newVals):

        image = self._displayCtx.getSelectedImage().data
        nvox  = self.getSelectionSize()

        if not isinstance(newVals, collections.Sequence):
            newVals = [newVals] * nvox
        else:
            newVals = np.array(newVals)

        xyzs    = self.getSelection()
        oldVals = image[self._selection.selection]
        
        image[self._selection.selection] = newVals

        change = Change(image, xyzs, oldVals, newVals)

        self._doneStack.append(change)


    def canUndo(self):
        return len(self._doneStack) > 0

    
    def canRedo(self):
        return len(self._undoneStack) > 0 


    def undo(self):
        if not self.canUndo():
            return
        change = self._doneStack.pop()
        self._revertChange(change)
        self._undoneStack.append(change)
        

    def redo(self):
        if not self.canRedo():
            return        
        change = self._undoneStack.pop()
        self._applyChange(change)
        self._doneStack.append(change)


    def _applyChange(self, change):
        change.image[change.selection] = change.newVals

        
    def _revertChange(self, change):
        change.image[change.selection] = change.oldVals
