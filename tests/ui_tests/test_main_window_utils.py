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


def test_GIVEN_action_properties_WHEN_creating_action_THEN_action_has_expected_attributes(
    tool_bar, tree_view_tab
):

    icon_path = "new_component.png"
    mouse_over_text = "New Component"
    trigger_method = Mock()

    action = create_and_add_toolbar_action(
        icon_path, mouse_over_text, trigger_method, tool_bar, tree_view_tab
    )

    assert action.toolTip() == mouse_over_text
    assert action.parent() is tree_view_tab
    assert not action.icon().isNull()
