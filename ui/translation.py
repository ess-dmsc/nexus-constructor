# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'translation.ui',
# licensing of 'translation.ui' applies.
#
# Created: Wed Jul  3 10:39:01 2019
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Translation(object):
    def setupUi(self, Translation):
        Translation.setObjectName("Translation")
        Translation.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Translation)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.setObjectName("nameLayout")
        self.nameLabel = QtWidgets.QLabel(Translation)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(Translation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameLineEdit.sizePolicy().hasHeightForWidth())
        self.nameLineEdit.setSizePolicy(sizePolicy)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLayout.addWidget(self.nameLineEdit)
        self.mainLayout.addLayout(self.nameLayout)
        self.line = QtWidgets.QFrame(Translation)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.mainLayout.addWidget(self.line)
        self.vectorLabel = QtWidgets.QLabel(Translation)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vectorLabel.sizePolicy().hasHeightForWidth())
        self.vectorLabel.setSizePolicy(sizePolicy)
        self.vectorLabel.setObjectName("vectorLabel")
        self.mainLayout.addWidget(self.vectorLabel)
        self.vectorLayout = QtWidgets.QHBoxLayout()
        self.vectorLayout.setObjectName("vectorLayout")
        self.xPosLabel = QtWidgets.QLabel(Translation)
        self.xPosLabel.setObjectName("xPosLabel")
        self.vectorLayout.addWidget(self.xPosLabel)
        self.xLineEdit = QtWidgets.QLineEdit(Translation)
        self.xLineEdit.setObjectName("xLineEdit")
        self.vectorLayout.addWidget(self.xLineEdit)
        self.yPosLabel = QtWidgets.QLabel(Translation)
        self.yPosLabel.setObjectName("yPosLabel")
        self.vectorLayout.addWidget(self.yPosLabel)
        self.yLineEdit = QtWidgets.QLineEdit(Translation)
        self.yLineEdit.setObjectName("yLineEdit")
        self.vectorLayout.addWidget(self.yLineEdit)
        self.zPosLabel = QtWidgets.QLabel(Translation)
        self.zPosLabel.setObjectName("zPosLabel")
        self.vectorLayout.addWidget(self.zPosLabel)
        self.zLineEdit = QtWidgets.QLineEdit(Translation)
        self.zLineEdit.setObjectName("zLineEdit")
        self.vectorLayout.addWidget(self.zLineEdit)
        self.mainLayout.addLayout(self.vectorLayout)
        self.lengthLayout = QtWidgets.QHBoxLayout()
        self.lengthLayout.setObjectName("lengthLayout")
        self.lengthLabel = QtWidgets.QLabel(Translation)
        self.lengthLabel.setObjectName("lengthLabel")
        self.lengthLayout.addWidget(self.lengthLabel)
        self.lengthLineEdit = QtWidgets.QLineEdit(Translation)
        self.lengthLineEdit.setObjectName("lengthLineEdit")
        self.lengthLayout.addWidget(self.lengthLineEdit)
        self.mainLayout.addLayout(self.lengthLayout)
        self.verticalLayout_2.addLayout(self.mainLayout)

        self.retranslateUi(Translation)
        QtCore.QMetaObject.connectSlotsByName(Translation)

    def retranslateUi(self, Translation):
        Translation.setWindowTitle(QtWidgets.QApplication.translate("Translation", "GroupBox", None, -1))
        Translation.setTitle(QtWidgets.QApplication.translate("Translation", "Translation", None, -1))
        self.nameLabel.setText(QtWidgets.QApplication.translate("Translation", "Name", None, -1))
        self.vectorLabel.setText(QtWidgets.QApplication.translate("Translation", "Vector", None, -1))
        self.xPosLabel.setText(QtWidgets.QApplication.translate("Translation", "x", None, -1))
        self.yPosLabel.setText(QtWidgets.QApplication.translate("Translation", "y", None, -1))
        self.zPosLabel.setText(QtWidgets.QApplication.translate("Translation", "z", None, -1))
        self.lengthLabel.setText(QtWidgets.QApplication.translate("Translation", "Length", None, -1))

