from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QQuaternion, QVector3D
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QTreeView,
    QWidget,
)

from nexus_constructor.common_attrs import TransformationType
from nexus_constructor.component_tree_model import NexusTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.instrument_view.instrument_view import InstrumentView
from nexus_constructor.model.model import Model
from nexus_constructor.treeview_utils import (
    add_transformation,
    create_and_add_toolbar_action,
    expand_transformation_list,
    set_button_states,
)
from ui.parameters_widget import ParametersView


class RenderSettingsTab(QWidget):
    def __init__(self, scene_widget: InstrumentView, parent=None):
        super().__init__()
        self.setParent(parent)
        self.renderSettingsLayout = QGridLayout()
        self.sceneWidget = scene_widget


        ### Default material settings: color, ambient, diffuse, hoover

        ### Other material settings ???? : color, ambient, diffuse, hoover

        ### Render full geometry QPushButton (may take time or crash program)

        ### Save simplified data  QCheckBox

        ### Triangle picking or boundingbox picking




        self.switchMeshesBtn = QPushButton("Switch")
        self.switchMeshesBtn.clicked.connect(self.sceneWidget.update_meshes)

        self.renderSettingsLayout.addWidget(self.switchMeshesBtn, 0, 0)


        #
        # self.positionVector_label = QLabel("Camera position")
        # self.positionVector_x_dsb = QDoubleSpinBox()
        #
        #
        # self.viewCenterVector_label = QLabel("View center")
        # self.viewCenterVector_x_dsb = QDoubleSpinBox()
        #
        #
        # self.fieldOfView_label = QLabel("Field of view")
        # self.fieldOfView_dsb = QDoubleSpinBox()
        #
        #
        # self.apply_btn = QPushButton("Apply")
        # self.apply_btn.clicked.connect(self.update_current_values)
        #
        #
        #
        # self.cameraSettingsLayout.addWidget(self.positionVector_label, 0, 0)



        self.setLayout(self.renderSettingsLayout)























