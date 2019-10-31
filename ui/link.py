# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'link.ui',
# licensing of 'link.ui' applies.
#
# Created: Sun Jul  7 13:10:23 2019
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Link(object):
    def setupUi(self, Link):
        Link.setObjectName("Link")
        Link.resize(406, 96)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Link)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.groupBox = QtWidgets.QGroupBox(Link)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.boxLayout = QtWidgets.QVBoxLayout()
        self.boxLayout.setObjectName("boxLayout")
        self.firstRowLayout = QtWidgets.QHBoxLayout()
        self.firstRowLayout.setObjectName("firstRowLayout")
        self.selectLinkLayout = QtWidgets.QVBoxLayout()
        self.selectLinkLayout.setObjectName("selectLinkLayout")
        self.selectLinkLabel = QtWidgets.QLabel(self.groupBox)
        self.selectLinkLabel.setObjectName("selectLinkLabel")
        self.selectLinkLayout.addWidget(self.selectLinkLabel)
        self.TransformationsComboBox = QtWidgets.QComboBox(self.groupBox)
        self.TransformationsComboBox.setObjectName("TransformationsComboBox")
        self.selectLinkLayout.addWidget(self.TransformationsComboBox)
        self.firstRowLayout.addLayout(self.selectLinkLayout)
        self.boxLayout.addLayout(self.firstRowLayout)
        self.verticalLayout_4.addLayout(self.boxLayout)
        self.mainLayout.addWidget(self.groupBox)
        self.verticalLayout_2.addLayout(self.mainLayout)

        self.retranslateUi(Link)
        QtCore.QMetaObject.connectSlotsByName(Link)

    def retranslateUi(self, Link):
        Link.setWindowTitle(QtWidgets.QApplication.translate("Link", "Frame", None, -1))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("Link", "Link", None, -1))
        self.selectLinkLabel.setText(QtWidgets.QApplication.translate("Link", "Select component", None, -1))

