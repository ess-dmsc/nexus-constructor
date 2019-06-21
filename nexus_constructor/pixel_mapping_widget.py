from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout
from nexus_constructor.validators import NullableIntValidator


class PixelMappingWidget(QWidget):
    def __init__(self, parent, face_no):
        super().__init__(parent)
        self.pixelIDLabel = QLabel()
        self.pixelIDLineEdit = QLineEdit()

        self.pixelIDLabel.setText("Pixel ID for face #" + str(face_no) + ":")
        self.pixelIDLineEdit.setValidator(NullableIntValidator())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.pixelIDLabel)
        self.layout.addWidget(self.pixelIDLineEdit)

        self.setLayout(self.layout)
