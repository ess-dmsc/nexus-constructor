import os
import sys
from collections.abc import Callable

from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QColor, QIcon
from PySide2.QtWidgets import (
    QAction,
    QFrame,
    QLabel,
    QToolBar,
    QToolButton,
    QTreeView,
    QWidget,
)

from nexus_constructor.common_attrs import TransformationType
from nexus_constructor.component_tree_model import NexusTreeModel
from nexus_constructor.link_transformation import LinkTransformation
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import FileWriterModule
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.module_view import ModuleView
from nexus_constructor.transformation_view import (
    EditRotation,
    EditTransformationLink,
    EditTranslation,
)
from nexus_constructor.transformations_list import TransformationsList

# We have to use this for cx freeze as __file__ does not work

if getattr(sys, "frozen", False):
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")


def create_and_add_toolbar_action(
    icon_path: str,
    mouse_over_text: str,
    trigger_method: Callable,
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
    component_tool_bar.addAction(toolbar_action)
    set_enabled_and_raise(toolbar_action, set_enabled)
    return toolbar_action


def set_button_states(
    component_tree_view: QTreeView,
    new_component_action: QAction,
    delete_action: QAction,
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
    :param new_rotation_action: The action for creating a new rotation.
    :param new_translation_action: The action for creating a new translation.
    :param create_link_action: The action for creating a link.
    :param zoom_action: The action for zooming on a component.
    :param edit_component_action: The action for editing a component.
    """
    selection_indices = component_tree_view.selectedIndexes()
    if len(selection_indices) != 1:
        handle_number_of_items_selected_is_not_one(
            new_component_action,
            create_link_action,
            delete_action,
            new_rotation_action,
            new_translation_action,
            zoom_action,
            edit_component_action,
        )
    else:
        selected_object = selection_indices[0].internalPointer()
        selected_object_is_component = isinstance(selected_object, Component)
        selected_object_is_group = isinstance(selected_object, Group)
        selected_object_is_not_group_or_fw_module = isinstance(
            selected_object, Component
        ) or not isinstance(selected_object, (Group, FileWriterModule))
        set_enabled_and_raise(zoom_action, selected_object_is_component)
        set_enabled_and_raise(new_component_action, selected_object_is_group)
        set_enabled_and_raise(edit_component_action, selected_object_is_group)

        selected_object_is_not_link_transform = not isinstance(
            selected_object, LinkTransformation
        )

        set_enabled_and_raise(
            new_rotation_action,
            selected_object_is_not_link_transform
            and selected_object_is_not_group_or_fw_module,
        )

        set_enabled_and_raise(
            new_translation_action,
            selected_object_is_not_link_transform
            and selected_object_is_not_group_or_fw_module,
        )

        not_tree_root = True
        if hasattr(selected_object, "parent_node") and not selected_object.parent_node:
            not_tree_root = False

        set_enabled_and_raise(delete_action, not_tree_root)
        if isinstance(selected_object, Component):
            if selected_object.stored_transforms is None:
                selected_object.stored_transforms = selected_object.transforms
            set_enabled_and_raise(
                create_link_action, not selected_object.stored_transforms.has_link
            )

        elif isinstance(selected_object, TransformationsList):
            set_enabled_and_raise(create_link_action, not selected_object.has_link)
        elif isinstance(selected_object, Transformation):
            set_enabled_and_raise(
                create_link_action,
                not selected_object.parent_component.transforms.has_link,
            )
        else:
            set_enabled_and_raise(create_link_action, False)


def set_enabled_and_raise(action: QAction, value: bool):
    """Disable or enable the action and autoRaise the associated QToolButton.

    Parameters
    ----------
        action: QAction
            The action to enable or disable
        value: bool
            True to enable action and raise associated QToolButton.
    """
    action.setEnabled(value)
    for widget in action.associatedWidgets():
        if isinstance(widget, QToolButton):
            widget.setAutoRaise(not value)
            # Change background color to pale gray if button is enabled
            color = "#d7d6d5" if value else "white"
            widget.setStyleSheet(f"background-color: {color}")


def handle_number_of_items_selected_is_not_one(
    delete_action: QAction,
    new_component_action: QAction,
    new_rotation_action: QAction,
    new_translation_action: QAction,
    create_link_action: QAction,
    zoom_action: QAction,
    edit_component_action: QAction,
):
    """
    Disables all actions when the number of selected items in the Component Tree View is not equal to one.
    :param delete_action: The action for deleting an item.
    :param new_rotation_action: The action for creating a new rotation.
    :param new_translation_action: The action for creating a new translation.
    :param create_link_action: The action for creating a link.
    :param zoom_action: The action for zooming on a component.
    """
    for action in vars().values():
        set_enabled_and_raise(action, False)


def expand_transformation_list(
    node: QModelIndex,
    component_tree_view: QTreeView,
    component_model: NexusTreeModel,
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
    transformation_type: str,
    component_tree_view: QTreeView,
    component_model: NexusTreeModel,
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


def get_link_transformation_frame(
    frame: QFrame, model: Model, value: LinkTransformation
):
    frame.transformation_frame = EditTransformationLink(frame, value, model)
    frame.layout().addWidget(frame.transformation_frame, Qt.AlignTop)


def get_transformation_frame(frame: QFrame, model: Model, value: Transformation):
    if value.transform_type == TransformationType.TRANSLATION:
        frame.transformation_frame = EditTranslation(frame, value, model)
    elif value.transform_type == TransformationType.ROTATION:
        frame.transformation_frame = EditRotation(frame, value, model)
    else:
        raise (
            RuntimeError(
                'Transformation type "{}" is unknown.'.format(value.transform_type)
            )
        )
    frame.layout().addWidget(frame.transformation_frame, Qt.AlignTop)


def get_transformations_list_frame(frame):
    frame.label = QLabel("Transformations", frame)
    frame.layout().addWidget(frame.label)


def get_group_info_frame(frame, value):
    frame.label = QLabel(f"{value.name} ({value.nx_class})", frame)
    frame.layout().addWidget(frame.label)


def get_group_frame(frame, value):
    text = f"{value.name}"
    if value.nx_class:
        text += f" ({value.nx_class})"
    frame.label = QLabel(text, frame)
    frame.layout().addWidget(frame.label)


def get_module_frame(frame: QFrame, model: Model, value: FileWriterModule):
    module_frame = ModuleView(value, frame, model)
    frame.module_frame = module_frame
    frame.layout().addWidget(frame.module_frame)
