from PySide2.QtWidgets import QDialog, QGridLayout, QListWidget, QPushButton


class FieldAttrsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QGridLayout())

        self.list_widget = QListWidget()
        self.add_button = QPushButton("Add attr")
        self.remove_button = QPushButton("Remove attr")

        self.layout().addWidget(self.list_widget, 0, 0, 2, 1)
        self.layout().addWidget(self.add_button, 0, 1)
        self.layout().addWidget(self.remove_button, 1, 1)
