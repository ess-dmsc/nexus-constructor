from PySide2.QtWidgets import QComboBox, QGridLayout, QLineEdit, QDialog, QSpinBox

SCHEMAS = ["ev42", "f142", "hs00", "ns10"]
types = ["double", "int"]


class StreamFieldsWidget(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.schema_combo = QComboBox()
        self.schema_combo.currentTextChanged.connect(self.schema_type_changed)
        self.schema_combo.addItems(SCHEMAS)
        self.topic_line_edit = QLineEdit()
        self.source_line_edit = QLineEdit()

        self.type_combo = QComboBox()
        self.type_combo.currentTextChanged.connect(self._type_changed)

        self.array_size_spinbox = QSpinBox()

        self.layout().addWidget(self.schema_combo)
        self.layout().addWidget(self.topic_line_edit)

        self.schema_type_changed(self.schema_combo.currentText())

    def schema_type_changed(self, schema):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        if schema == "f142":
            self._set_edits_enabled(True, True)

    def _set_edits_enabled(self, source: bool, type: bool):
        self.source_line_edit.setEnabled(source)
        self.type_combo.setEnabled(type)

    def _type_changed(self, dtype):
        self.array_size_spinbox.setEnabled(dtype == "double")
