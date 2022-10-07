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
    # def __init__(self):
    #     super().__init__()

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
            ("hoover_state", "shadows"),
            ("hoover_state", "highlights"),
        ]

        self.switchMeshesLabel = QLabel("Toggle high resolution mesh: ")
        self.switchMeshesBox = QCheckBox()
        self.switchMeshesBox.stateChanged.connect(self.sceneWidget.update_meshes)

        self.switchMeshLayout.addWidget(self.switchMeshesLabel)
        self.switchMeshLayout.addWidget(self.switchMeshesBox)

        self.normalShadowsBtn = QPushButton("")
        self.normalHighlightsBtn = QPushButton("")
        self.hooverShadowsBtn = QPushButton("")
        self.hooverHighlightsBtn = QPushButton("")
        self.normalShadowsBtn.clicked.connect(lambda: self._pick_color(0))
        self.normalHighlightsBtn.clicked.connect(lambda: self._pick_color(1))
        self.hooverShadowsBtn.clicked.connect(lambda: self._pick_color(2))
        self.hooverHighlightsBtn.clicked.connect(lambda: self._pick_color(3))

        self.material_combobox = QComboBox()
        self.material_combobox.currentIndexChanged.connect(self.updateColorBoxes)
        for key in MATERIAL_DICT.keys():
            self.material_combobox.addItem(key)

        self.colorBoxLayout.addWidget(self.normalShadowsBtn, 0, 0)
        self.colorBoxLayout.addWidget(self.normalHighlightsBtn, 0, 1)
        self.colorBoxLayout.addWidget(self.hooverShadowsBtn, 1, 0)
        self.colorBoxLayout.addWidget(self.hooverHighlightsBtn, 1, 1)

        Separador = QFrame()
        Separador.setFrameShape(QFrame.HLine)
        Separador.setLineWidth(0.01)
        Separador.setStyleSheet(
            """
            background-color: rgba(240,240,240,0);
            border-width: 1px;
            border-style: solid;
            border-color: rgba(240,240,240,0) rgba(240,240,240,0) rgba(230,230,230,1) rgba(240,240,240,0);
            border-top-style:none;
            """
        )

        self.renderSettingsLayout.addLayout(self.switchMeshLayout)
        self.renderSettingsLayout.addWidget(Separador)
        self.renderSettingsLayout.addWidget(self.material_combobox)
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
            self.hooverShadowsBtn,
            MATERIAL_DICT[self.current_material]["hoover_state"]["shadows"],
        )
        self._changeBoxColor(
            self.hooverHighlightsBtn,
            MATERIAL_DICT[self.current_material]["hoover_state"]["highlights"],
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
        # color_dialog.show()
        color_dialog.exec()

    # def _pick_color(self, component_type, shading_type):
    #     if component_type == "ground":
    #         entities = self.sceneWidget.component_entities["_ground"].entities
    #         for e in entities:
    #             for c in e.components():
    #                 if isinstance(c, Qt3DExtras.QPhongMaterial):
    #                     break
    #
    #
    #
    #         if not isinstance(c, Qt3DExtras.QPhongMaterial):
    #             return
    #         self.current_ambient = deepcopy(c.ambient())
    #         self.current_diffuse = deepcopy(c.diffuse())
    #
    #     self.color_dialog = CustomColorDialog(self)
    #     self.color_dialog.currentColorChanged.connect(lambda: self._update_color(
    #         e, c, shading_type
    #     ))
    #     self.color_dialog.show()
    #     self.color_dialog.exec()
    #     print('all the way')
    #     self.color_dialog.close()
    #
    #
    # def _update_color(self, e, c, shading_type):
    #     if shading_type == "ambient":
    #         self.current_ambient = self.color_dialog.selectedColor()
    #     elif shading_type == "diffuse":
    #         self.current_diffuse = self.color_dialog.selectedColor()
    #
    #     new_material = Qt3DExtras.QPhongMaterial(
    #         ambient = self.current_ambient,
    #         diffuse = self.current_diffuse,
    #     )
    #
    #     e.removeComponent(c)
    #     e.addComponent(new_material)
