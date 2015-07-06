__author__ = 'Alex'


import pymel.core as pmc
import AWGeneral as AWG
from awSettings import *


def boneSplitter(cuts=1, suffix=None, keepOriginalJoint=True):

    curSel = AWG.getCurrentSelection()

    if not curSel:
        pmc.displayError(eSELECT_BONE)
        return
    elif curSel and pmc.nodeType(curSel[0]) == 'joint':
        bone = curSel[0]
    else:
        pmc.displayError(eSELECT_BONE)
        return

    if suffix is None:
        pmc.displayError(eSUFFIX_BONE)
        return

    # get the joint's child.
    boneEnd = pmc.PyNode(pmc.pickWalk(d='down')[0])

    if not boneEnd:
        pmc.displayWarning(eBONENEEDSCHILDREN)
        return

    if not pmc.nodeType(boneEnd) == 'joint':
        pmc.displayError(eBONENEEDSCHILDREN)
        return

    # a, b, c relate to triangulation.
    # the base of c goes to the point of a and orients toward b.
    aVector = bone.getTranslation(space='world')
    bVector = boneEnd.getTranslation(space='world')
    cVector = bVector - aVector
    splitVector = (cVector / (cuts + 1))
    cLoc = aVector + splitVector

    parent = bone
    # reload(AWG)
    for cut in range(0, cuts):
        if cut == 0:
            segment = pmc.duplicate(bone)[0]
            segment.setParent(bone)
            pmc.delete(segment.getChildren())
            segment.rename(str(bone) + suffix.replace('#', '') + str(cut + 1))
            AWG.breakAttrs(segment, ['translate', 'rotate', 'scale'])
            AWG.unlockAttrs(segment, ['translate', 'rotate', 'scale'])
            pmc.makeIdentity(segment, apply=True, r=True, t=True, s=True)
            segment.setTranslation(cLoc, space='world')
            segment.setParent(bone)
            parent = segment
        else:
            segment = pmc.duplicate(parent)[0]
            segment.setParent(parent)
            segment.rename(str(bone) + suffix.replace('#', '') + str(cut+1))
            segment.setTranslation(cLoc, space='world')
            segment.setParent(parent)
            parent = segment
        cLoc += splitVector

    if not keepOriginalJoint:
        boneEnd.setParent(parent)

    pmc.select(curSel)

class OrientJoints:
    """
    Class to orient the passed in joints according to the current PySide state.
    """
    def __init__(self):
        pass

    def main(self):
        pass

    """
    if not bone:
        if pmc.selected() and pmc.nodeType(pmc.selected()[0] == 'joint'):

            bone = pmc.selected()[0]
        else:
            pmc.displayWarning('Please select a bone.')
            return
    else:
        try:
            bone = pmc.PyNode(bone)
            pmc.select(bone)
            if pmc.nodeType(bone) != 'joint':
                return
        except:
            pmc.displayWarning('Please select a bone.')
    """
