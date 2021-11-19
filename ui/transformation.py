from typing import TYPE_CHECKING

from PySide2.QtCore import QMetaObject, QSize
from PySide2.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from nexus_constructor.field_widget import FieldWidget

if TYPE_CHECKING:
    from nexus_constructor.transformation_view import EditTransformation


class UiTransformation:
    def __init__(self, Transformation: "EditTransformation"):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(4)

        self.frame_layout = QVBoxLayout(Transformation)
        self.frame_layout.setContentsMargins(4, 4, 4, 4)

        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(-1)
        self.name_label = QLabel("Name", Transformation)
        self._make_text_bold(self.name_label)
        self.name_line_edit = QLineEdit(Transformation)

        self.vector_label = QLabel("", Transformation)
        self._make_text_bold(self.vector_label)

        self.value_label = QLabel("")
        self._make_text_bold(self.value_label)

        self.magnitude_widget = FieldWidget(
            hide_name_field=True, show_only_f142_stream=True
        )
        self.magnitude_widget.setFrameShape(QFrame.NoFrame)
        self.magnitude_widget.setMinimumHeight(40)

        self.ui_placeholder_layout = QFormLayout()

        self.value_spinbox = QDoubleSpinBox(Transformation)
        self.value_spinbox.setToolTip("Placeholder value for 3D view to use")
        self.value_spinbox.setDecimals(8)
        self.value_spinbox.setMaximumSize(QSize(100, 16777215))
        self.ui_placeholder_layout.addRow(
            "Value to use in 3D view:", self.value_spinbox
        )

        self.setupUI(Transformation)

    def setupUI(self, transformation):
        self.setup_name_layout()
        self.setup_vector_layout(transformation)
        self.setup_value_and_magnitude()
        self.set_spinbox_ranges()

        self.frame_layout.addLayout(self.main_layout)

        self.retranslate_ui(transformation)
        QMetaObject.connectSlotsByName(transformation)

    def setup_value_and_magnitude(self):
        self.main_layout.addWidget(self.value_label)
        self.main_layout.addWidget(self.magnitude_widget)
        self.main_layout.addLayout(self.ui_placeholder_layout)

    def setup_vector_layout(self, transformation):
        self.main_layout.addWidget(self.vector_label)
        self._set_up_vector_box(transformation)
        self._add_line()

    def setup_name_layout(self):
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_line_edit)
        self.main_layout.addLayout(self.name_layout)
        self._add_line()

    def _set_up_vector_box(self, transformation):
        self.xyz_layout = QHBoxLayout()

        self.x_layout = QFormLayout()
        self.x_spinbox = QDoubleSpinBox(transformation)
        self.x_layout.addRow("x:", self.x_spinbox)
        self.xyz_layout.addLayout(self.x_layout)

        self.y_layout = QFormLayout()
        self.y_spinbox = QDoubleSpinBox(transformation)
        self.y_layout.addRow("y:", self.y_spinbox)
        self.xyz_layout.addLayout(self.y_layout)

        self.z_layout = QFormLayout()
        self.z_spinbox = QDoubleSpinBox(transformation)
        self.z_layout.addRow("z:", self.z_spinbox)
        self.xyz_layout.addLayout(self.z_layout)

        self.main_layout.addLayout(self.xyz_layout)

    def _add_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

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

    @staticmethod
    def _make_text_bold(label: QLabel):
        font = label.font()
        font.setBold(True)
        label.setFont(font)

    @staticmethod
    def retranslate_ui(transformation):
        transformation.setWindowTitle(
            QApplication.translate("Transformation", "GroupBox", None, -1)
        )
        transformation.setTitle(
            QApplication.translate("Transformation", "Translation", None, -1)
        )
