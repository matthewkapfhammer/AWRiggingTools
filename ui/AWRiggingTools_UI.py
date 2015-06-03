#!/usr/bin/python

import traceback
from shiboken import wrapInstance

import pymel.core as pmc
import maya.OpenMayaUI
from maya.app.general.mayaMixin import  MayaQWidgetDockableMixin
from PySide import QtCore
from PySide.QtGui import *

import libs.awRenamer as AWR
import libs.awMirrorObj as AMO
from libs.AWGeneral import *


reload(AWR)

def showui():
    main_window = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QWidget)

class AWTools_UI(QDialog):
    """
    Words
    """
    def __init__(self, parent=showui()):
        super(AWTools_UI, self).__init__(parent)

    def start(self):
        self.setWindowTitle('Alex Rigging Tools')
        self.setObjectName('AlexRiggingTools')
        self.setMinimumSize(400, 750)
        self.setMaximumSize(400, 750)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        #self.setDockableParameters(dockable=True, width=0, height=0)
        self._layout()
        self._connections()


    def _connections(self):
        self.rename_searchReplaceButton.clicked.connect(lambda: self.searchAndReplace())
        self.rename_prefixButton.clicked.connect(lambda: self.addPrefix())
        self.rename_suffixButton.clicked.connect(lambda: self.addSuffix())
        self.rename_renameButton.clicked.connect(lambda: self.renameItems())

    def renameItems(self):
        strRename  = self.getFieldContents(self.rename_renameField)
        startNum = self.getFieldContents(self.rename_startField)
        paddingNum = self.getFieldContents(self.rename_paddingField)

        AWR.rename(strRename, startNum, paddingNum)

    def addSuffix(self):
        AWR.suffix(self.getFieldContents(self.rename_suffixField))

    def addPrefix(self):
        AWR.prefix(self.getFieldContents(self.rename_prefixField))

    def searchAndReplace(self):
        searchFor = self.getFieldContents(self.rename_searchField)
        replaceWith = self.getFieldContents(self.rename_replaceField)
        AWR.searchReplace(searchFor, replaceWith)

    def getFieldContents(self, item):
        return item.text()

    def getSelection(self):
        return pmc.ls(sl=True)

    def _createSecondUI(self):

        # Custom Hierarchies
        self.customHierarchiesBox = QGroupBox('Select Custom Hierarchies')
        self.operations_customHierarchiesLayout = QVBoxLayout(self.customHierarchiesBox)
        self.operations_excludeText = QLabel('Exclude nodes with this text:')

        self.operations_customHi_excludeField = QLineEdit('')
        self.operations_customHi_excludeNodesText = QLabel('Exclude these types of nodes:')
        self.operations_customHi_selectButton = QPushButton('Select Hierarchy')

        self.operations_customHi_checkNodes = QHBoxLayout()
        self.operations_customHi_meshCheck = QCheckBox('Mesh')
        self.operations_customHi_jointCheck = QCheckBox('Joint')
        self.operations_customHi_constraintCheck = QCheckBox('Constraint')
        self.operations_customHi_ikCheck = QCheckBox('IK')
        self.operations_customHi_nullCheck = QCheckBox('Null')
        self.operations_customHi_locatorCheck = QCheckBox('Locator')
        #self.operations_customHi_nurbsCheck = QCheckBox('Nurbs')

        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_meshCheck)
        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_jointCheck)
        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_constraintCheck)
        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_ikCheck)
        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_nullCheck)
        self.operations_customHi_checkNodes.addWidget(self.operations_customHi_locatorCheck)
        #self.operations_customHi_checkNodes.addWidget(self.operations_customHi_nurbsCheck)


        self.operations_customHierarchiesLayout.addWidget(self.operations_excludeText)
        self.operations_customHierarchiesLayout.addWidget(self.operations_customHi_excludeField)
        self.operations_customHierarchiesLayout.addWidget(self.operations_customHi_excludeNodesText)
        self.operations_customHierarchiesLayout.addLayout(self.operations_customHi_checkNodes)
        self.operations_customHierarchiesLayout.addWidget(self.operations_customHi_selectButton)

    def _createConstraintsLayout(self):
        self.constraintsBox = QGroupBox('Constraining')
        self.constraintsBox_layout = QVBoxLayout(self.constraintsBox)


    def _createRenamerUI(self):

        self.lineEdit_integerValidator = QIntValidator()

        self.rename_searchFieldLabel = QLabel('Search For:')
        self.rename_searchFieldLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rename_searchField = QLineEdit('')
        self.rename_replaceFieldLabel = QLabel('Replace With:')
        self.rename_replaceFieldLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rename_replaceField = QLineEdit('')
        self.rename_searchReplaceButton = QPushButton('Search And Replace')

        self.rename_prefixLabel = QLabel('Prefix:')
        self.rename_prefixLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rename_prefixField = QLineEdit('')
        self.rename_prefixButton = QPushButton('Add Prefix')

        self.rename_suffixLabel = QLabel('Suffix:')
        self.rename_suffixLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rename_suffixField = QLineEdit('')
        self.rename_suffixButton = QPushButton('Add Suffix')

        self.rename_renameLabel = QLabel('Rename:')
        self.rename_renameLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rename_renameField = QLineEdit('')

        self.rename_startNumber = QLabel('Start #:')
        self.rename_startNumber.setAlignment(QtCore.Qt.AlignRight)
        self.rename_startField = QLineEdit('1')
        self.rename_startField.setValidator(self.lineEdit_integerValidator)

        self.rename_paddingNumber = QLabel('Padding:')
        self.rename_paddingNumber.setAlignment(QtCore.Qt.AlignRight)
        self.rename_paddingField = QLineEdit('')
        self.rename_paddingField.setValidator(self.lineEdit_integerValidator)
        self.rename_renameButton = QPushButton('Rename and Number')

        self.rename_groupBox = QGroupBox('Rename Tools')
        self.rename_layout = QGridLayout(self.rename_groupBox)
        self.rename_layout.setColumnStretch(1, 50)
        self.rename_layout.setColumnMinimumWidth(1, 50)
        self.rename_layout.setVerticalSpacing(4)

        self.rename_layout.addWidget(self.rename_searchFieldLabel, 1, 0, 0)
        self.rename_layout.addWidget(self.rename_searchField, 1, 1, 0)
        self.rename_layout.addWidget(self.rename_replaceFieldLabel, 2, 0, 0)
        self.rename_layout.addWidget(self.rename_replaceField, 2, 1, 0)
        self.rename_layout.addWidget(self.rename_searchReplaceButton, 3, 1, 0)
        self.rename_layout.addWidget(self.rename_prefixLabel, 5, 0, 0)
        self.rename_layout.addWidget(self.rename_prefixField, 5, 1, 0)
        self.rename_layout.addWidget(self.rename_prefixButton, 6, 1, 0)
        self.rename_layout.addWidget(self.rename_suffixLabel, 8, 0, 0)
        self.rename_layout.addWidget(self.rename_suffixField, 8, 1, 0)
        self.rename_layout.addWidget(self.rename_suffixButton, 9, 1, 0)
        self.rename_layout.addWidget(self.rename_renameLabel, 11, 0, 0)
        self.rename_layout.addWidget(self.rename_renameField, 11, 1, 0)
        self.rename_layout.addWidget(self.rename_startNumber, 12, 0, 0)
        self.rename_layout.addWidget(self.rename_startField, 12, 1, 0)
        self.rename_layout.addWidget(self.rename_paddingNumber, 13, 0, 0)
        self.rename_layout.addWidget(self.rename_paddingField, 13, 1, 0)
        self.rename_layout.addWidget(self.rename_renameButton, 14, 1, 0)

    def _createIcons(self):
        self.squareIcon = QtCore.QSize(16, 16)
        self.aIcon = QIcon()
        self.aIcon.addFile('a.png')

    def _createControlsLayout(self):
        self.controls_groupBox = QGroupBox('Controls')
        self.controls_layout = QVBoxLayout(self.controls_groupBox)
        self.controls_groupBox.setAlignment(QtCore.Qt.AlignRight)

        self.controlName_label = QLabel('Name')
        self.controlName_field = QLineEdit('')

        self.controls_label = QLabel('Type')
        self.controls_comboBox = QComboBox()
        self.controls_comboBox.addItem('Circle')
        self.controls_comboBox.addItem('Square')
        self.controls_comboBox.addItem('Cube')

        self.createOffsetButton = QPushButton('Offset')

        self.controls_gridTopLayout = QGridLayout()

        self.controls_gridTopLayout.setColumnStretch(1, 50)
        self.controls_gridTopLayout.setColumnMinimumWidth(1, 50)
        self.controls_gridTopLayout.addWidget(self.controlName_label)
        self.controls_gridTopLayout.addWidget(self.controlName_field)

        self.controls_gridTopLayout.addWidget(self.controls_label)
        self.controls_gridTopLayout.addWidget(self.controls_comboBox)

        self.controls_layout.addLayout(self.controls_gridTopLayout)

        self.constraintTypeLayout = QHBoxLayout()
        self.control_makeWithOffsets = QCheckBox('Offsets')


        self.constraint_label = QLabel('Constraint Type: ')
        self.control_pointConst = QRadioButton('Point')
        self.control_orientConst = QRadioButton('Orient')
        self.control_parentConst = QRadioButton('Parent')
        self.control_scaleConst = QCheckBox('Scale')

        self.control_createButton = QPushButton('Create')

        self.constraintTypeLayout.addStretch(True)


        self.controls_layout.addWidget(self.control_makeWithOffsets)

        self.constraintTypeLayout.addWidget(self.constraint_label)
        self.constraintTypeLayout.addWidget(self.control_pointConst)
        self.constraintTypeLayout.addWidget(self.control_orientConst)
        self.constraintTypeLayout.addWidget(self.control_parentConst)
        self.constraintTypeLayout.addWidget(self.control_scaleConst)

        self.controls_layout.addLayout(self.constraintTypeLayout)
        self.controls_layout.addWidget(self.control_createButton)

        self.coloring_groupBox = QGroupBox('Editing')
        self.coloring_layout = QVBoxLayout(self.coloring_groupBox)

        self.coloringGridlayout = QGridLayout()

        self.button_blue = QPushButton()
        self.button_red = QPushButton()
        self.green_button = QPushButton()
        self.yellow_button = QPushButton()
        self.teal_button = QPushButton()
        self.white_button = QPushButton()
        self.black_button = QPushButton()
        self.orange_button = QPushButton()
        self.pink_button = QPushButton()
        self.gray_button = QPushButton()
        self.darkgray_button = QPushButton()

        # The slider is movable by the keyboard
        self.scale_label = QLabel('Scale')
        self.control_scaleSlider = QSlider(QtCore.Qt.Horizontal)
        self.control_scaleSlider.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.scale_layout = QHBoxLayout()
        self.coloring_layout.addLayout(self.scale_layout)
        self.scale_layout.addWidget(self.scale_label)
        self.scale_layout.addWidget(self.control_scaleSlider)
        self.coloring_layout.addLayout(self.coloringGridlayout)

        self.coloringGridlayout.setSpacing(0)
        self.coloringGridlayout.addWidget(self.button_blue, 0, 0, 0)
        self.coloringGridlayout.addWidget(self.button_red, 0, 1, 0)
        self.coloringGridlayout.addWidget(self.green_button, 0, 2, 0)
        self.coloringGridlayout.addWidget(self.yellow_button, 0, 3, 0)
        self.coloringGridlayout.addWidget(self.teal_button, 0, 4, 0)
        self.coloringGridlayout.addWidget(self.white_button, 0, 5, 0)
        self.coloringGridlayout.addWidget(self.black_button, 0, 6, 0)
        self.coloringGridlayout.addWidget(self.orange_button, 0, 7, 0)
        self.coloringGridlayout.addWidget(self.pink_button, 0, 8, 0)
        self.coloringGridlayout.addWidget(self.gray_button, 0, 9, 0)
        self.coloringGridlayout.addWidget(self.darkgray_button, 1, 0, 0)

        self.button_blue.setStyleSheet('QPushButton {background-color: #A3C1DA;}')
        self.button_red.setStyleSheet('QPushButton {background-color:#FDFDFD}')
        self.white_button.setStyleSheet('QPushButton {background-color:#FFFFFF}')
        self.black_button.setStyleSheet('QPushButton {background-color:#000000}')
        self.gray_button.setStyleSheet('QPushButton {background-color:C3C3C3')

    def _createRiggingLayout(self):
        self.jointOrient_groupBox = QGroupBox('Joint Orients')
        self.jointOrient_masterLayout = QVBoxLayout(self.jointOrient_groupBox)

        self.jointOrient_layout = QHBoxLayout()
        self.jointOrient_layout.setStretch(1, 100)
        self.jointOrient_masterLayout.addLayout(self.jointOrient_layout)

        self.jointOrient_showHideLayout = QVBoxLayout()
        self.jointOrient_mainLayout = QVBoxLayout()
        self.jointOrient_layout.addLayout(self.jointOrient_showHideLayout)
        self.jointOrient_layout.addLayout(self.jointOrient_mainLayout)

        self.jointOrient_showAxisSelButton = QPushButton('Show Selected Axis')
        self.jointOrient_hideAxisSelButton = QPushButton('Hide Selected Axis')
        self.jointOrient_showAxisAllButton = QPushButton('Show All Axis')
        self.jointOrient_hideAxisAllButton = QPushButton('Hide All Axis')

        self.jointOrient_showHideLayout.addWidget(self.jointOrient_showAxisSelButton)
        self.jointOrient_showHideLayout.addWidget(self.jointOrient_hideAxisSelButton)
        self.jointOrient_showHideLayout.addWidget(self.jointOrient_showAxisAllButton)
        self.jointOrient_showHideLayout.addWidget(self.jointOrient_hideAxisAllButton)

        self.jointOrient_aimLayout = QHBoxLayout()
        self.jointOrient_aimAxisLabel = QLabel('Aim Axis:')
        self.jointOrient_aimXRadio = QRadioButton('X')
        self.jointOrient_aimYRadio = QRadioButton('Y')
        self.jointOrient_aimZRadio = QRadioButton('Z')
        self.jointOrient_aimReverseCheck = QCheckBox('Reverse')

        self.jointOrient_aimLayout.addWidget(self.jointOrient_aimAxisLabel)
        self.jointOrient_aimLayout.addWidget(self.jointOrient_aimXRadio)
        self.jointOrient_aimLayout.addWidget(self.jointOrient_aimYRadio)
        self.jointOrient_aimLayout.addWidget(self.jointOrient_aimZRadio)
        self.jointOrient_aimLayout.addWidget(self.jointOrient_aimReverseCheck)

        self.jointOrient_upAxisLayout = QHBoxLayout()
        self.jointOrient_upAxisLabel = QLabel('Up Axis: ')
        self.jointOrient_upAxisXRadio = QRadioButton('X')
        self.jointOrient_upAxisYRadio = QRadioButton('Y')
        self.jointOrient_upAxisZRadio = QRadioButton('Z')
        self.jointOrient_upReverseCheck = QCheckBox('Reverse')

        self.jointOrient_upAxisLayout.addWidget(self.jointOrient_upAxisLabel)
        self.jointOrient_upAxisLayout.addWidget(self.jointOrient_upAxisXRadio)
        self.jointOrient_upAxisLayout.addWidget(self.jointOrient_upAxisYRadio)
        self.jointOrient_upAxisLayout.addWidget(self.jointOrient_upAxisZRadio)
        self.jointOrient_upAxisLayout.addWidget(self.jointOrient_upReverseCheck)

        self.jointOrient_worldUpLayout = QHBoxLayout()
        self.jointOrient_worldUpLayout.setSpacing(0)
        self.jointOrient_worldUpLabel = QLabel('World:')
        self.jointOrient_worldUpXField = QLineEdit('0.0')
        self.jointOrient_worldUpYField = QLineEdit('1.0')
        self.jointOrient_worldUpZField = QLineEdit('0.0')

        self.jointOrient_worldUpXButton = QPushButton('X')
        self.jointOrient_worldUpYButton = QPushButton('Y')
        self.jointOrient_worldUpZButton = QPushButton('Z')

        self.jointOrient_worldUpXButton.setFixedWidth(20)
        self.jointOrient_worldUpYButton.setFixedWidth(20)
        self.jointOrient_worldUpZButton.setFixedWidth(20)

        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpLabel)
        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpXField)
        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpYField)
        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpZField)

        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpXButton)
        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpYButton)
        self.jointOrient_worldUpLayout.addWidget(self.jointOrient_worldUpZButton)

        self.jointOrient_mainLayout.addLayout(self.jointOrient_aimLayout)
        self.jointOrient_mainLayout.addLayout(self.jointOrient_upAxisLayout)
        self.jointOrient_mainLayout.addLayout(self.jointOrient_worldUpLayout)

        self.jointOrient_orientJointsButton = QPushButton('Orient Joints')
        self.jointOrient_mainLayout.addWidget(self.jointOrient_orientJointsButton)

        self.jointOrient_tweakGroupBox = QGroupBox('Tweak')
        self.jointOrient_tweakGroupBox.setFlat(True)
        self.jointOrient_tweakLayout = QHBoxLayout(self.jointOrient_tweakGroupBox)

        self.jointOrient_tweakXField = QLineEdit('0.0')
        self.jointOrient_tweakYField = QLineEdit('0.0')
        self.jointOrient_tweakZField = QLineEdit('0.0')
        self.jointOrient_zeroPushButton = QPushButton('0')
        self.jointOrient_zeroPushButton.setFixedWidth(20)

        self.jointOrient_tweakNegative = QPushButton('-')
        self.jointOrient_tweakPositive = QPushButton('+')
        self.jointOrient_tweakNegative.setFixedWidth(20)
        self.jointOrient_tweakPositive.setFixedWidth(20)

        self.jointOrient_tweakLayout.addWidget(self.jointOrient_zeroPushButton)
        self.jointOrient_tweakLayout.addWidget(self.jointOrient_tweakXField)
        self.jointOrient_tweakLayout.addWidget(self.jointOrient_tweakYField)
        self.jointOrient_tweakLayout.addWidget(self.jointOrient_tweakZField)
        self.jointOrient_tweakLayout.addWidget(self.jointOrient_tweakNegative)
        self.jointOrient_tweakLayout.addWidget(self.jointOrient_tweakPositive)

        self.jointOrient_masterLayout.addWidget(self.jointOrient_tweakGroupBox)

        self.joints_groupBox = QGroupBox('Joint Splitter')
        self.joints_layout = QVBoxLayout(self.joints_groupBox)

        self.vfk_groupBox = QGroupBox('Variable FK')
        self.vfk_layout = QVBoxLayout(self.vfk_groupBox)

        self.editJoints_groupBox = QGroupBox('Edit Joints')
        self.editJoints_layout = QVBoxLayout(self.editJoints_groupBox)


    def _createMirrorObjLayout(self):
        self.mirrorObjGroupBox = QGroupBox('Mirror Objs')
        self.mirrorObj_mainLayout = QVBoxLayout(self.mirrorObjGroupBox)
        self.mirrorObj_selObj_text = QLineEdit('')
        self.mirrorObj_updateButton = QPushButton('Update Selection')
        self.mirrorObj_mirrorButton = QPushButton('Mirror Selected Objects')

        self.mirrorObj_axisLabel = QLabel('Axis to mirror across')
        self.mirrorObj_x_rb = QRadioButton('X', self)
        self.mirrorObj_y_rb = QRadioButton('Y', self)
        self.mirrorObj_z_rb = QRadioButton('Z', self)
        self.mirrorObj_x_rb.setChecked(True)

        self.mirrorObj_searchLabel = QLabel('Search for:')
        self.mirrorObj_searchText = QLineEdit("_l_")
        self.mirrorObj_replaceLabel = QLabel('Replace with:')
        self.mirrorObj_replaceText = QLineEdit('_r_')

        self.mirrorObj_transCheck = QCheckBox('Translate')
        self.mirrorObj_rotCheck = QCheckBox('Rotate')
        self.mirrorObj_scaleCheck = QCheckBox('Scale')
        self.mirrorObj_transCheck.setChecked(True)

        self.mirrorObj_xyzLayout = QHBoxLayout()
        self.mirrorObj_xyzLayout.addWidget(self.mirrorObj_x_rb)
        self.mirrorObj_xyzLayout.addWidget(self.mirrorObj_y_rb)
        self.mirrorObj_xyzLayout.addWidget(self.mirrorObj_z_rb)

        self.mirrorObj_selectedLayout = QHBoxLayout()
        self.mirrorObj_selectedLayout.addWidget(self.mirrorObj_selObj_text)
        self.mirrorObj_selectedLayout.addWidget(self.mirrorObj_updateButton)

        self.mirrorObj_searchLayout = QHBoxLayout()
        self.mirrorObj_searchLayout.addWidget(self.mirrorObj_searchLabel)
        self.mirrorObj_searchLayout.addWidget(self.mirrorObj_searchText)
        self.mirrorObj_searchLayout.addWidget(self.mirrorObj_replaceLabel)
        self.mirrorObj_searchLayout.addWidget(self.mirrorObj_replaceText)

        self.mirrorObj_tranLayout = QHBoxLayout()
        self.mirrorObj_tranLayout.addWidget(self.mirrorObj_transCheck)
        self.mirrorObj_tranLayout.addWidget(self.mirrorObj_rotCheck)
        self.mirrorObj_tranLayout.addWidget(self.mirrorObj_scaleCheck)

        self.mirrorObj_mainLayout.addLayout(self.mirrorObj_selectedLayout)
        self.mirrorObj_mainLayout.addLayout(self.mirrorObj_searchLayout)
        self.mirrorObj_mainLayout.addLayout(self.mirrorObj_tranLayout)
        self.mirrorObj_mainLayout.addLayout(self.mirrorObj_xyzLayout)
        self.mirrorObj_mainLayout.addWidget(self.mirrorObj_mirrorButton)

    def _layout(self):

        # =====================
        # Create all UI layouts
        # =====================
        # Create Icons first
        self._createIcons()

        self._createRenamerUI()
        self._createSecondUI()
        self._createConstraintsLayout()
        self._createControlsLayout()
        self._createMirrorObjLayout()
        self._createRiggingLayout()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)

        self.riggingToolsWidget = QWidget()
        self.riggingToolsLayout = QVBoxLayout(self.riggingToolsWidget)

        self.controlToolsWidget = QWidget()
        self.controlToolsLayout = QVBoxLayout(self.controlToolsWidget)
        self.controlToolsLayout.addWidget(self.controls_groupBox)
        self.controlToolsLayout.addWidget(self.coloring_groupBox)

        self.attrToolsWidget = QWidget()
        self.attrToolsLayout = QVBoxLayout(self.attrToolsWidget)

        self.outlinerWidget = QWidget()
        self.outlinerLayout = QVBoxLayout(self.outlinerWidget)

        self.extraWidget = QWidget()
        self.extraLayout = QVBoxLayout(self.extraWidget)

        self.operationToolsWidget = QWidget()
        self.operationToolsLayout = QVBoxLayout(self.operationToolsWidget)

        self.operationToolsLayout.addWidget(self.rename_groupBox)
        self.operationToolsLayout.addWidget(self.mirrorObjGroupBox)
        self.operationToolsLayout.addWidget(self.customHierarchiesBox)
        self.operationToolsLayout.addWidget(self.constraintsBox)

        self.riggingToolsLayout.addWidget(self.joints_groupBox)
        self.riggingToolsLayout.addWidget(self.jointOrient_groupBox)

        self.riggingToolsLayout.addWidget(self.editJoints_groupBox)
        self.riggingToolsLayout.addWidget(self.vfk_groupBox)

        self.tab_layout = QTabWidget()
        self.tab_layout.addTab(self.operationToolsWidget, 'Operations')
        self.tab_layout.addTab(self.controlToolsWidget, 'Controls')
        self.tab_layout.addTab(self.riggingToolsWidget, 'Rigging')
        self.tab_layout.addTab(self.attrToolsWidget, 'Attributes')
        self.tab_layout.addTab(self.outlinerWidget, 'Outliner')

        self.main_layout.addWidget(self.tab_layout)
        self.setLayout(self.main_layout)

try:
    awToolsUI.deleteLater()
except:
    pass
awToolsUI = AWTools_UI()

try:
    awToolsUI.start()
    awToolsUI.show()
except:
    awToolsUI.deleteLater()
    print(traceback.format_exc())

