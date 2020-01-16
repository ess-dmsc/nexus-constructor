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

from nexus_constructor.field_widget import FieldWidget


class Ui_Transformation(object):
    def setupUi(self, Transformation, instrument):
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

        self.line_2 = QFrame(Transformation)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.line_2)
        self.length_layout = QHBoxLayout()
        self.length_layout.setSpacing(-1)
        self.valueLabel = QLabel("Length", Transformation)
        self.length_layout.addWidget(self.valueLabel)

        self.ui_placeholder_label = QLabel("UI placeholder:")
        self.length_layout.addWidget(self.ui_placeholder_label)

        self.value_spinbox = QDoubleSpinBox(Transformation)
        self.value_spinbox.setToolTip("Placeholder value for 3d view to use")
        self.value_spinbox.setDecimals(8)
        self.value_spinbox.setMaximumSize(QSize(100, 16777215))
        self.length_layout.addWidget(self.value_spinbox)
        self._set_up_vector_box(Transformation)

        self.magnitude_widget = FieldWidget(hide_name_field=True, instrument=instrument)
        self.main_layout.addLayout(self.length_layout)
        self.main_layout.addWidget(self.magnitude_widget)
        self.frame_layout.addLayout(self.main_layout)

        self.retranslateUi(Transformation)
        QMetaObject.connectSlotsByName(Transformation)

    def _set_up_vector_box(self, Transformation):
        self.vector_layout = QHBoxLayout()

        self.x_layout = QFormLayout()
        self.x_spinbox = QDoubleSpinBox(Transformation)
        self.x_layout.addRow("x:", self.x_spinbox)
        self.vector_layout.addLayout(self.x_layout)

        self.y_layout = QFormLayout()
        self.y_spinbox = QDoubleSpinBox(Transformation)
        self.y_layout.addRow("y:", self.y_spinbox)
        self.vector_layout.addLayout(self.y_layout)

        self.z_layout = QFormLayout()
        self.z_spinbox = QDoubleSpinBox(Transformation)
        self.z_layout.addRow("z:", self.z_spinbox)
        self.vector_layout.addLayout(self.z_layout)

        self.spinboxes = [
            self.x_spinbox,
            self.y_spinbox,
            self.z_spinbox,
            self.value_spinbox,
        ]
        for spinbox in self.spinboxes[:-1]:
            spinbox.setRange(0, 1000000)
            spinbox.setDecimals(5)

        self.main_layout.addLayout(self.vector_layout)

    def retranslateUi(self, Transformation):
        Transformation.setWindowTitle(
            QApplication.translate("Transformation", "GroupBox", None, -1)
        )
        Transformation.setTitle(
            QApplication.translate("Transformation", "Translation", None, -1)
        )
