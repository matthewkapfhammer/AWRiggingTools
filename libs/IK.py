#!/usr/bin/python
"""
If you're reading this and it's still up, this is merely a protoype.
Don't judge me based on this.
I'm trying to get something done as fast as possible.
Projected features in here:
Elbow Sliding
Stretchy IK.
Soft IK(works with stretching)
Elbow Pinning

A lot of this will be hardcoded for now because it needs to be finished for a rig like... yesterday.
Later on, I'll make it modular. Just no time right now.
"""
import traceback
from shiboken import wrapInstance

import pymel.core as pmc
import maya.OpenMayaUI as OMUI
from PySide import QtCore, QtGui

import libs.AWGeneral as AWG

def getMayaWindow():
    main_window = OMUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtGui.QWidget)

class IKSTUFF(QtGui.QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(IKSTUFF, self).__init__(parent)

    def start(self):
        self.setWindowTitle('Super IK')
        self.setObjectName('IKCreator')
        self.resize(400, 400)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self._layout()
        self._connections()

    def _layout(self):
        # Testing to see if I can just pass self to set it without self.setLayout
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)

        self.rootHBox = QtGui.QHBoxLayout()
        self.shoulderHBox = QtGui.QHBoxLayout()


        self.mainLayout.addLayout(self.rootHBox)
        self.mainLayout.addLayout(self.shoulderHBox)

        self.rootLabel = QtGui.QLabel('Root Object: ')
        self.rootObjectLine = QtGui.QLineEdit('null_l_armRoot')
        self.rootPushButton = QtGui.QPushButton('Load')

        self.rootHBox.addWidget(self.rootLabel)
        self.rootHBox.addWidget(self.rootObjectLine)
        self.rootHBox.addWidget(self.rootPushButton)

        self.shoulderLabel = QtGui.QLabel('Shoulder: ')
        self.shoulderObjectLine = QtGui.QLineEdit('shoulder_L_JNT')
        self.shoulderButton = QtGui.QPushButton('Load')

        self.shoulderHBox.addWidget(self.shoulderLabel)
        self.shoulderHBox.addWidget(self.shoulderObjectLine)
        self.shoulderHBox.addWidget(self.shoulderButton)

        self.sideHBox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(self.sideHBox)

        self.sideLabel = QtGui.QLabel('Side: ')
        self.sideLine = QtGui.QLineEdit('L_')
        self.sideHBox.addWidget(self.sideLabel)
        self.sideHBox.addWidget(self.sideLine)


        self.createIKButton = QtGui.QPushButton('Create IK')
        self.mainLayout.addWidget(self.createIKButton)

    def _connections(self):
        self.rootPushButton.clicked.connect(lambda: self.updateField(self.rootObjectLine))
        self.shoulderButton.clicked.connect(lambda: self.updateField(self.shoulderObjectLine))
        self.createIKButton.clicked.connect(lambda: self.createIK())

    def createIK(self):
        side = self.sideLine.text()
        rootObject = self.rootObjectLine.text()
        shoulderBone = self.shoulderObjectLine.text()

        pmc.select(shoulderBone, r=True)
        pyShoulder = pmc.PyNode(pmc.ls(sl=1)[0])
        pyElbow = pmc.PyNode(pmc.pickWalk(d='down')[0])
        if pyElbow:
            pyWrist = pmc.PyNode(pmc.pickWalk(d='down')[0])
        else:
            return
        if not pyWrist:
            return
        if not rootObject:
            return

        # Assuming all joints are aligned correctly.
        try:
            softBlendLocator = pmc.spaceLocator(n=side + 'softBlendLocator')
            elbowLocator = pmc.spaceLocator(n=side + 'elbowLocator')
            wristLocator = pmc.spaceLocator(n=side + 'wristLocator')
            upperArmLocator = pmc.spaceLocator(n=side + 'upperArmLocator')
            armControlDistLocator = pmc.spaceLocator(n=side + 'armControlDistLocator')
            armControl = pmc.nurbsSquare(n=side + 'IKArmControl')
            # Might need some work
            # Do the new IKControl setup. Fuckkkkk.
            pmc.select(cl=True)
            ikCtrlJoint = pmc.joint(n=side + 'armControlIK')
            # worry about this later
            pmc.parent(armControl, ikCtrlJoint, relative=True, shape=True) # parent the shape to the jnt

            self.giveXformsFromAToB(pyWrist, ikCtrlJoint)
            # pmc.select(cl=True)
            ikCtrlJointOffset = pmc.group(ikCtrlJoint, n=side + 'armControlIK_offset', a=True)
            pmc.makeIdentity(ikCtrlJoint, apply=True, rotate=True, scale=True)

            #self.giveXformsFromAToB(pyWrist, ikCtrlJointOffset)
            pmc.ikHandle

            self.giveXformsFromAToB(pyWrist, softBlendLocator)
            self.giveXformsFromAToB(pyElbow, elbowLocator)
            self.giveXformsFromAToB(pyWrist, wristLocator)
            self.giveXformsFromAToB(pyWrist, armControlDistLocator)
            self.giveXformsFromAToB(pyShoulder, upperArmLocator)



            # parent everything under the root node
            # last object is the parent
            pmc.parent(upperArmLocator, wristLocator, pyShoulder, wristLocator, rootObject, relative=True)
        except:
            print(traceback.format_exc())



    def giveXformsFromAToB(self, objectA, objectB):
        objectAXFormT = pmc.xform(objectA, q=True, ws=True, t=True)
        objectAXFormR = pmc.xform(objectA, q=True, ws=True, ro=True)
        objectBXForm = pmc.xform(objectB, ws=True, t=objectAXFormT, ro=objectAXFormR)


















    def updateField(self, line):
        itemName = pmc.ls(sl=1)[0]
        print(itemName)
        if itemName:
            line.setText(itemName.name())

    def getFieldContents(self, item):
        return item.text()

try:
    createSuperIK.deleteLater()
except:
    pass

createSuperIK = IKSTUFF()

try:
    createSuperIK.start()
    createSuperIK.show()
except:
    createSuperIK.deleteLater()
    print(traceback.format_exc())
