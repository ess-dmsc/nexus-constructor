from PySide6 import QtCore, QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

from nexus_constructor.model import GroupContainer
from nexus_constructor.widgets import ClassDropDownList, GroupNameEdit


class Ui_AddComponentDialog(QWidget):
    def __init__(self, parent: QtWidgets.QWidget, container: GroupContainer):
        super().__init__(parent)
        self._group_container = container

    def setGroupContainer(self, container: GroupContainer):
        self._group_container = container

    def setupUi(self):
        self.setObjectName("AddComponentDialog")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
#        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QtWidgets.QGridLayout(self)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.buttonLayout.addSpacerItem(
            QtWidgets.QSpacerItem(0, 0, hData=QtWidgets.QSizePolicy.Expanding)
        )
        self.ok_button = QtWidgets.QPushButton(self)
        self.ok_button.setText("Done")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ok_button.sizePolicy().hasHeightForWidth())
        self.ok_button.setSizePolicy(sizePolicy)
        self.ok_button.setMinimumSize(QtCore.QSize(104, 23))
        self.ok_button.setMaximumSize(QtCore.QSize(200, 16777215))
        self.ok_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ok_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ok_button.setAutoDefault(True)
        self.ok_button.setDefault(True)
        self.ok_button.setObjectName("buttonBox")
        self.buttonLayout.addWidget(self.ok_button)

        self.cancel_button = QtWidgets.QPushButton(self)
        self.cancel_button.setText("Cancel")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ok_button.sizePolicy().hasHeightForWidth())
        self.cancel_button.setSizePolicy(sizePolicy)
        self.cancel_button.setMinimumSize(QtCore.QSize(104, 23))
        self.cancel_button.setMaximumSize(QtCore.QSize(200, 16777215))
        self.cancel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancel_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setObjectName("cancelButton")
        self.buttonLayout.addWidget(self.cancel_button)
        self.cancel_button.setVisible(False)
        self.gridLayout_3.addLayout(self.buttonLayout, 1, 0, 1, 1)

        self.widget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
#        sizePolicy.setHorizontalStretch(1)
#        sizePolicy.setVerticalStretch(1)
#        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.nameLineEdit = GroupNameEdit(self.widget, self._group_container)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.horizontalLayout_5.addWidget(self.nameLineEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.placeholder_checkbox = QtWidgets.QCheckBox("Use placeholder")
        self.placeholder_checkbox.setObjectName("placeholder_checkbox")
        self.horizontalLayout_4.addWidget(self.placeholder_checkbox)
        self.placeholder_checkbox.setVisible(False)
        self.placeholder_checkbox.setChecked(False)
        self.componentTypeComboBox = ClassDropDownList(
            self.widget, self._group_container
        )
        self.componentTypeComboBox.setObjectName("componentTypeComboBox")
        self.horizontalLayout_4.addWidget(self.componentTypeComboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.shapeTypeBox = QtWidgets.QGroupBox(self.widget)
        self.shapeTypeBox.setObjectName("shapeTypeBox")
        self.shapeTypeBox.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.shapeTypeBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.noShapeRadioButton = QtWidgets.QRadioButton(self.shapeTypeBox)
        self.noShapeRadioButton.setObjectName("noShapeRadioButton")
        self.horizontalLayout.addWidget(self.noShapeRadioButton)
        self.boxRadioButton = QtWidgets.QRadioButton(self.shapeTypeBox)
        self.boxRadioButton.setObjectName("boxRadioButton")
        self.horizontalLayout.addWidget(self.boxRadioButton)
        self.meshRadioButton = QtWidgets.QRadioButton(self.shapeTypeBox)
        self.meshRadioButton.setObjectName("meshRadioButton")
        self.horizontalLayout.addWidget(self.meshRadioButton)
        self.CylinderRadioButton = QtWidgets.QRadioButton(self.shapeTypeBox)
        self.CylinderRadioButton.setObjectName("CylinderRadioButton")
        self.horizontalLayout.addWidget(self.CylinderRadioButton)
        self.verticalLayout_2.addWidget(self.shapeTypeBox)
        self.shapeOptionsBox = QtWidgets.QGroupBox(self.widget)
        self.shapeOptionsBox.setObjectName("shapeOptionsBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.shapeOptionsBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.geometryFileBox = QtWidgets.QGroupBox(self.shapeOptionsBox)
        self.geometryFileBox.setObjectName("geometryFileBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.geometryFileBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fileLineEdit = QtWidgets.QLineEdit(self.geometryFileBox)
        self.fileLineEdit.setReadOnly(True)
        self.fileLineEdit.setObjectName("fileLineEdit")
        self.horizontalLayout_2.addWidget(self.fileLineEdit)
        self.fileBrowseButton = QtWidgets.QPushButton(self.geometryFileBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.fileBrowseButton.sizePolicy().hasHeightForWidth()
        )
        self.fileBrowseButton.setSizePolicy(sizePolicy)
        self.fileBrowseButton.setMinimumSize(QtCore.QSize(80, 23))
        self.fileBrowseButton.setObjectName("fileBrowseButton")
        self.horizontalLayout_2.addWidget(self.fileBrowseButton)
        self.gridLayout_2.addWidget(self.geometryFileBox, 1, 0, 1, 1)

        # Box options.
        self.boxOptionsBox = QtWidgets.QGroupBox(self.shapeOptionsBox)
        self.boxOptionsBox.setObjectName("boxOptionsBox")
        self.gridLayout_box = QtWidgets.QGridLayout(self.boxOptionsBox)
        self.gridLayout_box.setObjectName("gridLayoutBox")
        self.boxLengthLineEdit = QtWidgets.QDoubleSpinBox(self.boxOptionsBox)
        self.boxLengthLineEdit.setMaximum(100000.0)
        self.boxLengthLineEdit.setObjectName("boxLengthLineEdit")
        self.gridLayout_box.addWidget(self.boxLengthLineEdit, 0, 1, 1, 1)
        self.boxWidthLineEdit = QtWidgets.QDoubleSpinBox(self.boxOptionsBox)
        self.boxWidthLineEdit.setMaximum(100000.0)
        self.boxWidthLineEdit.setObjectName("boxWidthLineEdit")
        self.gridLayout_box.addWidget(self.boxWidthLineEdit, 0, 3, 1, 1)
        self.boxHeightLineEdit = QtWidgets.QDoubleSpinBox(self.boxOptionsBox)
        self.boxHeightLineEdit.setMaximum(100000.0)
        self.boxHeightLineEdit.setObjectName("boxHeightLineEdit")
        self.gridLayout_box.addWidget(self.boxHeightLineEdit, 0, 5, 1, 1)
        self.gridLayout_box.setColumnStretch(1, 1)
        self.gridLayout_box.setColumnStretch(3, 1)
        self.gridLayout_box.setColumnStretch(5, 1)
        self.label_9 = QtWidgets.QLabel(self.boxOptionsBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout_box.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.boxOptionsBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout_box.addWidget(self.label_10, 0, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.boxOptionsBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout_box.addWidget(self.label_11, 0, 4, 1, 1)
        self.gridLayout_2.addWidget(self.boxOptionsBox, 1, 0, 1, 1)

        self.cylinderOptionsBox = QtWidgets.QGroupBox(self.shapeOptionsBox)
        self.cylinderOptionsBox.setObjectName("cylinderOptionsBox")
        self.gridLayout = QtWidgets.QGridLayout(self.cylinderOptionsBox)
        self.gridLayout.setObjectName("gridLayout")
        self.cylinderXLineEdit = QtWidgets.QDoubleSpinBox(self.cylinderOptionsBox)
        self.cylinderXLineEdit.setMaximum(100000.0)
        self.cylinderXLineEdit.setObjectName("cylinderXLineEdit")
        self.gridLayout.addWidget(self.cylinderXLineEdit, 2, 1, 1, 1)
        self.cylinderRadiusLineEdit = QtWidgets.QDoubleSpinBox(self.cylinderOptionsBox)
        self.cylinderRadiusLineEdit.setMaximum(100000.0)
        self.cylinderRadiusLineEdit.setObjectName("cylinderRadiusLineEdit")
        self.gridLayout.addWidget(self.cylinderRadiusLineEdit, 0, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.cylinderYLineEdit = QtWidgets.QDoubleSpinBox(self.cylinderOptionsBox)
        self.cylinderYLineEdit.setMaximum(100000.0)
        self.cylinderYLineEdit.setObjectName("cylinderYLineEdit")
        self.gridLayout.addWidget(self.cylinderYLineEdit, 2, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 4, 1, 1)
        self.cylinderHeightLineEdit = QtWidgets.QDoubleSpinBox(self.cylinderOptionsBox)
        self.cylinderHeightLineEdit.setMaximum(100000.0)
        self.cylinderHeightLineEdit.setObjectName("cylinderHeightLineEdit")
        self.gridLayout.addWidget(self.cylinderHeightLineEdit, 0, 1, 1, 1)
        self.cylinderZLineEdit = QtWidgets.QDoubleSpinBox(self.cylinderOptionsBox)
        self.cylinderZLineEdit.setMaximum(100000.0)
        self.cylinderZLineEdit.setProperty("value", 1.0)
        self.cylinderZLineEdit.setObjectName("cylinderZLineEdit")
        self.gridLayout.addWidget(self.cylinderZLineEdit, 2, 5, 1, 1)
        self.cylinderCountLabel = QtWidgets.QLabel(self.cylinderOptionsBox)
        self.cylinderCountLabel.setObjectName("cylinderCountLabel")
        self.gridLayout.addWidget(self.cylinderCountLabel, 3, 0, 1, 1)
        self.cylinderCountSpinBox = QtWidgets.QSpinBox(self.cylinderOptionsBox)
        self.cylinderCountSpinBox.setEnabled(False)
        self.cylinderCountSpinBox.setMinimum(1)
        self.cylinderCountSpinBox.setMaximum(999999999)
        self.cylinderCountSpinBox.setObjectName("cylinderCountSpinBox")
        self.gridLayout.addWidget(self.cylinderCountSpinBox, 1, 6, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(3, 1)
        self.gridLayout.setColumnStretch(5, 1)
        self.gridLayout_2.addWidget(self.cylinderOptionsBox, 3, 0, 1, 1)
        self.unitsbox = QtWidgets.QGroupBox(self.shapeOptionsBox)
        self.unitsbox.setObjectName("unitsbox")
        self.unitsLineEdit = QtWidgets.QLineEdit(self.unitsbox)
        self.unitsLineEdit.setPlaceholderText("")
        self.unitsLineEdit.setObjectName("unitsLineEdit")
        self.gridLayout_2.addWidget(self.unitsbox, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.unitsLineEdit, 1, 1, 1, 1)
        self.pixelOptionsWidget = QtWidgets.QWidget(self.shapeOptionsBox)
        self.gridLayout_2.addWidget(self.pixelOptionsWidget, 4, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.shapeOptionsBox)
        self.fieldsBox = QtWidgets.QGroupBox(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
#        sizePolicy.setHeightForWidth(self.fieldsBox.sizePolicy().hasHeightForWidth())
        self.fieldsBox.setSizePolicy(sizePolicy)
        self.fieldsBox.setMaximumHeight(50)
        self.fieldsBox.setObjectName("fieldsBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.fieldsBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.addFieldPushButton = QtWidgets.QPushButton(self.fieldsBox)
        self.addFieldPushButton.setObjectName("addFieldPushButton")
        self.gridLayout_5.addWidget(self.addFieldPushButton, 0, 0, 1, 1)
        self.removeFieldPushButton = QtWidgets.QPushButton(self.fieldsBox)
        self.removeFieldPushButton.setObjectName("removeFieldPushButton")
        self.gridLayout_5.addWidget(self.removeFieldPushButton, 0, 1, 1, 1)
        self.fieldsListWidget = QtWidgets.QListWidget(self.fieldsBox)
        self.fieldsListWidget.setObjectName("fieldsListWidget")
        self.gridLayout_5.addWidget(self.fieldsListWidget, 1, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.fieldsBox)
        self.verticalLayout_2.setStretch(5, 1)
        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 1)
        self.gridLayout_3.addWidget(self.widget, 0, 0, 1, 1)
        self.set_web_engine_view(sizePolicy)
        self.retranslateUi()
        self.nameLineEdit.setFocus()
        QtCore.QMetaObject.connectSlotsByName(self)

    def set_web_engine_view(self, sizePolicy):
        self.webEngineView = QWebEngineView(self.widget)
        # sizePolicy.setHeightForWidth(
        #     self.webEngineView.sizePolicy().hasHeightForWidth()
        # )
        self.webEngineView.setSizePolicy(sizePolicy)
        self.webEngineView.setProperty("url", QtCore.QUrl("about:blank"))
        self.webEngineView.setObjectName("webEngineView")
        self.gridLayout_4.addWidget(self.webEngineView, 0, 1, 1, 1)

    def retranslateUi(self):
        self.setWindowTitle(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Add group", None, -1
            )
        )
        self.label.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Name:", None, -1)
        )
        self.label_3.setText(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Group type:", None, -1
            )
        )
        # self.shapeTypeBox.setTitle(
        #     QtWidgets.QApplication.translate(
        #         "AddComponentDialog", "Shape type:", None, -1
        #     )
        # )
        self.noShapeRadioButton.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Auto", None, -1)
        )
        self.boxRadioButton.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Box", None, -1)
        )
        self.meshRadioButton.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Mesh", None, -1)
        )
        self.CylinderRadioButton.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Cylinder", None, -1)
        )
        # self.shapeOptionsBox.setTitle(
        #     QtWidgets.QApplication.translate(
        #         "AddComponentDialog", "Shape options:", None, -1
        #     )
        # )
        # self.geometryFileBox.setTitle(
        #     QtWidgets.QApplication.translate("AddComponentDialog", "CAD file", None, -1)
        # )
        self.fileBrowseButton.setText(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Browse...", None, -1
            )
        )
        # self.cylinderOptionsBox.setTitle(
        #     QtWidgets.QApplication.translate(
        #         "AddComponentDialog", "Cylinder options", None, -1
        #     )
        # )
        self.label_6.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "X:", None, -1)
        )
        self.label_5.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Radius", None, -1)
        )
        self.label_7.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Y:", None, -1)
        )
        self.label_4.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Height", None, -1)
        )
        self.label_8.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Z:", None, -1)
        )

        self.label_9.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Length:", None, -1)
        )
        self.label_10.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Width:", None, -1)
        )
        self.label_11.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "Height:", None, -1)
        )

        self.cylinderCountLabel.setText(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Cylinder Count:", None, -1
            )
        )
        self.unitsbox.setTitle(
            QtWidgets.QApplication.translate("AddComponentDialog", "Dimensions", None, -1)
        )
        self.unitsLineEdit.setText(
            QtWidgets.QApplication.translate("AddComponentDialog", "m", None, -1)
        )
        self.addFieldPushButton.setText(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Add field", None, -1
            )
        )
        self.removeFieldPushButton.setText(
            QtWidgets.QApplication.translate(
                "AddComponentDialog", "Remove field", None, -1
            )
        )
