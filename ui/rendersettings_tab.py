from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget

from nexus_constructor.instrument_view.instrument_view import InstrumentView


class RenderSettingsTab(QWidget):
    def __init__(self, scene_widget: InstrumentView, parent=None):
        super().__init__()
        self.setParent(parent)
        self.renderSettingsLayout = QGridLayout()
        self.sceneWidget = scene_widget
        # Default material settings: color, ambient, diffuse, hoover
        # Other material settings ???? : color, ambient, diffuse, hoover
        # Render full geometry QPushButton (may take time or crash program)
        # Save simplified data  QCheckBox
        # Triangle picking or boundingbox picking
        self.switchMeshesBtn = QPushButton("Switch")
        self.switchMeshesBtn.clicked.connect(self.sceneWidget.update_meshes)
        self.renderSettingsLayout.addWidget(self.switchMeshesBtn, 0, 0)
        self.setLayout(self.renderSettingsLayout)
