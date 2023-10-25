from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)


class ParametersView(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.model = None
        self.setLayout(QVBoxLayout())
        self.setParent(parent)