from PySide2.QtWidgets import QComboBox, QGridLayout, QLineEdit, QDialog, QSpinBox

SCHEMAS = ["ev42", "f142", "hs00", "ns10"]
types = ["double", "int"]


class StreamFieldsWidget(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.schema_combo = QComboBox()

        self.topic_line_edit = QLineEdit()
        self.source_line_edit = QLineEdit()

        self.array_size_spinbox = QSpinBox()

        self.type_combo = QComboBox()
        self.type_combo.currentTextChanged.connect(self._type_changed)

        self.schema_combo.currentTextChanged.connect(self.schema_type_changed)
        self.schema_combo.addItems(SCHEMAS)


        self.layout().addWidget(self.schema_combo)
        self.layout().addWidget(self.topic_line_edit)

        self.layout().addWidget(self.type_combo)
        self.layout().addWidget(self.array_size_spinbox)

        self.schema_type_changed(self.schema_combo.currentText())

    def schema_type_changed(self, schema):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
        if schema == "f142":
            self._set_edits_visible(True, True)
        elif schema == "ev42":
            self._set_edits_visible(False, False)
        elif schema == "hs00":
            self._set_edits_visible(False, False)
        elif schema == "ns10":
            self._set_edits_visible(False, False)

    def _set_edits_visible(self, source: bool, type: bool):
        self.source_line_edit.setVisible(source)
        self.type_combo.setVisible(type)

    def _type_changed(self, dtype):
        self.array_size_spinbox.setEnabled(dtype == "double")
