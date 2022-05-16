from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QCheckBox
from PySide2.QtCore import Qt
from nexus_constructor.model.writer_module_container import ModuleContainer
from .positive_integer_setting import PositiveIntegerSetting


class ArraySizeEdit(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._container = container
        self.setLayout(QHBoxLayout())
        self._activate_set_array = QCheckBox(parent=self, text="Is array")
        self.layout().addWidget(self._activate_set_array)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(line)

        self._array_size_label = QLabel(self, text="Array size:")
        self.layout().addWidget(self._array_size_label)
        self._array_size_edit = PositiveIntegerSetting(self, container, "array_size")
        self.layout().addWidget(self._array_size_edit)

        current_array_size = container.module.array_size
        if current_array_size is None:
            self._array_size_edit.setEnabled(False)
            self._array_size_label.setEnabled(False)
            self._array_size_edit.setValue(0)
            self._activate_set_array.setCheckState(Qt.CheckState.Unchecked)
        else:
            self._array_size_edit.setValue(current_array_size)
            self._activate_set_array.setCheckState(Qt.CheckState.Checked)
        self._activate_set_array.stateChanged.connect(self._handle_activate_array)
        self._stored_array_size = self._array_size_edit.value()

    def _handle_activate_array(self, new_state):
        enable_state = False
        new_value = 0
        if new_state == Qt.CheckState.Checked:
            enable_state = True
            new_value = self._stored_array_size
        elif new_state == Qt.CheckState.Unchecked:
            self._stored_array_size = self._array_size_edit.value()
        self._array_size_edit.setValue(new_value)
        self._array_size_edit.setEnabled(enable_state)
        self._array_size_label.setEnabled(enable_state)
