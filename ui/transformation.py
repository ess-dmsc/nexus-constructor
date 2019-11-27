from PySide2.QtCore import QSize, QMetaObject
from PySide2.QtWidgets import (
    QLabel,
    QFormLayout,
    QApplication,
    QDoubleSpinBox,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QVBoxLayout,
)


class Ui_Transformation(object):
    def setupUi(self, Transformation):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)
        self.frame_layout = QVBoxLayout(Transformation)
        self.frame_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(7)
        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(-1)
        self.name_label = QLabel("Name", Transformation)
        self.name_layout.addWidget(self.name_label)
        self.name_line_edit = QLineEdit(Transformation)

        self.name_layout.addWidget(self.name_line_edit)
        self.main_layout.addLayout(self.name_layout)
        self.line_1 = QFrame(Transformation)
        self.line_1.setFrameShape(QFrame.HLine)
        self.line_1.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.line_1)

        self.vector_label = QLabel("Vector", Transformation)

        self.main_layout.addWidget(self.vector_label)

        self._set_up_vector_box(Transformation)

        self.line_3 = QFrame(Transformation)
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.line_3)
        self.length_layout = QHBoxLayout()
        self.length_layout.setSpacing(-1)
        self.valueLabel = QLabel("Length", Transformation)
        self.length_layout.addWidget(self.valueLabel)
        self.value_spinbox = QDoubleSpinBox(Transformation)
        self.value_spinbox.setDecimals(8)
        self.value_spinbox.setMaximumSize(QSize(100, 16777215))
        self.length_layout.addWidget(self.value_spinbox)

        self.main_layout.addLayout(self.length_layout)
        self.frame_layout.addLayout(self.main_layout)

        self.retranslateUi(Transformation)
        QMetaObject.connectSlotsByName(Transformation)

    def _set_up_vector_box(self, Transformation):
        XYZ_MINIMUM = 0
        XYZ_MAXIMUM = 1000000
        PRECISION = 5
        self.vector_layout = QHBoxLayout()

        self.x_layout = QFormLayout()
        self.x_spinbox = QDoubleSpinBox(Transformation)
        self.x_spinbox.setRange(XYZ_MINIMUM, XYZ_MAXIMUM)
        self.x_spinbox.setDecimals(PRECISION)
        self.x_layout.addRow("x:", self.x_spinbox)
        self.vector_layout.addLayout(self.x_layout)

        self.y_layout = QFormLayout()
        self.y_spinbox = QDoubleSpinBox(Transformation)
        self.y_spinbox.setRange(XYZ_MINIMUM, XYZ_MAXIMUM)
        self.y_spinbox.setDecimals(PRECISION)
        self.y_layout.addRow("y:", self.y_spinbox)
        self.vector_layout.addLayout(self.y_layout)

        self.z_layout = QFormLayout()
        self.z_spinbox = QDoubleSpinBox(Transformation)
        self.z_spinbox.setRange(XYZ_MINIMUM, XYZ_MAXIMUM)
        self.z_spinbox.setDecimals(PRECISION)
        self.z_layout.addRow("z:", self.z_spinbox)
        self.vector_layout.addLayout(self.z_layout)

        self.main_layout.addLayout(self.vector_layout)

    def retranslateUi(self, Transformation):
        Transformation.setWindowTitle(
            QApplication.translate("Transformation", "GroupBox", None, -1)
        )
        Transformation.setTitle(
            QApplication.translate("Transformation", "Translation", None, -1)
        )
