__author__ = 'Alex'

import math
import pymel.core as pmc
import maya.OpenMaya as OM

from AWGeneral import *
from awSettings import *


def ikPoleVectorLoc():
    """Create an IK Pole Vector locator based on the bone selection.
    Requires a start, mid, end joint to be selected.

    In the future, I'll build it to work if only one joint is selected,
    but I'm a little strapped for time today.
    """
    curSel = getCurrentSelection()

    if len(curSel) != 3:
        pmc.displayError(eSELECTSTARTMIDEND)
        return

    for childBone in curSel:
        if pmc.nodeType(childBone) != 'joint':
            pmc.displayError(eSELECTONLYBONES)
            return

    startBone = pmc.xform(curSel[0], query=True, worldSpace=True, translation=True)
    midBone = pmc.xform(curSel[1], query=True, worldSpace=True, translation=True)
    endBone = pmc.xform(curSel[2], query=True, worldSpace=True, translation=True)

    aVector = OM.MVector(startBone[0], startBone[1], startBone[2])
    bVector = OM.MVector(midBone[0], midBone[1], midBone[2])
    cVector = OM.MVector(endBone[0], endBone[1], midBone[2])

    acVector = cVector - aVector
    abVector = bVector - aVector

    dotProduct = abVector * acVector

    projection = float(dotProduct) / float(acVector.length())
    acVectorNormal = acVector.normal()

    projectionVector = acVectorNormal * projection
    xVector = abVector - projectionVector
    xVector *= 0.5

    zVector = xVector + bVector
    cross1 = acVector - abVector
    cross1.normalize()
    cross2 = cross1 ^ xVector
    cross2.normalize()
    xVector.normalize()

    matrixVector = [xVector.x, xVector.y, xVector.z, 0,
                    cross1.x, cross1.y, cross1.z, 0,
                    cross2.x, cross2.y, cross2.z, 0,
                    0, 0, 0, 1]

    mMatrix = OM.MMatrix()

    OM.MScriptUtil.createMatrixFromList(matrixVector, mMatrix)
    xformMatrix = OM.MTransformationMatrix(mMatrix)
    rot = xformMatrix.eulerRotation()
    loc = pmc.spaceLocator(name='ikPoleVectorLoc01')
    pmc.xform(loc, worldSpace=True, translation=(zVector.x, zVector.y, zVector.z))
    pmc.xform(loc, worldSpace=True, rotation=((rot.x/math.pi*180.0),
                                              (rot.y/math.pi*180.0),
                                              (rot.z/math.pi*180.0)))
