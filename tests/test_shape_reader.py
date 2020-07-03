import pytest
from mock import Mock

from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.model.component import Component, OFF_GEOMETRY_NX_CLASS
from tests.shape_json import off_shape_json

COMPONENT_NAME = "ComponentName"

component_shape = dict()


def getitem(name):
    return component_shape[name]


def setitem(name, val):
    component_shape[name] = val


@pytest.fixture(scope="function")
def mock_component():
    mock_component = Mock(spec=Component)
    mock_component.name = COMPONENT_NAME
    set_item_mock = Mock()
    set_item_mock.side_effect = setitem
    get_item_mock = Mock()
    get_item_mock.side_effect = getitem
    mock_component.__setitem__ = set_item_mock
    mock_component.__getitem__ = get_item_mock
    return mock_component


@pytest.fixture(scope="function")
def off_shape_reader(off_shape_json, mock_component) -> ShapeReader:
    return ShapeReader(mock_component, off_shape_json)


def test_GIVEN_off_shape_WHEN_reading_shape_information_THEN_error_and_warning_messages_have_expected_content(
    off_shape_reader,
):
    off_shape_reader.add_shape_to_component()

    for message in [off_shape_reader.error_message, off_shape_reader.issue_message]:
        assert OFF_GEOMETRY_NX_CLASS in message
        assert OFF_GEOMETRY_NX_CLASS in message
