from ui.transformation import Ui_Transformation
from PySide2.QtWidgets import QGroupBox

class EditTranslation(QGroupBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self)


class EditRotation(QGroupBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self)
        self.set_t
        