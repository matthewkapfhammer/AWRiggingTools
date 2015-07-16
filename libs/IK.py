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
        self.rootObjectLine = QtGui.QLineEdit('')
        self.rootPushButton = QtGui.QPushButton('Load')

        self.rootHBox.addWidget(self.rootLabel)
        self.rootHBox.addWidget(self.rootObjectLine)
        self.rootHBox.addWidget(self.rootPushButton)

        self.shoulderLabel = QtGui.QLabel('Shoulder: ')
        self.shoulderObjectLine = QtGui.QLineEdit('')
        self.shoulderButton = QtGui.QPushButton('Load')

        self.shoulderHBox.addWidget(self.shoulderLabel)
        self.shoulderHBox.addWidget(self.shoulderObjectLine)
        self.shoulderHBox.addWidget(self.shoulderButton)

        self.createIKButton = QtGui.QPushButton('Create IK')
        self.mainLayout.addWidget(self.createIKButton)

    def _connections(self):
        self.rootPushButton.clicked.connect(lambda: self.updateField(self.rootObjectLine))
        self.shoulderButton.clicked.connect(lambda: self.updateField(self.shoulderObjectLine))
        self.createIKButton.clicked.connect(lambda: self.createIK())

    def createIK(self):
        rootObject = self.rootObjectLine.text()
        shoulderBone = self.shoulderObjectLine.text()

        pmc.select(shoulderBone, r=True)
        pyShoulder = pmc.PyNode(pmc.ls(sl=1)[0])
        pyElbow = pmc.PyNode(pmc.pickWalk(d='down')[0])
        if pyElbow:
            pyWrist = pmc.PyNode(pmc.pickWalk(d='down')[0])










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
