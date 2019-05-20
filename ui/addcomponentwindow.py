# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addcomponentwindow.ui',
# licensing of 'addcomponentwindow.ui' applies.
#
# Created: Mon May 20 07:43:52 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_AddComponentDialog(object):
    def setupUi(self, AddComponentDialog):
        AddComponentDialog.setObjectName("AddComponentDialog")
        AddComponentDialog.resize(232, 139)
        self.formLayout_2 = QtWidgets.QFormLayout(AddComponentDialog)
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.ComponentTypeComboBox = QtWidgets.QComboBox(AddComponentDialog)
        self.ComponentTypeComboBox.setEditable(False)
        self.ComponentTypeComboBox.setMaxVisibleItems(40)
        self.ComponentTypeComboBox.setObjectName("ComponentTypeComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ComponentTypeComboBox)
        self.label_2 = QtWidgets.QLabel(AddComponentDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.GeometryTypeComboBox = QtWidgets.QComboBox(AddComponentDialog)
        self.GeometryTypeComboBox.setObjectName("GeometryTypeComboBox")
        self.GeometryTypeComboBox.addItem("")
        self.GeometryTypeComboBox.addItem("")
        self.GeometryTypeComboBox.addItem("")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.GeometryTypeComboBox)
        self.PixelTypeComboBox = QtWidgets.QComboBox(AddComponentDialog)
        self.PixelTypeComboBox.setObjectName("PixelTypeComboBox")
        self.PixelTypeComboBox.addItem("")
        self.PixelTypeComboBox.addItem("")
        self.PixelTypeComboBox.addItem("")
        self.PixelTypeComboBox.addItem("")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.PixelTypeComboBox)
        self.label_3 = QtWidgets.QLabel(AddComponentDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label = QtWidgets.QLabel(AddComponentDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.line = QtWidgets.QFrame(AddComponentDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.line)
        self.line_2 = QtWidgets.QFrame(AddComponentDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.line_2)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddComponentDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(AddComponentDialog)
        self.ComponentTypeComboBox.setCurrentIndex(-1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddComponentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddComponentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddComponentDialog)

    def retranslateUi(self, AddComponentDialog):
        AddComponentDialog.setWindowTitle(QtWidgets.QApplication.translate("AddComponentDialog", "Add Component", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("AddComponentDialog", "Geometry type: ", None, -1))
        self.GeometryTypeComboBox.setItemText(0, QtWidgets.QApplication.translate("AddComponentDialog", "Mesh", None, -1))
        self.GeometryTypeComboBox.setItemText(1, QtWidgets.QApplication.translate("AddComponentDialog", "Cylinder", None, -1))
        self.GeometryTypeComboBox.setItemText(2, QtWidgets.QApplication.translate("AddComponentDialog", "None", None, -1))
        self.PixelTypeComboBox.setItemText(0, QtWidgets.QApplication.translate("AddComponentDialog", "Single ID", None, -1))
        self.PixelTypeComboBox.setItemText(1, QtWidgets.QApplication.translate("AddComponentDialog", "Repeatable Grid", None, -1))
        self.PixelTypeComboBox.setItemText(2, QtWidgets.QApplication.translate("AddComponentDialog", "Face Mapped Mesh", None, -1))
        self.PixelTypeComboBox.setItemText(3, QtWidgets.QApplication.translate("AddComponentDialog", "None", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("AddComponentDialog", "Pixel Type: ", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("AddComponentDialog", "Component Type: ", None, -1))

