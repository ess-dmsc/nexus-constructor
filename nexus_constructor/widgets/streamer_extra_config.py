from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QHeaderView,
    QTableWidget,
    QFrame,
    QCheckBox,
    QVBoxLayout,
)
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.widgets.data_type_dropdown_list import DataTypeDropDown
from PySide2.QtCore import Signal
from nexus_constructor.array_dataset_table_widget import ValueDelegate
from nexus_constructor.widgets.unit_line_edit import UnitLineEdit
from nexus_constructor.widgets.chunk_cue_edit import ChunkCueEdit
from nexus_constructor.widgets.array_size import ArraySizeEdit


def add_line(layout):
    line = QFrame()
    line.setFrameShape(QFrame.VLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)


class F142ExtraConfig(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setLayout(QVBoxLayout())
        self._unit_type_layout = QHBoxLayout()
        self._unit_type_layout.addWidget(QLabel("Value units"))
        self._unit_edit = UnitLineEdit(self, container)
        self._unit_type_layout.addWidget(self._unit_edit)
        add_line(self._unit_type_layout)
        self._unit_type_layout.addWidget(QLabel("Data type"))
        self._value_type_combo = DataTypeDropDown(self, container)
        self._unit_type_layout.addWidget(self._value_type_combo)
        self.layout().addLayout(self._unit_type_layout)
        self._array_size_edit = ArraySizeEdit(self, container)
        self.layout().addWidget(self._array_size_edit)
        self._chunk_cue_edit = ChunkCueEdit(self, container)
        self.layout().addWidget(self._chunk_cue_edit)

        self._unit_edit.is_valid.connect(self.is_valid.emit)

    def check_validity(self):
        self._unit_edit.validator().validate(self._unit_edit.text(), 0)

    is_valid = Signal(bool)


class Ev42ExtraConfig(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setLayout(QHBoxLayout())
        self._adc_debug_check_box = QCheckBox(parent=self, text="ADC debug")
        self.layout().addWidget(self._adc_debug_check_box)
        add_line(self.layout())
        self._chunk_cue_edit = ChunkCueEdit(self, container)
        self.layout().addWidget(self._chunk_cue_edit)

    def check_validity(self):
        pass

    is_valid = Signal(bool)


class ADArExtraConfig(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QLabel("Array size"))

        self.array_size_table = QTableWidget(1, 3)
        self.array_size_table.setHorizontalHeaderLabels(["x", "y", "z"])
        self.array_size_table.setVerticalHeaderLabels([""])
        table_height = self.array_size_table.sizeHintForRow(
            0
        ) + self.array_size_table.sizeHintForRow(1)
        self.array_size_table.setMaximumHeight(table_height)
        # self.array_size_table.setFrameStyle(QFrame.NoFrame)
        self.array_size_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.array_size_table.resizeColumnsToContents()
        self.array_size_table.resizeRowsToContents()
        self.array_size_table.setItemDelegate(ValueDelegate(int, self.array_size_table))
        self.layout().addWidget(self.array_size_table)

    def check_validity(self):
        pass

    is_valid = Signal(bool)
