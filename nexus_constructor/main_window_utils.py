import os

from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QToolBar, QWidget, QTreeView

from nexus_constructor.component.component import Component
from nexus_constructor.component.link_transformation import LinkTransformation
from nexus_constructor.component.transformations_list import TransformationsList
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.transformations import Transformation


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
        QIcon(os.path.join("ui", icon_path)), mouse_over_text, component_tree_view_tab
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

        zoom_action.setEnabled(isinstance(selected_object, Component))

        selected_object_is_component_or_transform = isinstance(
            selected_object, (Component, Transformation)
        )
        duplicate_action.setEnabled(selected_object_is_component_or_transform)
        edit_component_action.setEnabled(selected_object_is_component_or_transform)

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
