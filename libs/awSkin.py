__author__ = 'Alex'

# Nothing working.
import pymel.core as pmc

from AWGeneral import *
from awSettings import *

def reskinSubDiv(mesh, subDMeshes, history, smooth):
    curSel = getCurrentSelectionList()
    meshHistory = pmc.listHistory(mesh)
    if len(mesh) == 1:
        # set this up.
        reskinSubD(mesh, subDMeshes, history, smooth)

def reskinSubD(mesh, subDMesh, history, smooth):
    curSel = getCurrentSelectionList()
    meshHistory = pmc.listHistory()
    skinCluster = pmc.ls(meshHistory, type='skinCluster')
    if skinCluster[0]:
        attachedJoints = pmc.listConnections(skinCluster[0], type='joint')
        pmc.select(subDMesh)
        if history:
            pmc.deleteHistory()
        unlockAttrs(subDMesh, ['translate', 'rotate', 'scale'])
        pmc.makeIdentity(apply=True, t=True, r=True, s=True, n=False)

        if len(attachedJoints) > 0:
            pmc.select(attachedJoints, add=True)
            # new Skin Cluster
            # Open Maya
            pmc.select(mesh, replace=True)
            pmc.select(subDMesh, add=True)
            if smooth:
                pmc.copySkinWeights(ss=skinCluster[0], ds=newSkinCluster[0], noMirror=True, smooth=True)
            else:
                pmc.copySkinWeights(ss=skinCluster[0], ds=newSkinCluster[0], noMirror=True)
    else:
        pmc.displayWarning(wNOSKINCLUSTER)
    pmc.select(curSel)









