#!/usr/bin/python

import pymel.core as pmc
import maya.OpenMaya as OM

from awSettings import *


def getCurrentSelectionList():
    #return pmc.ls(sl=1)
    curSel = OM.MSelectionList()
    OM.MGlobal.getActiveSelectionList(curSel)
    return curSel

def getCurrentItemSelected():
    curSel = OM.MSelectionList()
    OM.MGlobal.getActiveSelectionList(curSel)

    if curSel.length() > 1:
        # if you create an object, I think the shape is selected.
        # Maybe write something in here to check and see that they are
        # the same object.
        pmc.displayWarning(eTOOMANYOBJECTSSELECTED)
        return
    elif curSel.length() == 0:
        pmc.displayWarning(eSELECTOBJECT)
        return
    else:
        for i in xrange(curSel.length()):
            item = OM.MObject()
            curSel.getDependNode(i, item)
            itemFn = OM.MFnDependencyNode(item)
            return itemFn

def breakAttrs(node, channels):
    """
    Wrote for batch breaking of attributes instead of doing them one by one.
    :param node: The node upon which to sever an attribute connection.
    :param nodeAttr: List or string. If list, operate on the node for each attr.
    """
    if not isinstance(channels, list):
        pmc.displayError(eINCORRECTTYPE)
        return

    for c in channels:
        pmc.disconnectAttr(node + '.' + c)


def unlockAttrs(node, channels):
    """
    Wrote for batch unlocking of attributes instead of doing them one by one.
    :param node: The node upon which to unlock an attribute connection.
    :param channels: List of channels to unlock.
    """
    # dev
    if not isinstance(channels, list):
        pmc.displayError(eINCORRECTTYPE)
        return

    for c in channels:
        pmc.setAttr(str(node) + '.' + c, lock=False, keyable=True)


def lockAttrs(node, channels):
    """
    Wrote for batch locking of attributes instead of doing them one by one.
    :param node: The node upon which to lock an attribute connection.
    :param channels: List of channels to lock.
    """
    # dev
    if not isinstance(channels, list):
        pmc.displayError(eINCORRECTTYPE)
        return

    for c in channels:
        pmc.setAttr(str(node) + '.' + c, lock=True, keyable=False)


def getSelectedItemOfType(nodeType):
    curSel = getCurrentSelection()
    if len(curSel) == 1 and pmc.nodeType(curSel) == nodeType:
        return str(curSel)
    elif len(curSel) < 1:
        pmc.displayError(eSELECTOBJECT)
        return
    elif pmc.nodeType(curSel) != nodeType:
        pmc.displayError('{0} {1}'.format(eSELECTTHISTYPE, nodeType))
        return
    else:
        pmc.displayError(eTOOMANYOBJECTSSELECTED)
        return

def getSelectedItemsOfType(nodeType):
    curSel = getCurrentSelection()
    if curSel and pmc.nodeType(curSel) == nodeType:
        return curSel
    elif not curSel:
        pmc.displayError(eSELECTOBJECT)
        return
    elif pmc.nodeType(curSel) != nodeType:
        pmc.displayError('{0} {1}'.format(eSELECTTHISTYPE, nodeType))

