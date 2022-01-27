from os import environ

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import (
    QAbstractItemView,
    QSizePolicy,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from nexus_constructor.common_attrs import TransformationType
from nexus_constructor.component_tree_model import ComponentTreeModel, NexusTreeModel
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


class ComponentTreeViewTab(QWidget):
    def __init__(self, scene_widget: InstrumentView, parent=None):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setParent(parent)
        self.componentsTabLayout = QVBoxLayout()
        self.component_tree_view = QTreeView()
        self.parameters_widget = ParametersView(parent)
        self.componentsTabLayout.addWidget(self.parameters_widget)
        self.componentsTabLayout.addWidget(self.component_tree_view)

        self.layout().addLayout(self.componentsTabLayout)

        self.sceneWidget = scene_widget

        self.component_tree_view.setDragEnabled(True)
        self.component_tree_view.setAcceptDrops(True)
        self.component_tree_view.setDropIndicatorShown(True)
        self.component_tree_view.header().hide()
        self.component_tree_view.updateEditorGeometries()
        self.component_tree_view.updateGeometries()
        self.component_tree_view.updateGeometry()
        self.component_tree_view.clicked.connect(self._set_button_state)
        self.component_tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.component_tool_bar = QToolBar("Actions", self)
        self.new_component_action = create_and_add_toolbar_action(
            "new_component.png",
            "Component",
            self.parent().show_add_component_window,
            self.component_tool_bar,
            self,
            True,
        )
        self.new_translation_action = create_and_add_toolbar_action(
            "new_translation.png",
            "Translation",
            lambda: self._add_transformation(TransformationType.TRANSLATION),
            self.component_tool_bar,
            self,
        )
        self.new_rotation_action = create_and_add_toolbar_action(
            "new_rotation.png",
            "Rotation",
            lambda: self._add_transformation(TransformationType.ROTATION),
            self.component_tool_bar,
            self,
        )
        self.create_link_action = create_and_add_toolbar_action(
            "create_link.png",
            "Link",
            self.on_create_link,
            self.component_tool_bar,
            self,
        )
        self.edit_component_action = create_and_add_toolbar_action(
            "edit_component.png",
            "Edit",
            self.parent().show_edit_component_dialog,
            self.component_tool_bar,
            self,
        )
        self.zoom_action = create_and_add_toolbar_action(
            "zoom.svg",
            "Zoom",
            self.on_zoom_item,
            self.component_tool_bar,
            self,
        )
        self.component_tool_bar.insertSeparator(self.zoom_action)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.component_tool_bar.addWidget(self.spacer)
        self.delete_action = create_and_add_toolbar_action(
            "delete.png", "Delete", self.on_delete_item, self.component_tool_bar, self
        )
        self.component_tool_bar.insertSeparator(self.delete_action)
        self.componentsTabLayout.insertWidget(0, self.component_tool_bar)

    def set_up_model(self, model: Model):
        if int(environ.get("USE_NEW_TREE_STRUCT", 0)):
            self.component_model = NexusTreeModel(model)
        else:
            self.component_model = ComponentTreeModel(model)
        self.component_delegate = ComponentEditorDelegate(
            self.component_tree_view, model
        )
        self.component_tree_view.setItemDelegate(self.component_delegate)
        self.component_tree_view.setModel(self.component_model)
        self.parameters_widget.set_up_model(model)

    def _set_button_state(self):
        set_button_states(
            self.component_tree_view,
            self.delete_action,
            self.new_rotation_action,
            self.new_translation_action,
            self.create_link_action,
            self.zoom_action,
            self.edit_component_action,
        )

    def on_create_link(self):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            self.component_model.add_link(selected[0])
            self._expand_transformation_list(selected[0])
            self._set_button_state()

    def _expand_transformation_list(self, node: QModelIndex):
        expand_transformation_list(node, self.component_tree_view, self.component_model)

    def _add_transformation(self, transformation_type: str):
        add_transformation(
            transformation_type, self.component_tree_view, self.component_model
        )

    def on_delete_item(self):
        selected = self.component_tree_view.selectedIndexes()
        for item in selected:
            self.component_model.remove_node(item)
        self._set_button_state()

    def on_zoom_item(self):
        selected = self.component_tree_view.selectedIndexes()[0]
        component = selected.internalPointer()
        self.sceneWidget.zoom_to_component(
            self.sceneWidget.get_entity(component.name), self.sceneWidget.view.camera()
        )
