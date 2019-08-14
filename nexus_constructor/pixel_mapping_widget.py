from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QListWidget

from nexus_constructor.validators import NullableIntValidator


class PixelMappingWidget(QWidget):
    def __init__(self, parent: QListWidget, id_no: int, text: str):
        """
        A custom widget used for acting as a template in the pixel mapping list. Consists of a label and an input box.
        :param parent: The QListWidget that will contain this list item.
        :param id_no: The "temporary" ID number based on the number of faces in the mesh/number of cylinders. Used
        to distinguish elements in the list but doesn't define the actual IDs that are saved upon clicking Add Component.
        :param text: The text that appears in the list widget. Will be either "cylinder" or "face."
        """
        super().__init__(parent)
        self.pixelIDLabel = QLabel()
        self.pixelIDLineEdit = QLineEdit()

        # Create the label text based on the face number
        self.pixelIDLabel.setText("Pixel ID for " + text + " #" + str(id_no) + ":")

        # Give the line edit a validator that requires values of zero or greater
        self.pixelIDLineEdit.setValidator(NullableIntValidator(bottom=0))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.pixelIDLabel)
        self.layout.addWidget(self.pixelIDLineEdit)

        self.setLayout(self.layout)

    def get_id(self):
        """
        :return: The user-entered ID converted to an int. Returns None if the text field is empty.
        """
        text = self.pixelIDLineEdit.text()
        if text:
            return int(text)

        return None
