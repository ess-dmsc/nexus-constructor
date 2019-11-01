from PySide2 import QtCore, QtWidgets


class Ui_Transformation(object):
    def setupUi(self, Transformation):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)
        self.frame_layout = QtWidgets.QVBoxLayout(Transformation)
        self.frame_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(7)
        self.name_layout = QtWidgets.QHBoxLayout()
        self.name_layout.setSpacing(-1)
        self.name_label = QtWidgets.QLabel("Name", Transformation)
        self.name_layout.addWidget(self.name_label)
        self.name_line_edit = QtWidgets.QLineEdit(Transformation)

        self.name_layout.addWidget(self.name_line_edit)
        self.main_layout.addLayout(self.name_layout)
        self.line_1 = QtWidgets.QFrame(Transformation)
        self.line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(self.line_1)

        self.vector_label = QtWidgets.QLabel("Vector", Transformation)

        self.main_layout.addWidget(self.vector_label)

        self._set_up_vector_box(Transformation)

        self.line_3 = QtWidgets.QFrame(Transformation)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(self.line_3)
        self.length_layout = QtWidgets.QHBoxLayout()
        self.length_layout.setSpacing(-1)
        self.valueLabel = QtWidgets.QLabel("Length", Transformation)
        self.length_layout.addWidget(self.valueLabel)
        self.valueSpinBox = QtWidgets.QDoubleSpinBox(Transformation)
        self.valueSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.length_layout.addWidget(self.valueSpinBox)

        self.main_layout.addLayout(self.length_layout)
        self.frame_layout.addLayout(self.main_layout)

        self.retranslateUi(Transformation)
        QtCore.QMetaObject.connectSlotsByName(Transformation)

    def _set_up_vector_box(self, Transformation):
        self.vectorLayout = QtWidgets.QFormLayout()
        self.vectorLayout.setObjectName("vectorLayout")
        self.xSpinBox = QtWidgets.QDoubleSpinBox(Transformation)
        self.xSpinBox.setMinimum(0)
        self.xSpinBox.setMaximum(360)
        self.xSpinBox.setObjectName("xSpinBox")
        self.vectorLayout.addRow("x:", self.xSpinBox)
        self.ySpinBox = QtWidgets.QDoubleSpinBox(Transformation)
        self.ySpinBox.setObjectName("ySpinBox")
        self.ySpinBox.setMinimum(0)
        self.ySpinBox.setMaximum(360)
        self.vectorLayout.addRow("y:", self.ySpinBox)
        self.zSpinBox = QtWidgets.QDoubleSpinBox(Transformation)
        self.zSpinBox.setObjectName("zSpinBox")
        self.zSpinBox.setMinimum(0)
        self.zSpinBox.setMaximum(360)
        self.vectorLayout.addRow("z:", self.zSpinBox)

        self.main_layout.addLayout(self.vectorLayout)

    def retranslateUi(self, Transformation):
        Transformation.setWindowTitle(
            QtWidgets.QApplication.translate("Transformation", "GroupBox", None, -1)
        )
        Transformation.setTitle(
            QtWidgets.QApplication.translate("Transformation", "Translation", None, -1)
        )
