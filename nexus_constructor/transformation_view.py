from ui.transformation import Ui_Transformation
from PySide2.QtWidgets import QGroupBox
from nexus_constructor.transformations import TransformationModel

class EditTransformation(QGroupBox):
    def __init__(self, parent, transformation: TransformationModel):
        super().__init__(parent)
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self)
        self.transformation = transformation

class EditTranslation(EditTransformation):
    def __init__(self, parent, transformation: TransformationModel):
        super().__init__(parent, transformation)
        self.transformation_frame.valueLabel.setText("Position (m)")

class EditRotation(EditTransformation):
    def __init__(self, parent, transformation: TransformationModel):
        super().__init__(parent, transformation)
        self.transformation_frame.valueLabel.setText("Rotation (°)")