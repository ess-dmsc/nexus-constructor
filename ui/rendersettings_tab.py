from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nexus_constructor.instrument_view.instrument_view import InstrumentView
from nexus_constructor.instrument_view.qentity_utils import MATERIAL_DICT


class CustomColorDialog(QColorDialog):
    def closeEvent(self, *args, **kwargs):
        super(QColorDialog, self).closeEvent(*args, **kwargs)


class RenderSettingsTab(QWidget):
    def __init__(self, scene_widget: InstrumentView, parent=None):
        super().__init__()
        self.setParent(parent)
        self.renderSettingsLayout = QVBoxLayout()
        self.switchMeshLayout = QHBoxLayout()
        self.colorBoxLayout = QGridLayout()
        self.sceneWidget = scene_widget
        self.boxTypeTuples = [
            ("normal_state", "shadows"),
            ("normal_state", "highlights"),
            ("hover_state", "shadows"),
            ("hover_state", "highlights"),
        ]

        self.subTitle_1 = QLabel("Mesh Settings")

        self.switchMeshesLabel = QLabel("Toggle high resolution mesh: ")
        self.switchMeshesBox = QCheckBox()
        self.switchMeshesBox.stateChanged.connect(self.sceneWidget.update_meshes)

        self.switchMeshLayout.addWidget(self.switchMeshesLabel)
        self.switchMeshLayout.addWidget(self.switchMeshesBox)

        self.normalShadowsLabel = QLabel("Shadows")
        self.normalHighlightsLabel = QLabel("Highlights")
        self.hoverShadowsLabel = QLabel("Hover Shadows")
        self.hoverHighlightsLabel = QLabel("Hover Highlights")

        self.normalShadowsBtn = QPushButton("")
        self.normalHighlightsBtn = QPushButton("")
        self.hoverShadowsBtn = QPushButton("")
        self.hoverHighlightsBtn = QPushButton("")
        self.normalShadowsBtn.clicked.connect(lambda: self._pick_color(0))
        self.normalHighlightsBtn.clicked.connect(lambda: self._pick_color(1))
        self.hoverShadowsBtn.clicked.connect(lambda: self._pick_color(2))
        self.hoverHighlightsBtn.clicked.connect(lambda: self._pick_color(3))

        self.subTitle_2 = QLabel("Material Color Settings")

        self.material_combobox = QComboBox()
        self.material_combobox.currentIndexChanged.connect(self.updateColorBoxes)
        for key in MATERIAL_DICT.keys():
            self.material_combobox.addItem(key)

        self.colorBoxLayout.addWidget(self.normalShadowsLabel, 0, 0)
        self.colorBoxLayout.addWidget(self.normalHighlightsLabel, 0, 1)
        self.colorBoxLayout.addWidget(self.hoverShadowsLabel, 2, 0)
        self.colorBoxLayout.addWidget(self.hoverHighlightsLabel, 2, 1)

        self.colorBoxLayout.addWidget(self.normalShadowsBtn, 1, 0)
        self.colorBoxLayout.addWidget(self.normalHighlightsBtn, 1, 1)
        self.colorBoxLayout.addWidget(self.hoverShadowsBtn, 3, 0)
        self.colorBoxLayout.addWidget(self.hoverHighlightsBtn, 3, 1)

        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.HLine)
        separator_line.setLineWidth(0.01)
        separator_line.setStyleSheet(
            """
            background-color: rgba(240,240,240,0);
            border-width: 1px;
            border-style: solid;
            border-color: rgba(240,240,240,0) rgba(240,240,240,0) rgba(230,230,230,1) rgba(240,240,240,0);
            border-top-style:none;
            """
        )

        subtitle_font = QFont("Arial", 11, QFont.Bold)
        self.subTitle_1.setFont(subtitle_font)
        self.subTitle_2.setFont(subtitle_font)

        self.renderSettingsLayout.setAlignment(Qt.AlignTop)
        self.switchMeshLayout.setAlignment(Qt.AlignTop)
        self.colorBoxLayout.setAlignment(Qt.AlignTop)

        self.renderSettingsLayout.addWidget(self.subTitle_1, alignment=Qt.AlignTop)
        self.renderSettingsLayout.addLayout(self.switchMeshLayout)
        self.renderSettingsLayout.addWidget(separator_line, alignment=Qt.AlignTop)
        self.renderSettingsLayout.addWidget(self.subTitle_2, alignment=Qt.AlignTop)
        self.renderSettingsLayout.addWidget(
            self.material_combobox, alignment=Qt.AlignTop
        )
        self.renderSettingsLayout.addLayout(self.colorBoxLayout)

        self.setLayout(self.renderSettingsLayout)
        self.updateColorBoxes()

    def _changeBoxColor(self, box, color):
        box.setAutoFillBackground(True)
        box.setStyleSheet("background-color: {}; border: none;".format(color.name()))

    def updateColorBoxes(self):
        self.current_material = self.material_combobox.currentText()
        self._changeBoxColor(
            self.normalShadowsBtn,
            MATERIAL_DICT[self.current_material]["normal_state"]["shadows"],
        )
        self._changeBoxColor(
            self.normalHighlightsBtn,
            MATERIAL_DICT[self.current_material]["normal_state"]["highlights"],
        )
        self._changeBoxColor(
            self.hoverShadowsBtn,
            MATERIAL_DICT[self.current_material]["hover_state"]["shadows"],
        )
        self._changeBoxColor(
            self.hoverHighlightsBtn,
            MATERIAL_DICT[self.current_material]["hover_state"]["highlights"],
        )

    def setMaterialColor(self, color_state, color_type, new_color):
        MATERIAL_DICT[self.current_material][color_state][color_type] = new_color
        self.updateColorBoxes()
        self.sceneWidget.updateRenderedMaterials(self.current_material, color_state)

    def _pick_color(self, box_idx):
        color_state, color_type = self.boxTypeTuples[box_idx]
        color_dialog = CustomColorDialog(self)
        color_dialog.setCurrentColor(
            MATERIAL_DICT[self.current_material][color_state][color_type]
        )
        color_dialog.currentColorChanged.connect(
            lambda: self.setMaterialColor(
                color_state, color_type, color_dialog.currentColor()
            )
        )
        color_dialog.exec()
