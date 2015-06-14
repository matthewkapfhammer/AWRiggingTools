#!/usr/bin/python

import cPickle as pickle

import pymel.core as pm

import maya.OpenMaya as OM
import maya.OpenMayaUI as OMUI
import maya.OpenMayaAnim as OMA

def getShape(node, intermediate=False):
    """
    Gets the shape from the specified node
    :param node: Name of the transform or shape node.
    :param intermediate: True to get intermediate shape, False to get visible shape
    :return: The name of the desired shape node
    """
    if pm.nodeType(node) == 'transform':
        shapes = pm.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []

        for shape in shapes:
            isIntermediate = pm.getAttr('%s.intermediateObject' % shape)
            if intermediate and isIntermediate and pm.listConnections(shape, source=False):
                return shape
            elif not intermediate and not isIntermediate:
                return shape

        if shapes:
            return shapes[0]
    elif pm.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        return node
    return None

class SkinCluster(object):

    kFileExtension = '.skin'

    @classmethod
    def createAndImport(cls, filePath=None, shape=None):
        """
        Creates a skinCluster on the specified shape if one does not already exists & then import the weight data.
        :param filePath: the filePath
        :param shape: None / the shape of the selected object
        """
        if not shape:
            try:
                shape = pm.ls(sl=True)[0]
            except:
                raise RuntimeError('No shape is selected.')

        if filePath is None:
            startDir = pm.workspace(q=True, rootDirectory=True)
            filePath = pm.fileDialog(dialogStyle=2, fileMode=1, startingDirectory=startDir,
                                     fileFilter='Skin Files (*%s)' % SkinCluster.kFileExtension)
        if not filePath:
            return
        if not isinstance(filePath, basestring):
            filePath = filePath[0]

        """
        If this doesn't work:
        fh = open(filePath, 'rb')
        data = pickle.load(fh)
        fh.close()
        """
        with open(filePath, 'rb') as loadSkin:
            data = pickle.load(loadSkin)

        meshVertices = pm.polyEvaluate(shape, vertex=True)
        importedVertices = len(data['blendWeights'])
        if meshVertices != importedVertices:
            raise RuntimeError('Vertex counts do not match. {0} != {1}'.format(meshVertices, importedVertices))

        # Check if the shape that you're importing onto has a skinCluster.
        if SkinCluster.getSkinCluster(shape):
            skinCluster = SkinCluster(shape)
        else:
            joints = data['weights'].keys()
            unusedImports = []
            noMatch = set([SkinCluster.removeNamespaceFromString(s) for s in pm.ls(type='joint')])
            for j in joints:
                if j in noMatch:
                    noMatch.remove(j)
                else:
                    unusedImports.append(j)
            # If there were unmapped influences ask the user to map them.
            if unusedImports and noMatch:
                # Write the weightRemapDialog tomorrow
                mappingDialog = WeightRemapDialog(getMayaWindow())
                mappingDialog.setInfluences(unusedImports, noMatch)
                mappingDialog.exec_()

                for src, dst in mappingDialog.mapping.items():
                    # Swap mapping
                    data['weights'][dst] = data['weights'][src]
                    del data['weights'][src]

            # Create the skinCluster with post normalization so setting the weights does not normalize all weights.
            joints = data['weights'].keys()
            skinCluster = pm.skinCluster(joints, shape, tsb=True, nw=2, n=data['name'])
            skinCluster = SkinCluster(shape)

        skinCluster.setData(data)
        print('Imported %s' % filePath)

    @classmethod
    def export(cls, filePath=None, shape=None):
        skin = SkinCluster(shape)
        skin.exportSkin(filePath)

    @classmethod
    def removeNamespaceFromString(cls, value):
        """
        Removes namespaces from string

        NAMESPACE:joint1|NAMESPACE:joint2 becomes
        joint1|joint2

        :param value: String name with namespace
        :return:name without namespaces
        """
        tokens = value.split('|')
        result = ''
        for i, token in enumerate(tokens):
            if (i > 0):
                result += '|'
            result += token.split(':')[-1]
        return result

    @classmethod
    def getSkinCluster(cls, shape):
        """
        Get skinCluster node attached to the specified shape:
        :param shape: Shape node name
        :return: The attached skin cluster name or None if no skin cluster is attached:
        """
        shape = getShape(shape)
        history = pm.listHistory(shape, pruneDagObjects=True, il=2)
        if not history:
            return None
        skins = [h for h in history if pm.nodeType(h) == 'skinCluster']
        if skins:
            return skins[0]
        return None

    def __init__(self, shape=None):
        if not shape:
            try:
                shape = pm.ls(sl=True)[0]
            except:
                raise RuntimeError('No shape is currently selected.')

        self.shape = getShape(shape)
        if not self.shape:
            raise RuntimeError('No shape is connected to %s' % shape)

        self.node = SkinCluster.getSkinCluster(shape)
        if not self.node:
            raise ValueError('No skin cluster is attached to %s' % self.shape)


        # Get the skinCluster MObject
        selectionList = OM.MSelectionList()
        selectionList.add(self.node)
        self.mobject = OM.MObject()
        selectionList.getDependNode(0, self.mobject)
        self.fn = OMA.MFnSkinCluster(self.mobject)

        self.data = {
            'weights' : {},
            'blendWeights' : [],
            'name' : self.node,
        }

    def setData(self, data):
        """
        Sets the data and stores it in the Maya skinCluster node
        :param data: Data dictionary
        """
        self.data = data
        dagPath, components = self.__getGeometryComponents()
        self.setInfluenceWeights(dagPath, components)
        self.setBlendWeights(dagPath, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            pm.setAttr('%s.%s' % (self.node, attr), self.data[attr])

    def setBlendWeights(self, dagPath, components):
        blendWeights = OM.MDoubleArray(len(self.data['blendWeights']))
        for i, w in enumerate(self.data['blendWeights']):
            blendWeights.set(w, i)
        self.fn.setBlendWeights(dagPath, components, blendWeights)

    def setInfluenceWeights(self, dagPath, components):
        weights = self.__getCurrentWeights(dagPath, components)
        influencePaths = OM.MDagPathArray()
        numInfluences = self.fn.influenceObjects(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences

        unusedImports = []

        noMatch = [influencePaths[i].partialPathName() for i in range(influencePaths.length())]

        for importedInfluence, importedWeights in self.data['weights'].items():
            for i in range(influencePaths.length()):
                influenceName = influencePaths[i].partialPathName()
                influenceWithoutNamespace = SkinCluster.removeNamespaceFromString(influenceName)
                if influenceWithoutNamespace == importedInfluence:
                    # store imported weights into MDoubleArray
                    for j in range(numComponentsPerInfluence):
                        weights.set(importedWeights[j], j*numInfluences+i)
                    noMatch.remove(influenceName)
                    break
            else:
                unusedImports.append(importedInfluence)

        if unusedImports and noMatch:
            mappingDialog = WeightRemapDialog(getMayaWindow())
            mappingDialog.setInfluences(unusedImports, noMatch)
            mappingDialog.exec_()
            for src, dst in mappingDialog.mapping.items():
                for i in range(influencePaths.length()):
                    if influencePaths[i].partialPathName() == dst:
                        for j in range(numComponentsPerInfluence):
                            weights.set(self.data['weights'][src][j], j*numInfluences+1)
                        break

        influenceIndices = OM.MIntArray(numInfluences)
        for i in range(numInfluences):
            influenceIndices.set(i, i)
        # False = normalize
        self.fn.setWeights(dagPath, components, influenceIndices, weights, False)

    def gatherData(self):
        dagPath, components = self.__getGeometryComponents()
        self.gatherInfluenceWeights(dagPath, components)
        self.gatherBlendWeights(dagPath, components)

        for attr in ['skinningMethod', 'normalizeWeights']:
            self.data[attr] = cmds.getAttr('%s.%s' % (self.node, attr))

    def __getGeometryComponents(self):
        # Has jurisdiction over what is allowed to be influenced.
        fnSet = OM.MFnSet(self.fn.deformerSet())
        members = OM.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OM.MDagPath()
        components = OM.MObject()
        members.getDagPath(0, dagPath, components)
        return dagPath, components

    def __getCurrentWeights(self, dagPath, components):
        weights = OM.MDoubleArray()
        util = OM.MScriptUtil()
        util.createFromInt(0)
        pUInt = util.asUintPtr()
        self.fn.getWeights(dagPath, components, weights, pUInt)
        return weights

    def gatherInfluenceWeights(self, dagPath, components):
        """Gathers all the influence weights"""
        weights = self.__getCurrentWeights(dagPath, components)

        influencePaths = OM.MDagPathArray()
        numInfluences = self.fn.influenceObject(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences
        for i in range(influencePaths.length()):
            influenceName = influencePaths[i].partialPathName()
            # store weights by influence & not by namespace so it can be imported with different namespaces.
            influenceWithoutNamespace = SkinCluster.removeNamespaceFromString(influenceName)
            self.data['weights'][influenceWithoutNamespace] = \
                [weights[jj*numInfluences+i] for jj in range(numComponentsPerInfluence)]

    def gatherBlendWeights(self, dagPath, components):
        weights = OM.MDoubleArray()
        self.fn.getBlendWeights(dagPath, components, weights)
        self.data['blendWeights'] = [weights[i] for i in range(weights.length())]

    def exportSkin(self, filePath=None):
        """
        Exports the skinCluster data to disk.
        :param filePath: filePath.
        """
        if filePath is None:
            startDir = pm.workspace(q=True, rootDirectory=True)
            filePath = pm.fileDialog(dialogStyle=2, fileMode=0, startingDirectory=startDir,
                                     fileFilter='Skin Files (*%s)' % SkinCluster.kFileExtension)

        if not filePath:
            return

        filePath = filePath[0]
        if not filePath.endswith(SkinCluster.kFileExtension):
            filePath += SkinCluster.kFileExtension

        self.gatherData()

        """
        In case the below doesn't work properly:
        fh = open(filePath, 'wb')
        pickle.dump(self.data, fh, pickle.HIGHEST_PROTOCOL)
        fh.close()
        """

        with open(filePath, 'wb') as skinFile:
            pickle.dump(self.data, skinFile, pickle.HIGHEST_PROTOCOL)

        print 'Exported skinCluster ({0} influences, {1} vertices) {2}'.format(len(self.data['weights'].keys()),
                                                                               len(self.data['blendWeights']),
                                                                               filePath)









