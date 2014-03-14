#!/usr/bin/env python
#
# __init__.py - Sets up the tkprop package namespace.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from tkprop.properties import \
    PropertyBase,  \
    HasProperties, \
    Boolean,       \
    Int,           \
    Double,        \
    Percentage,    \
    String,        \
    Choice,        \
    List,          \
    FilePath

from tkprop.widgets import \
    makeWidget

from tkprop.build import \
    buildGUI,      \
    ViewItem,      \
    Button,        \
    Widget,        \
    Group,         \
    NotebookGroup, \
    HGroup,        \
    VGroup
