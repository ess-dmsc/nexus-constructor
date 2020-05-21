import os
import sys

from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QAction, QToolBar, QWidget, QTreeView, QLabel

from nexus_constructor.component.link_transformation import LinkTransformation
from nexus_constructor.component.transformations_list import TransformationsList
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.model.component import Component
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.transformation_view import (
    EditTransformationLink,
    EditTranslation,
    EditRotation,
)

# We have to use this for cx freeze as __file__ does not work
if getattr(sys, "frozen", False):
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")


def create_and_add_toolbar_action(
    icon_path: str,
    mouse_over_text: str,
    trigger_method: classmethod,
    component_tool_bar: QToolBar,
    component_tree_view_tab: QWidget,
    set_enabled: bool = False,
) -> QAction:
    """
    Create a QAction and add it to the component toolbar.
    :param icon_path: The location of the action icon relative to the "ui" folder.
    :param mouse_over_text: The text that should appear when the mouse is above the icon.
    :param trigger_method: The method that should be called when the icon is clicked.
    :param component_tool_bar: The tool bad that the action is added to.
    :param component_tree_view_tab: The tab for the component tree view.
    :param set_enabled: A bool indicating whether or not the action should be enabled immediately after it's been
        created. Only needs to be true for the Add Component button.
    :return The new QAction.
    """
    toolbar_action = QAction(
        QIcon(os.path.join(root_dir, "ui", icon_path)),
        mouse_over_text,
        component_tree_view_tab,
    )
    toolbar_action.triggered.connect(trigger_method)
    toolbar_action.setEnabled(set_enabled)
    component_tool_bar.addAction(toolbar_action)
    return toolbar_action


def set_button_states(
    component_tree_view: QTreeView,
    delete_action: QAction,
    duplicate_action: QAction,
    new_rotation_action: QAction,
    new_translation_action: QAction,
    create_link_action: QAction,
    zoom_action: QAction,
    edit_component_action: QAction,
):
    """
    Changes the button states based on user interaction with the component tree view.
    :param component_tree_view: The component tree view.
    :param delete_action: The action for deleting an item.
    :param duplicate_action: The action for duplicating an item.
    :param new_rotation_action: The action for creating a new rotation.
    :param new_translation_action: The action for creating a new translation.
    :param create_link_action: The action for creating a link.
    :param zoom_action: The action for zooming on a component.
    :param edit_component_action: The action for editing a component.
    """
    selection_indices = component_tree_view.selectedIndexes()
    if len(selection_indices) != 1:
        handle_number_of_items_selected_is_not_one(
            create_link_action,
            delete_action,
            duplicate_action,
            new_rotation_action,
            new_translation_action,
            zoom_action,
        )
    else:
        selected_object = selection_indices[0].internalPointer()
        selected_object_is_component = isinstance(selected_object, Component)
        zoom_action.setEnabled(selected_object_is_component)

        selected_object_is_component_or_transform = isinstance(
            selected_object, (Component, Transformation)
        )
        duplicate_action.setEnabled(selected_object_is_component_or_transform)
        edit_component_action.setEnabled(selected_object_is_component)

        selected_object_is_not_link_transform = not isinstance(
            selected_object, LinkTransformation
        )
        new_rotation_action.setEnabled(selected_object_is_not_link_transform)
        new_translation_action.setEnabled(selected_object_is_not_link_transform)
        delete_action.setEnabled(
            selected_object_is_component_or_transform
            or not selected_object_is_not_link_transform
        )

        if isinstance(selected_object, Component):
            if not hasattr(selected_object, "stored_transforms"):
                selected_object.stored_transforms = selected_object.transforms
            create_link_action.setEnabled(
                not selected_object.stored_transforms.has_link
            )
        elif isinstance(selected_object, TransformationsList):
            create_link_action.setEnabled(not selected_object.has_link)
        elif isinstance(selected_object, Transformation):
            create_link_action.setEnabled(not selected_object.parent.has_link)
        else:
            create_link_action.setEnabled(False)


def handle_number_of_items_selected_is_not_one(
    delete_action: QAction,
    duplicate_action: QAction,
    new_rotation_action: QAction,
    new_translation_action: QAction,
    create_link_action: QAction,
    zoom_action: QAction,
):
    """
    Disables all actions when the number of selected items in the Component Tree View is not equal to one.
    :param delete_action: The action for deleting an item.
    :param duplicate_action: The action for duplicating an item.
    :param new_rotation_action: The action for creating a new rotation.
    :param new_translation_action: The action for creating a new translation.
    :param create_link_action: The action for creating a link.
    :param zoom_action: The action for zooming on a component.
    """
    delete_action.setEnabled(False)
    duplicate_action.setEnabled(False)
    new_rotation_action.setEnabled(False)
    new_translation_action.setEnabled(False)
    create_link_action.setEnabled(False)
    zoom_action.setEnabled(False)


def expand_transformation_list(
    node: QModelIndex,
    component_tree_view: QTreeView,
    component_model: ComponentTreeModel,
):
    current_pointer = node.internalPointer()
    if isinstance(current_pointer, TransformationsList) or isinstance(
        current_pointer, Component
    ):
        component_tree_view.expand(node)
        if isinstance(current_pointer, Component):
            trans_list_index = component_model.index(1, 0, node)
            component_tree_view.expand(trans_list_index)
        else:
            component_index = component_model.parent(node)
            component_tree_view.expand(component_index)
    elif isinstance(current_pointer, Transformation):
        trans_list_index = component_model.parent(node)
        component_tree_view.expand(trans_list_index)
        component_index = component_model.parent(trans_list_index)
        component_tree_view.expand(component_index)


def add_transformation(
    transformation_type: TransformationType,
    component_tree_view: QTreeView,
    component_model: ComponentTreeModel,
):
    selected = component_tree_view.selectedIndexes()
    if len(selected) > 0:
        current_index = selected[0]
        if transformation_type == TransformationType.TRANSLATION:
            component_model.add_translation(current_index)
        elif transformation_type == TransformationType.ROTATION:
            component_model.add_rotation(current_index)
        else:
            raise ValueError(f"Unknown transformation type: {transformation_type}")
        expand_transformation_list(current_index, component_tree_view, component_model)


def fill_selection(option, painter):
    colour = QColor("lightblue")
    colour.setAlpha(100)
    painter.fillRect(option.rect, colour)


def get_link_transformation_frame(frame, instrument, value):
    frame.transformation_frame = EditTransformationLink(frame, value, instrument)
    frame.layout().addWidget(frame.transformation_frame, Qt.AlignTop)


def get_transformation_frame(frame, instrument, value):
    if value.type == TransformationType.TRANSLATION:
        frame.transformation_frame = EditTranslation(frame, value, instrument)
    elif value.type == TransformationType.ROTATION:
        frame.transformation_frame = EditRotation(frame, value, instrument)
    else:
        raise (RuntimeError('Transformation type "{}" is unknown.'.format(value.type)))
    frame.layout().addWidget(frame.transformation_frame, Qt.AlignTop)


def get_component_info_frame(frame):
    frame.label = QLabel("", frame)
    frame.layout().addWidget(frame.label)


def get_transformations_list_frame(frame):
    frame.label = QLabel("Transformations", frame)
    frame.layout().addWidget(frame.label)


def get_component_frame(frame, value):
    frame.label = QLabel(f"{value.name} ({value.nx_class})", frame)
    frame.layout().addWidget(frame.label)
