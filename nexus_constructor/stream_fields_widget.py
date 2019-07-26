from PySide2.QtWidgets import QComboBox, QGridLayout, QLineEdit, QDialog

SCHEMAS = ["ev42", "f142", "hs00", ""]


class StreamFieldsWidget(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setLayout(QGridLayout())
        self.schema_combo = QComboBox()
        self.schema_combo.currentTextChanged.connect(self.schema_type_changed)
        self.schema_combo.addItems(SCHEMAS)
        self.topic_line_edit = QLineEdit()

        self.layout().addWidget(self.schema_combo)
        self.layout().addWidget(self.topic_line_edit)

        self.schema_type_changed(self.schema_combo.currentText())

    def schema_type_changed(self, schema):
        self.parent().setWindowTitle(f"Editing {schema} stream field")
