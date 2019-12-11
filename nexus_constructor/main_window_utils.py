import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QToolBar, QWidget, QTreeView

from nexus_constructor.component.component import Component
from nexus_constructor.component.link_transformation import LinkTransformation
from nexus_constructor.component.transformations_list import TransformationsList
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


def set_button_state(
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
    indices = component_tree_view.selectedIndexes()
    if len(indices) != 1:
        delete_action.setEnabled(False)
        duplicate_action.setEnabled(False)
        new_rotation_action.setEnabled(False)
        new_translation_action.setEnabled(False)
        create_link_action.setEnabled(False)
        zoom_action.setEnabled(False)
    else:
        selected_object = indices[0].internalPointer()
        zoom_action.setEnabled(isinstance(selected_object, Component))
        if isinstance(selected_object, Component) or isinstance(
            selected_object, Transformation
        ):
            delete_action.setEnabled(True)
            duplicate_action.setEnabled(True)
            edit_component_action.setEnabled(True)
        else:
            delete_action.setEnabled(False)
            duplicate_action.setEnabled(False)
            edit_component_action.setEnabled(False)
        if isinstance(selected_object, LinkTransformation):
            new_rotation_action.setEnabled(False)
            new_translation_action.setEnabled(False)
            delete_action.setEnabled(True)
        else:
            new_rotation_action.setEnabled(True)
            new_translation_action.setEnabled(True)

        if isinstance(selected_object, Component):
            if not hasattr(selected_object, "stored_transforms"):
                selected_object.stored_transforms = selected_object.transforms
            if not selected_object.stored_transforms.has_link:
                create_link_action.setEnabled(True)
            else:
                create_link_action.setEnabled(False)
        elif isinstance(selected_object, TransformationsList):
            if not selected_object.has_link:
                create_link_action.setEnabled(True)
            else:
                create_link_action.setEnabled(False)
        elif isinstance(selected_object, Transformation):
            if not selected_object.parent.has_link:
                create_link_action.setEnabled(True)
            else:
                create_link_action.setEnabled(False)
        else:
            create_link_action.setEnabled(False)
