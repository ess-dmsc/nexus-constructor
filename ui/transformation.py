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
    QGridLayout,
)

from nexus_constructor.field_widget import FieldWidget


class Ui_Transformation(object):
    def setupUi(self, Transformation, instrument):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)
        self.frame_layout = QVBoxLayout(Transformation)
        self.frame_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(4)

        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(-1)
        self.name_label = QLabel("Name", Transformation)
        self._make_text_bold(self.name_label)

        self.name_layout.addWidget(self.name_label)
        self.name_line_edit = QLineEdit(Transformation)

        self.name_layout.addWidget(self.name_line_edit)
        self.main_layout.addLayout(self.name_layout)

        self._add_line()

        self.vector_label = QLabel("", Transformation)
        self._make_text_bold(self.vector_label)
        self.main_layout.addWidget(self.vector_label)

        self._set_up_vector_box(Transformation)

        self._add_line()

        self.value_label = QLabel("")
        self._make_text_bold(self.value_label)
        self.main_layout.addWidget(self.value_label)

        self.magnitude_widget = FieldWidget(hide_name_field=True, instrument=instrument)
        self.magnitude_widget.setFrameShape(QFrame.NoFrame)
        self.magnitude_widget.setMinimumHeight(40)
        self.main_layout.addWidget(self.magnitude_widget)

        self.ui_placeholder_layout = QFormLayout()
        self.value_spinbox = QDoubleSpinBox(Transformation)
        self.value_spinbox.setToolTip("Placeholder value for 3D view to use")
        self.value_spinbox.setDecimals(8)
        self.value_spinbox.setMaximumSize(QSize(100, 16777215))
        self.ui_placeholder_layout.addRow(
            "Value to use in 3D view:", self.value_spinbox
        )

        self.main_layout.addLayout(self.ui_placeholder_layout)

        self.set_spinbox_ranges()

        self.frame_layout.addLayout(self.main_layout)

        self.retranslateUi(Transformation)
        QMetaObject.connectSlotsByName(Transformation)

    def _add_line(self):
        line = QFrame()
        line.setFrameShape((QFrame.HLine))
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

    @staticmethod
    def _make_text_bold(label: QLabel):
        font = label.font()
        font.setBold(True)
        label.setFont(font)

    def _set_up_vector_box(self, Transformation):
        self.xyz_layout = QHBoxLayout()

        self.x_layout = QFormLayout()
        self.x_spinbox = QDoubleSpinBox(Transformation)
        self.x_layout.addRow("x:", self.x_spinbox)
        self.xyz_layout.addLayout(self.x_layout)

        self.y_layout = QFormLayout()
        self.y_spinbox = QDoubleSpinBox(Transformation)
        self.y_layout.addRow("y:", self.y_spinbox)
        self.xyz_layout.addLayout(self.y_layout)

        self.z_layout = QFormLayout()
        self.z_spinbox = QDoubleSpinBox(Transformation)
        self.z_layout.addRow("z:", self.z_spinbox)
        self.xyz_layout.addLayout(self.z_layout)

        self.main_layout.addLayout(self.xyz_layout)

    def set_spinbox_ranges(self):
        self.spinboxes = [
            self.x_spinbox,
            self.y_spinbox,
            self.z_spinbox,
            self.value_spinbox,
        ]
        for spinbox in self.spinboxes:
            spinbox.setRange(-10000000, 10000000)
            spinbox.setDecimals(5)

    def retranslateUi(self, Transformation):
        Transformation.setWindowTitle(
            QApplication.translate("Transformation", "GroupBox", None, -1)
        )
        Transformation.setTitle(
            QApplication.translate("Transformation", "Translation", None, -1)
        )
