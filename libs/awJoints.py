__author__ = 'Alex'


import pymel.core as pmc
from AWGeneral import *


def splitBone(cuts=1, bone=None):

    curSel = pmc.selected()

    if cuts <= 0:
        pmc.displayWarning('Please enter a number greater than 0.')
        return

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

    # get the joint's child.
    boneEnd = pmc.PyNode(pmc.pickWalk(d='down')[0])

    # get and calculate vectors.
    # a, b, c relate to triangulation.
    # the base of c goes to the point of a and orients toward b.
    aVector = bone.getTranslation(space='world')
    bVector = boneEnd.getTranslation(space='world')
    cVector = bVector - aVector
    splitVector = (cVector / (cuts + 1))
    cLoc = aVector + splitVector

    parent = bone
    selChildren = bone.getChildren()

    for cut in range(0, cuts):
        if cut == 0:
            segment = pmc.duplicate(bone)[0]
            segment.setParent(bone)
            pmc.delete(seg.getChildren())
            segment.rename(str(bone) + '_split1')
            breakAttrs(segment, ['.t', '.r', '.s'])
            unlockXForms(segment)
            pmc.makeIdentity(segment, apply=True, r=True, t=True, s=True)
            segment.setTranslation(cLoc, space='world')
            parent = segment
        else:
            segment = pmc.duplicate(parent)[0]
            segment.setParent(parent)
            segment.rename(str(bone) + '_split' + str(cut+1))
            segment.setTranslation(cLoc, space='world')
            parent = segment
        cLoc += splitVector

    for selChild in selChildren:
        selChild.setParent(parent)

    pmc.selected(curSel)

class OrientJoints:
    """
    Class to orient the passed in joints according to the current PySide state.
    """
    def __init__(self):
        pass

    def main(self):
        pass

