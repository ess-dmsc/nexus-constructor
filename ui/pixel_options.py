# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/pixel_options.ui',
# licensing of 'ui/pixel_options.ui' applies.
#
# Created: Wed Aug 14 09:30:56 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_PixelOptionsWidget(object):
    def setupUi(self, PixelOptionsWidget):
        PixelOptionsWidget.setObjectName("PixelOptionsWidget")
        PixelOptionsWidget.resize(560, 403)

        PixelOptionsWidget.setMinimumSize(QtCore.QSize(560, 20))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(PixelOptionsWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pixelOptionsBox = QtWidgets.QGroupBox(PixelOptionsWidget)

        self.pixelOptionsBox.setMinimumSize(QtCore.QSize(0, 20))
        self.pixelOptionsBox.setObjectName("pixelOptionsBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.pixelOptionsBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pixelLayoutBox = QtWidgets.QGroupBox(self.pixelOptionsBox)
        self.pixelLayoutBox.setMinimumSize(QtCore.QSize(0, 63))
        self.pixelLayoutBox.setObjectName("pixelLayoutBox")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.pixelLayoutBox)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.singlePixelRadioButton = QtWidgets.QRadioButton(self.pixelLayoutBox)
        self.singlePixelRadioButton.setChecked(True)
        self.singlePixelRadioButton.setObjectName("singlePixelRadioButton")
        self.horizontalLayout_7.addWidget(self.singlePixelRadioButton)
        self.entireShapeRadioButton = QtWidgets.QRadioButton(self.pixelLayoutBox)
        self.entireShapeRadioButton.setObjectName("entireShapeRadioButton")
        self.horizontalLayout_7.addWidget(self.entireShapeRadioButton)
        self.noPixelsButton = QtWidgets.QRadioButton(self.pixelLayoutBox)
        self.noPixelsButton.setObjectName("noPixelsButton")
        self.horizontalLayout_7.addWidget(self.noPixelsButton)
        self.verticalLayout_3.addWidget(self.pixelLayoutBox)
        self.pixelOptionsStack = QtWidgets.QStackedWidget(self.pixelOptionsBox)
        self.pixelOptionsStack.setMinimumSize(QtCore.QSize(518, 192))
        self.pixelOptionsStack.setObjectName("pixelOptionsStack")
        self.pixelGridPage = QtWidgets.QWidget()
        self.pixelGridPage.setObjectName("pixelGridPage")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.pixelGridPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pixelGridBox = QtWidgets.QGroupBox(self.pixelGridPage)
        self.pixelGridBox.setObjectName("pixelGridBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.pixelGridBox)
        self.gridLayout_5.setVerticalSpacing(6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.rowLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.rowLabel.setObjectName("rowLabel")
        self.gridLayout_5.addWidget(self.rowLabel, 0, 0, 1, 1)
        self.rowHeightLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.rowHeightLabel.setObjectName("rowHeightLabel")
        self.gridLayout_5.addWidget(self.rowHeightLabel, 0, 2, 1, 1)
        self.columnWidthLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.columnWidthLabel.setObjectName("columnWidthLabel")
        self.gridLayout_5.addWidget(self.columnWidthLabel, 1, 2, 1, 1)
        self.firstIDLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.firstIDLabel.setObjectName("firstIDLabel")
        self.gridLayout_5.addWidget(self.firstIDLabel, 2, 0, 1, 1)
        self.columnsLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.columnsLabel.setObjectName("columnsLabel")
        self.gridLayout_5.addWidget(self.columnsLabel, 1, 0, 1, 1)
        self.countFirstLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.countFirstLabel.setObjectName("countFirstLabel")
        self.gridLayout_5.addWidget(self.countFirstLabel, 4, 0, 1, 2)
        self.countingFromLabel = QtWidgets.QLabel(self.pixelGridBox)
        self.countingFromLabel.setObjectName("countingFromLabel")
        self.gridLayout_5.addWidget(self.countingFromLabel, 3, 0, 1, 2)
        self.startCountingComboBox = QtWidgets.QComboBox(self.pixelGridBox)
        self.startCountingComboBox.setMaxCount(4)
        self.startCountingComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        self.startCountingComboBox.setObjectName("startCountingComboBox")
        self.startCountingComboBox.addItem("")
        self.startCountingComboBox.addItem("")
        self.startCountingComboBox.addItem("")
        self.startCountingComboBox.addItem("")
        self.gridLayout_5.addWidget(self.startCountingComboBox, 3, 2, 1, 2)
        self.countFirstComboBox = QtWidgets.QComboBox(self.pixelGridBox)
        self.countFirstComboBox.setCurrentText("")
        self.countFirstComboBox.setMaxCount(2)
        self.countFirstComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        self.countFirstComboBox.setObjectName("countFirstComboBox")
        self.gridLayout_5.addWidget(self.countFirstComboBox, 4, 2, 1, 2)
        self.rowCountSpinBox = QtWidgets.QSpinBox(self.pixelGridBox)
        self.rowCountSpinBox.setMinimum(1)
        self.rowCountSpinBox.setMaximum(1000000)
        self.rowCountSpinBox.setProperty("value", 1)
        self.rowCountSpinBox.setObjectName("rowCountSpinBox")
        self.gridLayout_5.addWidget(self.rowCountSpinBox, 0, 1, 1, 1)
        self.columnCountSpinBox = QtWidgets.QSpinBox(self.pixelGridBox)
        self.columnCountSpinBox.setMinimum(1)
        self.columnCountSpinBox.setMaximum(1000000)
        self.columnCountSpinBox.setProperty("value", 1)
        self.columnCountSpinBox.setObjectName("columnCountSpinBox")
        self.gridLayout_5.addWidget(self.columnCountSpinBox, 1, 1, 1, 1)
        self.firstIDSpinBox = QtWidgets.QSpinBox(self.pixelGridBox)
        self.firstIDSpinBox.setMaximum(1000000)
        self.firstIDSpinBox.setObjectName("firstIDSpinBox")
        self.gridLayout_5.addWidget(self.firstIDSpinBox, 2, 1, 1, 1)
        self.rowHeightSpinBox = QtWidgets.QDoubleSpinBox(self.pixelGridBox)
        self.rowHeightSpinBox.setMinimum(0.1)
        self.rowHeightSpinBox.setSingleStep(0.1)
        self.rowHeightSpinBox.setProperty("value", 0.5)
        self.rowHeightSpinBox.setObjectName("rowHeightSpinBox")
        self.gridLayout_5.addWidget(self.rowHeightSpinBox, 0, 3, 1, 1)
        self.columnWidthSpinBox = QtWidgets.QDoubleSpinBox(self.pixelGridBox)
        self.columnWidthSpinBox.setMinimum(0.1)
        self.columnWidthSpinBox.setSingleStep(0.1)
        self.columnWidthSpinBox.setProperty("value", 0.5)
        self.columnWidthSpinBox.setObjectName("columnWidthSpinBox")
        self.gridLayout_5.addWidget(self.columnWidthSpinBox, 1, 3, 1, 1)
        self.verticalLayout.addWidget(self.pixelGridBox)
        self.pixelOptionsStack.addWidget(self.pixelGridPage)
        self.pixelMappingPage = QtWidgets.QWidget()
        self.pixelMappingPage.setObjectName("pixelMappingPage")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.pixelMappingPage)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pixelMappingLabel = QtWidgets.QLabel(self.pixelMappingPage)
        self.pixelMappingLabel.setObjectName("pixelMappingLabel")
        self.verticalLayout_4.addWidget(self.pixelMappingLabel)
        self.pixelMappingListWidget = QtWidgets.QListWidget(self.pixelMappingPage)
        self.pixelMappingListWidget.setObjectName("pixelMappingListWidget")
        self.verticalLayout_4.addWidget(self.pixelMappingListWidget)
        self.pixelOptionsStack.addWidget(self.pixelMappingPage)
        self.verticalLayout_3.addWidget(self.pixelOptionsStack)
        self.verticalLayout_2.addWidget(self.pixelOptionsBox)

        self.retranslateUi(PixelOptionsWidget)
        self.pixelOptionsStack.setCurrentIndex(0)
        self.countFirstComboBox.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(PixelOptionsWidget)

    def retranslateUi(self, PixelOptionsWidget):
        PixelOptionsWidget.setWindowTitle(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Form", None, -1)
        )
        self.pixelOptionsBox.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel options", None, -1
            )
        )
        self.pixelLayoutBox.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel layout:", None, -1
            )
        )
        self.singlePixelRadioButton.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape describes each identical pixel in the detector",
                None,
                -1,
            )
        )
        self.singlePixelRadioButton.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Repeated Single Pixel Shape", None, -1
            )
        )
        self.entireShapeRadioButton.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape describes the shape of the entire detector",
                None,
                -1,
            )
        )
        self.entireShapeRadioButton.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Entire Shape", None, -1
            )
        )
        self.noPixelsButton.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape does not define the shape of the detector pixels",
                None,
                -1,
            )
        )
        self.noPixelsButton.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "No Pixels", None, -1
            )
        )
        self.pixelGridBox.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel grid:", None, -1
            )
        )
        self.rowLabel.setText(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Row:", None, -1)
        )
        self.rowHeightLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Row height:", None, -1
            )
        )
        self.columnWidthLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Column width:", None, -1
            )
        )
        self.firstIDLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "First ID:", None, -1
            )
        )
        self.columnsLabel.setText(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Columns:", None, -1)
        )
        self.countFirstLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Count first along:", None, -1
            )
        )
        self.countingFromLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Start counting from:", None, -1
            )
        )
        self.startCountingComboBox.setItemText(
            0,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Bottom Left", None, -1
            ),
        )
        self.startCountingComboBox.setItemText(
            1,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Bottom Right", None, -1
            ),
        )
        self.startCountingComboBox.setItemText(
            2,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Top Left", None, -1
            ),
        )
        self.startCountingComboBox.setItemText(
            3,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Top Right", None, -1
            ),
        )
        self.pixelMappingLabel.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel mapping:", None, -1
            )
        )
