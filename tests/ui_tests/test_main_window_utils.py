from unittest.mock import Mock

import pytest
from PySide2.QtCore import QPoint, QModelIndex
from PySide2.QtWidgets import QToolBar, QWidget, QTreeView

from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window_utils import (
    create_and_add_toolbar_action,
    set_button_state,
    expand_transformation_list,
    add_transformation,
)
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from tests.test_utils import DEFINITIONS_DIR
from tests.ui_tests.ui_test_utils import show_window_and_wait_for_interaction  # noqa


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
def component_tree_view(template, instrument, component_model, qtbot):
    component_tree_view = QTreeView(template)
    component_delegate = ComponentEditorDelegate(component_tree_view, instrument)
    component_tree_view.setItemDelegate(component_delegate)
    component_tree_view.setModel(component_model)
    qtbot.addWidget(component_tree_view)
    template.ui = component_tree_view
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


@pytest.fixture(scope="function")
def set_of_all_actions(
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
):
    return {
        delete_action,
        duplicate_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
        edit_component_action,
    }


def get_sample_index(component_tree_view: ComponentTreeModel):
    return component_tree_view.indexAt(QPoint(0, 0))


def add_transformation_at_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    component_index: QModelIndex,
):
    component_tree_view.setCurrentIndex(component_index)
    component_model.add_transformation(component_index, "translation")


def add_link_at_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    component_index: QModelIndex,
):
    component_tree_view.setCurrentIndex(component_index)
    component_model.add_link(component_index)


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

    assert not any([action.isEnabled() for action in actions])


def test_GIVEN_component_is_selected_WHEN_changing_button_state_THEN_all_buttons_are_enabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    set_of_all_actions,
):
    sample_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_index)

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

    assert all([action.isEnabled() for action in set_of_all_actions])


def test_GIVEN_transformation_is_selected_WHEN_changing_button_states_THEN_expected_buttons_are_enabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Select the sample in the component tree view
    sample_component_index = get_sample_index(component_tree_view)
    add_transformation_at_index(
        component_model, component_tree_view, sample_component_index
    )
    # Expand the tree at the sample
    component_tree_view.expand(sample_component_index)
    # Retrieve the index of the transformation list and expand the tree at this point
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_tree_view.expand(transformation_list_index)
    # Retrieve the index of the transformation that has just been created and set it as the current index of the tree
    # view
    transformation_index = component_model.index(0, 0, transformation_list_index)
    component_tree_view.setCurrentIndex(transformation_index)

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

    transformation_selected_actions = {
        delete_action,
        duplicate_action,
        edit_component_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
    }
    assert all([action.isEnabled() for action in transformation_selected_actions])
    assert not any(
        [
            action.isEnabled()
            for action in set_of_all_actions - transformation_selected_actions
        ]
    )


def test_GIVEN_link_is_selected_WHEN_changing_button_states_THEN_expected_buttons_are_enabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Select the sample in the component tree view
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    # Expand the tree at the sample
    component_tree_view.expand(sample_component_index)
    # Retrieve the index of the transformation list and expand the tree at this point
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_tree_view.expand(transformation_list_index)
    # Retrieve the index of the link that has just been created and set it as the current index of the tree view
    link_index = component_model.index(0, 0, transformation_list_index)
    component_tree_view.setCurrentIndex(link_index)

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

    link_transformation_selected_actions = {delete_action}
    assert all([action.isEnabled() for action in link_transformation_selected_actions])
    assert not any(
        [
            action.isEnabled()
            for action in set_of_all_actions - link_transformation_selected_actions
        ]
    )


def test_GIVEN_component_is_selected_WHEN_component_already_has_link_and_changing_button_states_THEN_create_link_button_is_disabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Select the sample in the component tree view
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    # Expand the tree at the sample
    component_tree_view.expand(sample_component_index)
    # Retrieve the index of the transformation list and expand the tree at this point
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_tree_view.expand(transformation_list_index)
    # Retrieve the index of the link that has just been created and set it as the current index of the tree view
    component_tree_view.setCurrentIndex(sample_component_index)

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

    already_has_link_actions = set_of_all_actions - {create_link_action}
    assert all([action.isEnabled() for action in already_has_link_actions])
    assert not any(
        [action.isEnabled() for action in set_of_all_actions - already_has_link_actions]
    )


def test_GIVEN_transformation_list_is_selected_WHEN_component_already_has_link_THEN_create_link_button_is_disabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Select the sample in the component tree view
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    # Expand the tree at the sample
    component_tree_view.expand(sample_component_index)
    # Retrieve the index of the transformation list and expand the tree at this point
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_tree_view.setCurrentIndex(transformation_list_index)

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

    already_has_link_actions = {new_translation_action, new_rotation_action}
    assert all([action.isEnabled() for action in already_has_link_actions])
    assert not any(
        [action.isEnabled() for action in set_of_all_actions - already_has_link_actions]
    )


def test_GIVEN_transformation_list_is_selected_WHEN_component_doesnt_have_link_THEN_create_link_button_is_enabled(
    component_tree_view,
    delete_action,
    duplicate_action,
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Select the sample in the component tree view
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    # Expand the tree at the sample
    component_tree_view.expand(sample_component_index)
    # Retrieve the index of the transformation list and expand the tree at this point
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_tree_view.setCurrentIndex(transformation_list_index)

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

    doesnt_have_link_actions = {
        new_translation_action,
        new_rotation_action,
        create_link_action,
    }
    assert all([action.isEnabled() for action in doesnt_have_link_actions])
    assert not any(
        [action.isEnabled() for action in set_of_all_actions - doesnt_have_link_actions]
    )


def test_GIVEN_item_is_component_WHEN_expanding_transformation_list_THEN_transformation_list_is_expanded(
    component_tree_view, component_model
):

    sample_component_index = get_sample_index(component_tree_view)
    expand_transformation_list(
        sample_component_index, component_tree_view, component_model
    )

    transformation_list_index = component_model.index(1, 0, sample_component_index)
    assert component_tree_view.isExpanded(transformation_list_index)
    assert component_tree_view.isExpanded(sample_component_index)


def test_GIVEN_item_is_transformation_list_WHEN_expanding_transformation_list_THEN_transformation_is_expanded(
    component_tree_view, component_model
):

    sample_component_index = get_sample_index(component_tree_view)
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    expand_transformation_list(
        transformation_list_index, component_tree_view, component_model
    )

    assert component_tree_view.isExpanded(sample_component_index)
    assert component_tree_view.isExpanded(transformation_list_index)


def test_GIVEN_item_is_transformation_WHEN_expanding_transformation_list_THEN_transformation_list_is_expanded(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    transformation_list_index = component_model.index(1, 0, sample_component_index)
    component_model.add_translation(sample_component_index)
    transformation_index = component_model.index(0, 0, transformation_list_index)

    expand_transformation_list(
        transformation_index, component_tree_view, component_model
    )

    assert component_tree_view.isExpanded(sample_component_index)
    assert component_tree_view.isExpanded(transformation_list_index)


def test_GIVEN_translation_is_added_WHEN_adding_transformation_THEN_translation_is_added_to_component_model(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    add_transformation("translation", component_tree_view, component_model)

    # assert


def test_GIVEN_rotation_is_added_WHEN_adding_transformation_THEN_rotation_is_added_to_component_model(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    add_transformation("rotation", component_tree_view, component_model)

    # assert
