from typing import TYPE_CHECKING
from functools import partial

from PySide6.QtCore import QMetaObject, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QSizePolicy
)

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.ui_utils import validate_line_edit
from nexus_constructor.validators import UnitValidator
from nexus_constructor.unit_utils import METRES

if TYPE_CHECKING:
    from nexus_constructor.transformation_view import EditTransformation


class UiTransformation:
    def __init__(self, Transformation: "EditTransformation"):
        Transformation.setObjectName("Transformation")
        Transformation.resize(361, 171)
        self.setup_ui(Transformation)

    def setup_ui(self, transformation):
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(4)

        self.frame_layout = QVBoxLayout(transformation)
        self.frame_layout.setContentsMargins(4, 4, 4, 4)

        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(-1)
        self.name_label = QLabel("Name", transformation)
        self._make_text_bold(self.name_label)
        self.name_line_edit = QLineEdit(transformation)

        self.vector_label = QLabel("", transformation)
        self._make_text_bold(self.vector_label)

        self.value_label = QLabel("")
        self._make_text_bold(self.value_label)

        self.magnitude_widget = FieldWidget(
            node_parent=transformation.transformation_parent,
            hide_name_field=True,
            show_only_f142_stream=True,
        )
        self.magnitude_widget.field_type_combo.setMaximumWidth(0)
        self.magnitude_widget.value_type_combo.setMaximumWidth(0)
        self.magnitude_widget.attrs_button.setMaximumWidth(0)
        self.magnitude_widget.setFrameShape(QFrame.NoFrame)
        self.magnitude_widget.setMinimumHeight(40)

        self.ui_placeholder_layout = QVBoxLayout()

        offset_font = QFont()
        offset_font.setBold(True)
        self.offset_label = QLabel("Offset")
        self.offset_label.setFont(offset_font)
        self.offset_line_edit = QLineEdit(transformation)

        self.depends_on_text_box = QLineEdit(transformation)
        self.depends_on_text_box.setToolTip("depends_on for transformation.")
        self.depends_on_text_box.setMaximumSize(QSize(3000, 16777215))
        self.depends_on_text_box.setMinimumWidth(250)
        depends_on_font = QFont()
        depends_on_font.setBold(True)
        depends_on_label = QLabel("depends_on")
        depends_on_label.setFont(depends_on_font)
        self.ui_placeholder_layout.addWidget(depends_on_label)
        self.ui_placeholder_layout.addWidget(self.depends_on_text_box)

        self.setup_name_layout()
        self.setup_vector_layout(transformation)
        self.setup_offset_layout(transformation)
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

    def setup_offset_layout(self, transformation):
        self.main_layout.addWidget(self.offset_label)
        self._set_up_vector_box_offset(transformation)
        self.offset_units_line_edit = QLineEdit()
        self.offset_unit_validator = UnitValidator(expected_dimensionality=METRES)
        self.offset_units_line_edit.setValidator(self.offset_unit_validator)
        self.offset_units_line_edit.setMinimumWidth(20)
        offset_unit_size_policy = QSizePolicy()
        offset_unit_size_policy.setHorizontalPolicy(QSizePolicy.Preferred)
        offset_unit_size_policy.setHorizontalStretch(1)
        self.offset_units_line_edit.setSizePolicy(offset_unit_size_policy)
        self.offset_units_line_edit.setText("m")
        self.offset_unit_validator.is_valid.connect(
            partial(validate_line_edit, self.offset_units_line_edit)
        )
        self.offset_units_line_edit.setPlaceholderText(CommonAttrs.UNITS)
        self.main_layout.addWidget(self.offset_units_line_edit)
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

    def _set_up_vector_box_offset(self, transformation):
        self.xyz_layout_offset = QHBoxLayout()

        self.x_layout_offset = QFormLayout()
        self.x_spinbox_offset = QDoubleSpinBox(transformation)
        self.x_layout_offset.addRow("x:", self.x_spinbox_offset)
        self.xyz_layout_offset.addLayout(self.x_layout_offset)

        self.y_layout_offset = QFormLayout()
        self.y_spinbox_offset = QDoubleSpinBox(transformation)
        self.y_layout_offset.addRow("y:", self.y_spinbox_offset)
        self.xyz_layout_offset.addLayout(self.y_layout_offset)

        self.z_layout_offset = QFormLayout()
        self.z_spinbox_offset = QDoubleSpinBox(transformation)
        self.z_layout_offset.addRow("z:", self.z_spinbox_offset)
        self.xyz_layout_offset.addLayout(self.z_layout_offset)

        self.main_layout.addLayout(self.xyz_layout_offset)

    def _add_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

    def set_spinbox_ranges(self):
        self.spinboxes = [
            self.x_spinbox,
            self.y_spinbox,
            self.z_spinbox
        ]
        self.offset_spinboxes = [
            self.x_spinbox_offset,
            self.y_spinbox_offset,
            self.z_spinbox_offset,
        ]
        for spinbox in self.spinboxes + self.offset_spinboxes:
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
