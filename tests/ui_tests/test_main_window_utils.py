from unittest.mock import Mock

import pytest
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QToolBar, QWidget, QTreeView

from nexus_constructor.component.component import Component
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window_utils import (
    create_and_add_toolbar_action,
    set_button_state,
)
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from tests.test_utils import DEFINITIONS_DIR


@pytest.fixture
def template(qtbot):
    return QWidget()


@pytest.fixture
def tool_bar(template):
    return QToolBar(template)


@pytest.fixture
def tree_view_tab(template):
    return QWidget(template)


@pytest.fixture(scope="function")
def icon_path():
    return "new_component.png"


@pytest.fixture(scope="function")
def mouse_over_text():
    return "New Component"


@pytest.fixture(scope="function")
def trigger_method_mock():
    return Mock()


@pytest.fixture(scope="function")
def instrument():
    nexus_wrapper = NexusWrapper("test")
    yield Instrument(nexus_wrapper, DEFINITIONS_DIR)
    nexus_wrapper.nexus_file.close()


@pytest.fixture(scope="function")
def component_model(instrument):
    return ComponentTreeModel(instrument)


@pytest.fixture(scope="function")
def component_tree_view(template, instrument, component_model):
    component_tree_view = QTreeView(template)
    component_delegate = ComponentEditorDelegate(component_tree_view, instrument)
    component_tree_view.setItemDelegate(component_delegate)
    component_tree_view.setModel(component_model)
    return component_tree_view


@pytest.fixture(scope="function")
def delete_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "delete.png", "Delete", trigger_method_mock, tool_bar, tree_view_tab
    )


@pytest.fixture(scope="function")
def duplicate_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "duplicate.png", "Duplicate", trigger_method_mock, tool_bar, tree_view_tab
    )


@pytest.fixture(scope="function")
def new_rotation_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "new_rotation.png", "New Rotation", trigger_method_mock, tool_bar, tree_view_tab
    )


@pytest.fixture(scope="function")
def new_translation_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "new_translation.png",
        "New Translation",
        trigger_method_mock,
        tool_bar,
        tree_view_tab,
    )


@pytest.fixture(scope="function")
def create_link_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "create_link.png", "Create Link", trigger_method_mock, tool_bar, tree_view_tab
    )


@pytest.fixture(scope="function")
def zoom_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "zoom.svg", "Zoom To Component", trigger_method_mock, tool_bar, tree_view_tab
    )


@pytest.fixture(scope="function")
def edit_component_action(trigger_method_mock, tool_bar, tree_view_tab):
    return create_and_add_toolbar_action(
        "edit_component.png",
        "Edit Component",
        trigger_method_mock,
        tool_bar,
        tree_view_tab,
    )


@pytest.mark.parametrize("set_enabled", [True, False])
def test_GIVEN_action_properties_WHEN_creating_action_THEN_action_has_expected_attributes(
    icon_path,
    mouse_over_text,
    trigger_method_mock,
    tool_bar,
    tree_view_tab,
    set_enabled,
):
    if not set_enabled:
        action = create_and_add_toolbar_action(
            icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
        )
    else:
        action = create_and_add_toolbar_action(
            icon_path,
            mouse_over_text,
            trigger_method_mock,
            tool_bar,
            tree_view_tab,
            set_enabled,
        )

    assert action.toolTip() == mouse_over_text
    assert action.parent() is tree_view_tab
    assert not action.icon().isNull()
    assert action.isEnabled() == set_enabled


def test_GIVEN_action_is_triggered_THEN_expected_trigger_method_is_called(
    icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
):
    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
    )
    action.trigger()
    trigger_method_mock.assert_called_once()


def test_GIVEN_items_selected_is_not_one_WHEN_interacting_with_tree_view_THEN_expected_buttons_are_disabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
):
    # Set the actions to enabled to make sure that their state changes
    actions = [
        delete_action,
        duplicate_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
    ]
    for action in actions:
        action.setEnabled(True)

    set_button_state(
        component_tree_view,
        delete_action,
        duplicate_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
        edit_component_action,
    )

    assert all([not action.isEnabled() for action in actions])


def test_GIVEN_component_is_selected_WHEN_changing_button_state_THEN_expected_buttons_are_enabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    instrument,
):
    # Add a component to the component model
    nexus_file = instrument.nexus.nexus_file
    component_group = nexus_file.create_dataset("Component", data=1)
    component_model.add_component(Component(nexus_file, component_group))

    component_tree_view.rootIndex()
