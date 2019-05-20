# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'componentdetails.ui',
# licensing of 'componentdetails.ui' applies.
#
# Created: Mon May 20 07:44:07 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ComponentDetailsDialog(object):
    def setupUi(self, ComponentDetailsDialog):
        ComponentDetailsDialog.setObjectName("ComponentDetailsDialog")
        ComponentDetailsDialog.resize(732, 738)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ComponentDetailsDialog.sizePolicy().hasHeightForWidth())
        ComponentDetailsDialog.setSizePolicy(sizePolicy)
        self.formLayoutWidget = QtWidgets.QWidget(ComponentDetailsDialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 0, 711, 731))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.componentNameField = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.componentNameField.setObjectName("componentNameField")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.componentNameField)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.DescriptionField = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.DescriptionField.setObjectName("DescriptionField")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.DescriptionField)
        self.TransformsBox = QtWidgets.QGroupBox(self.formLayoutWidget)
        self.TransformsBox.setMinimumSize(QtCore.QSize(0, 100))
        self.TransformsBox.setObjectName("TransformsBox")
        self.listView = QtWidgets.QListView(self.TransformsBox)
        self.listView.setGeometry(QtCore.QRect(0, 20, 711, 81))
        self.listView.setObjectName("listView")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.TransformsBox)
        self.GeometryFileBox = QtWidgets.QGroupBox(self.formLayoutWidget)
        self.GeometryFileBox.setMinimumSize(QtCore.QSize(0, 50))
        self.GeometryFileBox.setObjectName("GeometryFileBox")
        self.geometryfileform = QtWidgets.QLineEdit(self.GeometryFileBox)
        self.geometryfileform.setEnabled(True)
        self.geometryfileform.setGeometry(QtCore.QRect(0, 20, 561, 21))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geometryfileform.sizePolicy().hasHeightForWidth())
        self.geometryfileform.setSizePolicy(sizePolicy)
        self.geometryfileform.setMinimumSize(QtCore.QSize(400, 0))
        self.geometryfileform.setObjectName("geometryfileform")
        self.geometryfilebrowse = QtWidgets.QPushButton(self.GeometryFileBox)
        self.geometryfilebrowse.setEnabled(True)
        self.geometryfilebrowse.setGeometry(QtCore.QRect(569, 20, 141, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geometryfilebrowse.sizePolicy().hasHeightForWidth())
        self.geometryfilebrowse.setSizePolicy(sizePolicy)
        self.geometryfilebrowse.setMaximumSize(QtCore.QSize(300, 200))
        self.geometryfilebrowse.setObjectName("geometryfilebrowse")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.GeometryFileBox)
        self.CylinderGeometryBox = QtWidgets.QGroupBox(self.formLayoutWidget)
        self.CylinderGeometryBox.setObjectName("CylinderGeometryBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.SpanningRole, self.CylinderGeometryBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.formLayoutWidget)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.groupBox = QtWidgets.QGroupBox(self.formLayoutWidget)
        self.groupBox.setObjectName("groupBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.groupBox)

        self.retranslateUi(ComponentDetailsDialog)
        QtCore.QMetaObject.connectSlotsByName(ComponentDetailsDialog)

    def retranslateUi(self, ComponentDetailsDialog):
        ComponentDetailsDialog.setWindowTitle(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Component details", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Name: ", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Description: ", None, -1))
        self.TransformsBox.setTitle(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Transforms:", None, -1))
        self.GeometryFileBox.setTitle(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Geometry file:", None, -1))
        self.geometryfilebrowse.setText(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Browse", None, -1))
        self.CylinderGeometryBox.setTitle(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Cylinder Geometry:", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("ComponentDetailsDialog", "Pixel Data:", None, -1))

