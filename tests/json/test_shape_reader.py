from typing import List

import pytest
from PySide2.QtGui import QVector3D
from mock import Mock

from nexus_constructor.json.load_from_json_utils import (
    _find_attribute_from_list_or_dict,
)
from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.model.component import Component, OFF_GEOMETRY_NX_CLASS
from nexus_constructor.model.geometry import OFFGeometryNexus
from tests.json.shape_json import off_shape_json, cylindrical_shape_json

EXPECTED_TYPES = {"faces": "int", "vertices": "float", "winding_order": "int"}
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
def off_shape_reader(mock_component, off_shape_json) -> ShapeReader:
    return ShapeReader(mock_component, off_shape_json)


@pytest.fixture(scope="function")
def cylindrical_shape_reader(mock_component, cylindrical_shape_json):
    return ShapeReader(mock_component, cylindrical_shape_json)


def _any_warning_message_has_substrings(
    sub_strings: List[str], warning_messages: str
) -> bool:
    """
    Checks that at least one of the warning messages from the shape reader contains all the given sub-strings.
    :param sub_strings: The list of the substrings.
    :param warning_messages: The warning messages from the shape reader.
    :return: True if at least of the warnings contains all the sub-strings, False otherwise.
    """
    return any(
        [
            all([substring in warning_message for substring in sub_strings])
            for warning_message in warning_messages
        ]
    )


def test_GIVEN_off_shape_WHEN_reading_shape_information_THEN_error_and_issue_messages_have_expected_content(
    off_shape_reader,
):
    off_shape_reader.add_shape_to_component()

    for message in [off_shape_reader.error_message, off_shape_reader.issue_message]:
        assert OFF_GEOMETRY_NX_CLASS in message
        assert OFF_GEOMETRY_NX_CLASS in message


def test_GIVEN_unrecognised_shape_WHEN_reading_shape_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    off_shape_json["attributes"][0]["values"] = bad_geometry_type = "NotAValidGeometry"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [bad_geometry_type], off_shape_reader.warnings
    )


def test_GIVEN_no_attributes_field_WHEN_reading_shape_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    del off_shape_json["attributes"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        ["Unrecognised shape type for component"], off_shape_reader.warnings
    )


def test_GIVEN_missing_children_attribute_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    del off_shape_json["children"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Unable to find children list in shape group.",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_name_WHEN_reading_off_information_THEN_issue_message_is_created_and_substitute_name_is_used(
    off_shape_reader, off_shape_json, mock_component
):
    del off_shape_json["name"]
    off_shape_reader.add_shape_to_component()

    assert mock_component["shape"].name == "shape"
    assert _any_warning_message_has_substrings(
        [off_shape_reader.issue_message, "Unable to find name of shape."],
        off_shape_reader.warnings,
    )


def test_GIVEN_children_is_not_a_list_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    off_shape_json["children"] = "NotAList"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Children attribute in shape group is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_to_remove", EXPECTED_TYPES.keys())
def test_GIVEN_cant_find_attribute_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_to_remove
):
    attribute = off_shape_reader._get_shape_dataset_from_list(
        attribute_to_remove, off_shape_json["children"]
    )
    off_shape_json["children"].remove(attribute)

    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [attribute_to_remove, off_shape_reader.error_message], off_shape_reader.warnings
    )


@pytest.mark.parametrize("attribute_with_dataset_type_to_change", EXPECTED_TYPES.keys())
def test_GIVEN_type_value_is_not_expected_type_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_change, off_shape_json["children"]
    )

    invalid_dataset["dataset"]["type"] = "string"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Type attribute for {attribute_with_dataset_type_to_change} does not match expected type(s)",
            EXPECTED_TYPES[attribute_with_dataset_type_to_change],
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_dataset_type_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_unable_to_find_type_value_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_delete, off_shape_json["children"]
    )

    del invalid_dataset["dataset"]["type"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Unable to find type attribute for {attribute_with_dataset_type_to_delete}",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_dataset_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_unable_to_find_dataset_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_to_delete, off_shape_json["children"]
    )

    del invalid_dataset["dataset"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Unable to find type attribute for {attribute_with_dataset_to_delete}.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_values_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_missing_values_attribute_WHEN_finding_values_attribute_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_values_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_delete, off_shape_json["children"]
    )

    del invalid_dataset["values"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"Unable to find values in {attribute_with_values_to_delete} dataset.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_values_to_change", EXPECTED_TYPES.keys())
def test_GIVEN_values_attribute_is_not_a_list_WHEN_finding_values_attribute_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_values_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_change, off_shape_json["children"]
    )

    invalid_dataset["values"] = True
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"values attribute in {attribute_with_values_to_change} dataset is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_list_size_to_change", EXPECTED_TYPES.keys())
def test_GIVEN_inconsistent_list_size_WHEN_validating_attribute_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_list_size_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_list_size_to_change, off_shape_json["children"]
    )

    invalid_dataset["dataset"]["size"][0] -= 1
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Mismatch between length of {attribute_with_list_size_to_change} list",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_list_size_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_no_list_size_information_WHEN_validating_attribute_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_list_size_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_list_size_to_delete, off_shape_json["children"]
    )

    del invalid_dataset["dataset"]["size"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Unable to find size attribute for {attribute_with_list_size_to_delete} dataset.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_value_to_change", ["faces", "winding_order"])
def test_GIVEN_value_has_wrong_type_WHEN_validating_value_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_value_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_value_to_change, off_shape_json["children"]
    )

    invalid_dataset["values"][0] = "astring"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"Values in {attribute_with_value_to_change} list do not all have type(s)",
            EXPECTED_TYPES[attribute_with_value_to_change],
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_attributes_WHEN_finding_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    del vertices_dataset["attributes"]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Unable to find attributes list in vertices dataset.",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_units_WHEN_finding_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    units = off_shape_reader._get_shape_dataset_from_list(
        "units", vertices_dataset["attributes"]
    )
    vertices_dataset["attributes"].remove(units)
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Unable to find units attribute in vertices dataset.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("invalid_units", ["abc", "decibels", "2 m"])
def test_GIVEN_invalid_units_WHEN_validating_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, invalid_units
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    off_shape_reader._get_shape_dataset_from_list(
        "units", vertices_dataset["attributes"]
    )["values"] = invalid_units
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [off_shape_reader.error_message, invalid_units], off_shape_reader.warnings,
    )


def test_GIVEN_shape_json_WHEN_reading_shape_THEN_geometry_object_has_expected_properties(
    off_shape_reader, off_shape_json, mock_component
):
    children = off_shape_json["children"]

    name = off_shape_json["name"]
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", children
    )
    vertices = list(map(lambda vertex: QVector3D(*vertex), vertices_dataset["values"]))
    faces = off_shape_reader._get_shape_dataset_from_list("faces", children)["values"]
    units = _find_attribute_from_list_or_dict("units", vertices_dataset["attributes"])
    winding_order = off_shape_reader._get_shape_dataset_from_list(
        "winding_order", children
    )["values"]

    off_shape_reader.add_shape_to_component()

    shape = mock_component["shape"]
    assert isinstance(shape, OFFGeometryNexus)
    assert shape.name == name
    assert shape.units == units
    assert shape.get_field_value("faces") == faces
    assert shape.vertices == vertices
    assert shape.winding_order == winding_order


def test_GIVEN_missing_children_attribute_WHEN_reading_cylindrical_information_THEN_error_message_is_created(
    cylindrical_shape_reader, cylindrical_shape_json
):
    del cylindrical_shape_json["children"]
    cylindrical_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            cylindrical_shape_reader.error_message,
            "Unable to find children list in shape group.",
        ],
        cylindrical_shape_reader.warnings,
    )
