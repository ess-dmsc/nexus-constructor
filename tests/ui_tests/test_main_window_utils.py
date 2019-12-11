from unittest.mock import Mock

import pytest
from PySide2.QtWidgets import QToolBar, QWidget

from nexus_constructor.main_window_utils import create_and_add_toolbar_action


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


def test_GIVEN_action_properties_WHEN_creating_action_THEN_action_has_expected_attributes(
    icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
):
    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
    )

    assert action.toolTip() == mouse_over_text
    assert action.parent() is tree_view_tab
    assert not action.icon().isNull()
    assert not action.isEnabled()


def test_GIVEN_action_is_triggered_THEN_expected_trigger_method_is_called(
    icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
):
    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method_mock, tool_bar, tree_view_tab
    )
    action.trigger()
    trigger_method_mock.assert_called_once()
