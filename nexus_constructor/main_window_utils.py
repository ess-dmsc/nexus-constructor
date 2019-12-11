import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QToolBar, QWidget


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
    :param component_tree_view_tab: No idea...
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
