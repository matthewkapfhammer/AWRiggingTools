#!/usr/bin/python

import cPickle as pickle
from functools import partial
import traceback

import maya.cmds as cmds
import maya.OpenMaya as OM
import maya.OpenMayaUI as OMUI
import maya.OpenMayaAnim as OMA
from PySide.QtGui import *
from PySide import QtCore
from shiboken import wrapInstance


def getMayaWindow():
    main_window = OMUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QMainWindow)


def getShape(node, intermediate=False):
    """
    Gets the shape from the specified node
    :param node: Name of the transform or shape node.
    :param intermediate: True to get intermediate shape, False to get visible shape
    :return: The name of the desired shape node
    """
    if cmds.nodeType(node) == 'transform':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []

        for shape in shapes:
            isIntermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and isIntermediate and cmds.listConnections(shape, source=False):
                return shape
            elif not intermediate and not isIntermediate:
                return shape

        if shapes:
            return shapes[0]
    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        return node
    return None

class SkinCluster(object):

    kFileExtension = '.mayaskin'

    @classmethod
    def createAndImport(cls, filePath=None, shape=None):
        """
        Creates a skinCluster on the specified shape if one does not already exists & then import the weight data.
        :param filePath: the filePath
        :param shape: None / the shape of the selected object
        """
        if not shape:
            try:
                shape = cmds.ls(sl=True)[0]
            except:
                raise RuntimeError('No shape is selected.')

        if filePath is None:
            startDir = cmds.workspace(q=True, rootDirectory=True)
            filePath = cmds.fileDialog2(dialogStyle=2, fileMode=1, startingDirectory=startDir,
                                     fileFilter='Skin Files (*%s)' % SkinCluster.kFileExtension)
        if not filePath:
            return
        if not isinstance(filePath, basestring):
            filePath = filePath[0]


        fh = open(filePath, 'rb')
        data = pickle.load(fh)
        fh.close()

        """
        with open(filePath, 'rb') as loadSkin:
            data = pickle.load(loadSkin)
        """
        meshVertices = cmds.polyEvaluate(shape, vertex=True)
        importedVertices = len(data['blendWeights'])
        if meshVertices != importedVertices:
            raise RuntimeError('Vertex counts do not match. {0} != {1}'.format(meshVertices, importedVertices))

        # Check if the shape that you're importing onto has a skinCluster.
        if SkinCluster.getSkinCluster(shape):
            skinCluster = SkinCluster(shape)
        else:
            joints = data['weights'].keys()
            unusedImports = []
            noMatch = set([SkinCluster.removeNamespaceFromString(s) for s in cmds.ls(type='joint')])
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
                mappingDialog.show()

                for src, dst in mappingDialog.mapping.items():
                    # Swap mapping
                    data['weights'][dst] = data['weights'][src]
                    del data['weights'][src]

            # Create the skinCluster with post normalization so setting the weights does not normalize all weights.
            joints = data['weights'].keys()
            skinCluster = cmds.skinCluster(joints, shape, tsb=True, nw=2, n=data['name'])
            skinCluster = SkinCluster(shape)

        skinCluster.setData(data)
        print('Imported %s' % filePath)

    @classmethod
    def export(cls, filePath=None, shape=None):
        try:
            print('first')
            skin = SkinCluster(shape)
            skin.exportSkin(filePath)
            print(filePath)
            print(shape)
        except:
            print(traceback.format_exc())
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
        history = cmds.listHistory(shape, pruneDagObjects=True, il=2)
        if not history:
            return None
        skins = [h for h in history if cmds.nodeType(h) == 'skinCluster']
        if skins:
            return skins[0]
        return None

    def __init__(self, shape=None):
        if not shape:
            try:
                shape = cmds.ls(sl=True)[0]
            except:
                raise RuntimeError('No shape is currently selected.')

        self.shape = getShape(shape)
        if not self.shape:
            raise RuntimeError('No shape is connected to %s' % shape)

        self.node = SkinCluster.getSkinCluster(self.shape)
        if not self.node:
            raise ValueError('No skin cluster is attached to %s' % self.shape)


        # Get the skinCluster MObject
        selectionList = OM.MSelectionList()
        selectionList.add(self.node, True)
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
            cmds.setAttr('%s.%s' % (self.node, attr), self.data[attr])

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
            mappingDialog.show()
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
        print(influencePaths)
        numInfluences = self.fn.influenceObjects(influencePaths)
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
            startDir = cmds.workspace(q=True, rootDirectory=True)
            filePath = cmds.fileDialog2(dialogStyle=2, fileMode=0, startingDirectory=startDir,
                                        fileFilter='Skin Files (*%s)' % SkinCluster.kFileExtension)

        if not filePath:
            return

        filePath = filePath[0]
        if not filePath.endswith(SkinCluster.kFileExtension):
            filePath += SkinCluster.kFileExtension

        self.gatherData()

        fh = open(filePath, 'wb')
        pickle.dump(self.data, fh, pickle.HIGHEST_PROTOCOL)
        fh.close()

        print 'Exported skinCluster ({0} influences, {1} vertices) {2}'.format(len(self.data['weights'].keys()),
                                                                               len(self.data['blendWeights']),
                                                                               filePath)


class WeightRemapDialog(QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(WeightRemapDialog, self).__init__(parent)
        self.setWindowTitle('Remap Weights')
        self.setObjectName('remapWeightsUI')
        self.setModal(True)
        self.resize(600, 400)
        self.mapping = {}

        mainVBox = QVBoxLayout()
        label = QLabel('The following influences have no corresponding influence from the imported file. '\
                       'You can either remap the influences or skip them.')
        label.setWordWrap(True)
        mainVBox.addWidget(label)
        hbox = QHBoxLayout()
        mainVBox.addLayout(hbox)

        vbox = QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addWidget(QLabel('Unmapped Influences'))
        self.existingInfluences = QListWidget()
        vbox.addWidget(self.existingInfluences)

        vbox = QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addWidget(QLabel('Available imported influences'))
        scrollArea = QScrollArea()
        widget = QScrollArea()
        self.importedInfluencesLayout = QVBoxLayout(widget)
        vbox.addWidget(widget)

        hbox = QHBoxLayout()
        mainVBox.addLayout(hbox)
        hbox.addStretch()
        btn = QPushButton('Ok')
        btn.clicked.connect(self.accept)
        hbox.addWidget(btn)
        self.setLayout(mainVBox)

    def setInfluences(self, importedInfluences, existingInfluences):
        infs = list(existingInfluences)
        infs.sort()
        self.existingInfluences.addItems(infs)
        width = 200
        for inf in importedInfluences:
            self.row = QHBoxLayout()
            self.importedInfluencesLayout.addLayout(self.row)
            label = QLabel(inf)
            self.row.addWidget(label)
            toggleBtn = QPushButton('>')
            toggleBtn.setMaximumWidth(30)
            self.row.addWidget(toggleBtn)
            label = QLabel('')
            label.setMaximumWidth(width)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.row.addWidget(label)
            toggleBtn.clicked.connect(partial(self.setInfluenceMapping, src=inf, label=label))
        self.importedInfluencesLayout.addStretch()

    def setInfluenceMapping(self, src, label):
        selectedInfluence = self.existingInfluences.selectedItems()
        if not selectedInfluence:
            return
        dst = selectedInfluence[0].text()
        label.setText(dst)

        self.mapping[src] = dst
        index = self.existingInfluences.indexFromItem(selectedInfluence[0])
        item = self.existingInfluences.takeItem(index.row())
        del item






