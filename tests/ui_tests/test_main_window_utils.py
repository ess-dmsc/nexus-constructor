from unittest.mock import Mock

import pytest
from PySide2.QtCore import QModelIndex, QPoint
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QFrame, QToolBar, QTreeView, QVBoxLayout, QWidget

from nexus_constructor.common_attrs import TransformationType
from nexus_constructor.component_tree_model import NexusTreeModel as ComponentTreeModel
from nexus_constructor.component_tree_view import ComponentEditorDelegate
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.transformation_view import EditRotation, EditTranslation
from nexus_constructor.treeview_utils import (
    add_transformation,
    create_and_add_toolbar_action,
    expand_transformation_list,
    get_transformation_frame,
    set_button_states,
)


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
def component_model(model: Model):
    return ComponentTreeModel(model)


@pytest.fixture(scope="function")
def component_tree_view(template, model, component_model, qtbot):
    component_tree_view = QTreeView(template)
    component_delegate = ComponentEditorDelegate(component_tree_view, model)
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
):
    return {
        delete_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
        edit_component_action,
    }


def get_sample_index(component_tree_view: QTreeView) -> QModelIndex:
    """
    Retrieves the QModelIndex of the sample in the component tree view.
    :param component_tree_view: The component tree view in the main window.
    :return: The index of the sample component.
    """
    return component_tree_view.indexAt(QPoint(0, 0))


def add_transformation_at_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    component_index: QModelIndex,
):
    """
    Adds a transformation to the component model at a given index.
    :param component_model: The component model.
    :param component_tree_view: The component tree view.
    :param component_index: The QModelIndex that is selected when the transformation is added.
    """
    component_tree_view.setCurrentIndex(component_index)
    component_model.add_transformation(component_index, TransformationType.TRANSLATION)


def add_link_at_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    component_index: QModelIndex,
):
    """
    Adds a link to the component model at a given index.
    :param component_model: The component model.
    :param component_tree_view: The component tree view.
    :param component_index: The QModelIndex that is selected when the link is added.
    """
    component_tree_view.setCurrentIndex(component_index)
    component_model.add_link(component_index)


def get_transformation_list_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    component_index: QModelIndex,
) -> QModelIndex:
    """
    Retrieves the index of a component's transformation list from the component tree view.
    :param component_model: The component model.
    :param component_tree_view: The component tree view.
    :param component_index: The index of the component.
    :return: The index of the component's transformation list.
    """
    component_tree_view.expand(component_index)
    return component_model.index(1, 0, component_index)


def get_transformation_or_link_index(
    component_model: ComponentTreeModel,
    component_tree_view: QTreeView,
    transformation_list_index: QModelIndex,
) -> QModelIndex:
    """
    Retrieves the index of a component's first transformation or link.
    :param component_model: The component tree model.
    :param component_tree_view: The component tree view.
    :param transformation_list_index: The index of the component's transformation list.
    :return: The index of the component's first transformation/link.
    """
    component_tree_view.expand(transformation_list_index)
    return component_model.index(0, 0, transformation_list_index)


def test_GIVEN_action_properties_WHEN_creating_disabled_action_THEN_action_has_expected_attributes(
    icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
):
    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
    )

    assert action.toolTip() == mouse_over_text
    assert action.parent() is tree_view_tab
    assert not action.icon().isNull()
    assert not action.isEnabled()


def test_GIVEN_action_properties_WHEN_creating_enabled_action_THEN_action_has_expected_attributes(
    icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
):
    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab, True
    )

    assert action.toolTip() == mouse_over_text
    assert action.parent() is tree_view_tab
    assert not action.icon().isNull()
    assert action.isEnabled()


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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
):
    # Set the actions to enabled to make sure that their state changes
    actions = [
        delete_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
    ]
    for action in actions:
        action.setEnabled(True)

    set_button_states(
        component_tree_view,
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    set_of_all_actions,
):
    sample_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_index)

    set_button_states(
        component_tree_view,
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Create a transformation and select it on the component list
    sample_component_index = get_sample_index(component_tree_view)
    add_transformation_at_index(
        component_model, component_tree_view, sample_component_index
    )
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    transformation_index = get_transformation_or_link_index(
        component_model, component_tree_view, transformation_list_index
    )
    component_tree_view.setCurrentIndex(transformation_index)

    set_button_states(
        component_tree_view,
        delete_action,
        new_rotation_action,
        new_translation_action,
        create_link_action,
        zoom_action,
        edit_component_action,
    )

    transformation_selected_actions = {
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Create a link and select it on the component list
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    link_index = get_transformation_or_link_index(
        component_model, component_tree_view, transformation_list_index
    )
    component_tree_view.setCurrentIndex(link_index)

    set_button_states(
        component_tree_view,
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Create a link and then select the sample component
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    component_tree_view.setCurrentIndex(sample_component_index)

    set_button_states(
        component_tree_view,
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Create a link and then select the transformation list
    sample_component_index = get_sample_index(component_tree_view)
    add_link_at_index(component_model, component_tree_view, sample_component_index)
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    component_tree_view.setCurrentIndex(transformation_list_index)

    set_button_states(
        component_tree_view,
        delete_action,
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
    new_rotation_action,
    new_translation_action,
    create_link_action,
    zoom_action,
    edit_component_action,
    component_model,
    set_of_all_actions,
):
    # Don't create a link and then select the transformation list
    sample_component_index = get_sample_index(component_tree_view)
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    component_tree_view.setCurrentIndex(transformation_list_index)

    set_button_states(
        component_tree_view,
        delete_action,
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
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    assert component_tree_view.isExpanded(transformation_list_index)
    assert component_tree_view.isExpanded(sample_component_index)


def test_GIVEN_item_is_transformation_list_WHEN_expanding_transformation_list_THEN_transformation_is_expanded(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    expand_transformation_list(
        transformation_list_index, component_tree_view, component_model
    )

    assert component_tree_view.isExpanded(sample_component_index)
    assert component_tree_view.isExpanded(transformation_list_index)


def test_GIVEN_item_is_transformation_WHEN_expanding_transformation_list_THEN_transformation_list_is_expanded(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    transformation_list_index = get_transformation_list_index(
        component_model, component_tree_view, sample_component_index
    )
    component_model.add_translation(sample_component_index)
    transformation_index = component_model.index(0, 0, transformation_list_index)
    expand_transformation_list(
        transformation_index, component_tree_view, component_model
    )

    assert component_tree_view.isExpanded(sample_component_index)
    assert component_tree_view.isExpanded(transformation_list_index)


def test_GIVEN_translation_is_added_WHEN_adding_transformation_THEN_translation_is_added_to_component(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    add_transformation(
        TransformationType.TRANSLATION, component_tree_view, component_model
    )
    sample_component = sample_component_index.internalPointer()

    assert len(sample_component.transforms) == 1
    assert sample_component.transforms[0].transform_type == "translation"


def test_GIVEN_rotation_is_added_WHEN_adding_transformation_THEN_rotation_is_added_to_component(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    add_transformation(
        TransformationType.ROTATION, component_tree_view, component_model
    )
    sample_component = sample_component_index.internalPointer()

    assert len(sample_component.transforms) == 1
    assert sample_component.transforms[0].transform_type == "rotation"


def test_GIVEN_unknown_transformation_type_WHEN_adding_transformation_THEN_raises_value_error(
    component_tree_view, component_model
):
    sample_component_index = get_sample_index(component_tree_view)
    component_tree_view.setCurrentIndex(sample_component_index)
    with pytest.raises(ValueError):
        add_transformation(
            "NotAKnownTransformation", component_tree_view, component_model
        )


def create_transformation(trans_type: TransformationType):
    t = Transformation(
        parent_node=None, name="transformation", type=ValueTypes.DOUBLE, values=8
    )
    t.transform_type = trans_type
    t.vector = QVector3D(1, 0, 0)
    t.values = Dataset(
        parent_node=Transformation, name="", values=0, type=ValueTypes.DOUBLE
    )
    t.units = "m"
    return t


def test_GIVEN_rotation_WHEN_getting_transformation_frame_THEN_frame_type_is_edit_rotation(
    qtbot,
):
    frame = QFrame()
    frame.setLayout(QVBoxLayout())
    value = create_transformation(TransformationType.ROTATION)
    qtbot.addWidget(frame)
    get_transformation_frame(frame, None, value)
    assert isinstance(frame.transformation_frame, EditRotation)


def test_GIVEN_translation_WHEN_getting_transformation_frame_THEN_frame_type_is_edit_translation(
    qtbot,
):
    frame = QFrame()
    frame.setLayout(QVBoxLayout())
    value = create_transformation(TransformationType.TRANSLATION)
    qtbot.addWidget(frame)
    get_transformation_frame(frame, None, value)
    assert isinstance(frame.transformation_frame, EditTranslation)


def test_GIVEN_invalid_transformation_type_WHEN_getting_transformation_frame_THEN_runtime_error_is_thrown(
    qtbot,
):
    frame = QFrame()
    frame.setLayout(QVBoxLayout())
    value = create_transformation("asdf")
    qtbot.addWidget(frame)
    with pytest.raises(RuntimeError):
        get_transformation_frame(frame, None, value)
