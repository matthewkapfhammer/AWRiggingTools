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
import math
from shiboken import wrapInstance

import pymel.core as pmc
import maya.cmds as mc
import pymel.util as PMU
import maya.OpenMayaUI as OMUI
import maya.OpenMaya as OpenMaya
from PySide import QtCore, QtGui

from libs.AWGeneral import *

def getMayaWindow():
    main_window = OMUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtGui.QWidget)

def ikPoleVectorLoc(ikPVName='ikPVLoc'):
    """Create an IK Pole Vector locator based on the bone selection.
    Requires a start, mid, end joint to be selected.

    In the future, I'll build it to work if only one joint is selected,
    but I'm a little strapped for time today.
    """
    #curSel = getCurrentSelectionList()
    curSel = pmc.ls(sl=1)
    print curSel
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
    loc = pmc.spaceLocator(name=ikPVName)
    pmc.xform(loc, worldSpace=True, translation=(zVector.x, zVector.y, zVector.z))
    pmc.xform(loc, worldSpace=True, rotation=((rot.x/math.pi*180.0),
                                              (rot.y/math.pi*180.0),
                                              (rot.z/math.pi*180.0)))
    return loc

def parentShape(child=None, parent=None, maintainOffset=True):
    '''
    Parent a child shape node to a parent transform. The child node can be a shape,
    or a transform which has any number of shapes.
    '''

    if not child or not parent:
        sel = mc.ls(sl=True)
        if sel and len(sel) > 1:
            child = sel[:-1]
            parent = sel[-1]
        else:
            OpenMaya.MGlobal.displayWarning('Please make a selection.')
            return

    parentNodeType = mc.nodeType(parent)
    if not parentNodeType in ('transform', 'joint', 'ikHandle'):
        OpenMaya.MGlobal.displayWarning('Parent must be a transform node.')
        return

    if not isinstance(child, (list, tuple)):
        child = [child]

    newChild = unparentShape(child)

    shapes = list()
    for each in newChild:
        thisChild = mc.parent(each, parent)[0]
        mc.makeIdentity(thisChild, apply=True)

        for s in mc.listRelatives(thisChild, shapes=True, noIntermediate=True, path=True):
            shape = mc.parent(s, parent, shape=True, relative=True)[0]
            #move to bottom
            mc.reorder(shape, back=True)

            #rename
            parentName = mc.ls(parent, shortNames=True)[0]
            shapes.append(mc.rename(shape, parentName+'Shape#'))

    mc.delete(newChild)

    for each in child:
        if not mc.listRelatives(each):
            #if it doesn't have any kids, delete it
            mc.delete(each)

    #return shapes



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

        pmc.select(rootObject, r=True)
        pyRootObject = pmc.PyNode(pmc.ls(sl=1)[0])
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
        if not pyRootObject:
            return

        # Assuming all joints are aligned correctly.
        try:
            softBlendLocator = pmc.PyNode(pmc.spaceLocator(n=side + 'softBlendLocator'))
            # elbowLocator = pmc.spaceLocator(n=side + 'elbowLocator')
            pmc.select(pyShoulder, pyElbow, pyWrist, r=True)
            #Create an IKPV loc at the CORRECT position.
            elbowLocator = pmc.PyNode(ikPoleVectorLoc(ikPVName=side + 'elbowLocator'))

            wristLocator = pmc.PyNode(pmc.spaceLocator(n=side + 'wristLocator'))
            upperArmLocator = pmc.PyNode(pmc.spaceLocator(n=side + 'upperArmLocator'))
            armControlDistLocator = pmc.PyNode(pmc.spaceLocator(n=side + 'armControlDistLocator'))
            armControl = pmc.nurbsSquare(n=side + 'IKArmControl')
            # Might need some work
            # Do the new IKControl setup. Fuckkkkk.
            pmc.select(cl=True)
            ikCtrlJoint = pmc.joint(n=side + 'armControlIK')
            # worry about this later
            pmc.parent(armControl, ikCtrlJoint) # parent the shape to the jnt
            self.giveXformsFromAToB(pyWrist, ikCtrlJoint)
            # pmc.select(cl=True)
            parentShape(armControl, ikCtrlJoint)
            ikCtrlJointOffset = pmc.group(ikCtrlJoint, n=side + 'armControlIK_offset', a=True)
            pmc.makeIdentity(ikCtrlJoint, apply=True, rotate=True, scale=True)
            #self.giveXformsFromAToB(pyWrist, ikCtrlJointOffset)
            # create the IK
            armIKHandle = pmc.PyNode(pmc.ikHandle(n=(side + 'armIKHandle'), sj=pyShoulder, ee=pyWrist, solver='ikRPsolver')[0])

            self.giveXformsFromAToB(pyWrist, softBlendLocator)
            #self.giveXformsFromAToB(pyElbow, elbowLocator) Should have PV position.
            self.giveXformsFromAToB(pyWrist, wristLocator)
            self.giveXformsFromAToB(pyWrist, armControlDistLocator)
            self.giveXformsFromAToB(pyShoulder, upperArmLocator)

            pmc.poleVectorConstraint(elbowLocator, armIKHandle, n=side + 'armIK_PVConstraint')
            pmc.makeIdentity(armControl, apply=True, translate=True, rotate=True, scale=True)
            pmc.delete(armControl, ch=True)

            pmc.addAttr(armControl[0], ln='slideP', sn='Slide', min=-1.0, max=1.0, dv=0.0, k=True)
            pmc.addAttr(armControl[0], ln='stretchP', sn='Stretch', min=0.0, max=1.0, dv=0.0, k=True)
            pmc.addAttr(armControl[0], ln='softP', sn='Soft', min=0.0, max=1.0, dv=0.0, k=True)
            pmc.addAttr(armControl[0], ln='pinP', sn='ElbowPinning', min=0.0, max=1.0, dv=0.0, k=True)

            pmc.aimConstraint(armControl[0], upperArmLocator, n=side+ '_rootAimConstraint', wut='objectrotation', wuo=pyRootObject)

            # I don't ever really need these, I guess. They can end up deleted at the end.
            # All I need is the number in them, I believe.
            armControlDist = pmc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0))
            softDist = pmc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0))
            upperArmDist = pmc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0))
            lowerArmDist = pmc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0))
            stretchDist = pmc.distanceDimension(sp=(0, 0, 0), ep=(0, 0, 0))

           # Also, get the transform and rename it. This is just the shape.
            pmc.rename(armControlDist, side + 'armControlDistance')
            pmc.rename(softDist, side + 'softDistance')
            pmc.rename(upperArmDist, side + 'upperArmDist')
            pmc.rename(lowerArmDist, side + 'lowerArmDist')
            pmc.rename(stretchDist, side + 'stretchDist')

            pmc.connectAttr(upperArmLocator.worldPosition[0], armControlDist.startPoint, f=True)
            pmc.connectAttr(armControlDistLocator.worldPosition[0], armControlDist.endPoint, f=True)

            pmc.connectAttr(wristLocator.worldPosition[0], softDist.startPoint, f=True)
            pmc.connectAttr(softBlendLocator.worldPosition[0], softDist.endPoint, f=True)

            pmc.connectAttr(upperArmLocator.worldPosition[0], upperArmDist.startPoint, f=True)
            pmc.connectAttr(elbowLocator.worldPosition[0], upperArmDist.endPoint, f=True)

            pmc.connectAttr(elbowLocator.worldPosition[0], lowerArmDist.startPoint, f=True)
            pmc.connectAttr(softBlendLocator.worldPosition[0], lowerArmDist.endPoint, f=True)

            pmc.connectAttr(upperArmLocator.worldPosition[0], stretchDist.startPoint, f=True)
            pmc.connectAttr(softBlendLocator.worldPosition[0], stretchDist.endPoint, f=True)


            pmc.parent(pyShoulder, wristLocator, upperArmLocator, relative=True)
            pmc.parent(upperArmLocator, elbowLocator, softBlendLocator, ikCtrlJointOffset, pyRootObject, relative=True)
            pmc.parent(armIKHandle, softBlendLocator)

            # Conditional node hell

            COND_ARM_CTRL = pmc.shadingNode('condition', n=side + 'arm_control_COND', au=True, )
            PMA_ARM_CTRL = pmc.shadingNode('plusMinusAverage', n=side + 'arm_control_PMA', au=True)
            # subtract
            pmc.setAttr(PMA_ARM_CTRL.operation, 2)
            # Need to double-check what this is - notes says 'length of both bones'.
            # Not sure if it's to add the translate or use the distance between them(from the dist shape)
            pmc.setAttr(PMA_ARM_CTRL.input1D[0], 7)
            pmc.connectAttr(armControl[0].softP, PMA_ARM_CTRL.input1D[1])
            # Greater than
            pmc.setAttr(COND_ARM_CTRL.operation, 2)
            # 113
            pmc.connectAttr(armControlDist.distance, COND_ARM_CTRL.firstTerm)
            pmc.connectAttr(PMA_ARM_CTRL.output1D, COND_ARM_CTRL.secondTerm)
            # 115
            pmc.connectAttr(armControlDist.distance, COND_ARM_CTRL.colorIfFalseR)
            COND_ARM_CTRL_SOFT = pmc.shadingNode('condition', n=side + 'arm_control_soft_COND', au=True)
            pmc.connectAttr(armControl[0].softP, COND_ARM_CTRL_SOFT.firstTerm)
            pmc.setAttr(COND_ARM_CTRL_SOFT.operation, 2)
            # Get the length of the bones and put them in here.
            pmc.setAttr(COND_ARM_CTRL_SOFT.colorIfFalseR, 7)
            #120
            PMA_ARM_SOFT = pmc.shadingNode('plusMinusAverage', n=side+'arm_soft_PMA', au=True)
            pmc.setAttr(PMA_ARM_SOFT.operation, 2)
            PMA_ARM_CTRL.output1D >> PMA_ARM_SOFT.input1D[1]

            # Taken out 127/128
            # pmc.connectAttr(armControlDist.distance, )

            ARM_SOFTP_DIV = pmc.shadingNode('multiplyDivide', n=side + 'arm_softP_DIV', au=True)
            # Set it to divide
            pmc.setAttr(ARM_SOFTP_DIV.operation, 2)

            pmc.connectAttr(armControl[0].softP, ARM_SOFTP_DIV.input2X)
            pmc.connectAttr(PMA_ARM_SOFT.output1D, ARM_SOFTP_DIV.input1X)
            ARM_INVERSE_MULT = pmc.shadingNode('multiplyDivide', n=side + 'arm_inverse_MULT', au=True)
            pmc.setAttr(ARM_INVERSE_MULT.operation, 1)
            pmc.setAttr(ARM_INVERSE_MULT.input1X, -1)
            # 134
            pmc.connectAttr(ARM_SOFTP_DIV.outputX, ARM_INVERSE_MULT.input2X, force=True)

            exponentValue = PMU.exp(1)
            ARM_EXPONENT_POWER = pmc.shadingNode('multiplyDivide', n=side + 'arm_exponent_power', au=True)
            pmc.setAttr(ARM_EXPONENT_POWER.operation, 3)
            pmc.setAttr(ARM_EXPONENT_POWER.input1X, exponentValue)

            ARM_INVERSE_MULT.outputX >> ARM_EXPONENT_POWER.input2X
            #141
            ARM_CTRL_SOFTP_MULT = pmc.shadingNode('multiplyDivide', n=side + 'arm_control_softP_MULT', au=True)
            pmc.setAttr(ARM_CTRL_SOFTP_MULT.operation, 1)
            armControl[0].softP >> ARM_CTRL_SOFTP_MULT.input1X
            ARM_EXPONENT_POWER.outputX >> ARM_CTRL_SOFTP_MULT.input2X
            ARM_CHAINLENGTH_PMA = pmc.shadingNode('plusMinusAverage', n=side + 'arm_chainlength_PMA', au=True)
            ARM_CTRL_SOFTP_MULT.outputX >> ARM_CHAINLENGTH_PMA.input1D[1]
            # Get the length of the bones and plug it in here.
            pmc.setAttr(ARM_CHAINLENGTH_PMA.input1D[0], 7)
            # Check if correct
            COND_ARM_CTRL_SOFT.outColorR >> COND_ARM_CTRL.colorIfTrueR
            COND_ARM_CTRL.outColorR >> wristLocator.tx









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
