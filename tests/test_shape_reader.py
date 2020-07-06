from typing import List

import pytest
from mock import Mock

from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.model.component import Component, OFF_GEOMETRY_NX_CLASS
from tests.shape_json import off_shape_json

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
def off_shape_reader(off_shape_json, mock_component) -> ShapeReader:
    return ShapeReader(mock_component, off_shape_json)


def _any_warning_message_has_substrings(
    sub_strings: List[str], warning_messages: str
) -> bool:
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
    n_warnings = len(off_shape_reader.warnings)

    off_shape_json["attributes"][0]["values"] = bad_geometry_type = "NotAValidGeometry"
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [bad_geometry_type], off_shape_reader.warnings
    )


def test_GIVEN_no_attributes_field_WHEN_reading_shape_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    n_warnings = len(off_shape_reader.warnings)

    del off_shape_json["attributes"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert "''" in off_shape_reader.warnings[-1]


def test_GIVEN_missing_children_attribute_WHEN_reading_off_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    n_warnings = len(off_shape_reader.warnings)

    del off_shape_json["children"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Unable to find children list in shape group.",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_name_WHEN_reading_off_information_THEN_warning_message_is_created_and_substitute_name_is_used(
    off_shape_reader, off_shape_json, mock_component
):
    n_warnings = len(off_shape_reader.warnings)

    del off_shape_json["name"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert mock_component["shape"].name == "shape"


def test_GIVEN_children_is_not_a_list_WHEN_reading_off_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    n_warnings = len(off_shape_reader.warnings)

    off_shape_json["children"] = "NotAList"
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Children attribute in shape group is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_to_remove", EXPECTED_TYPES.keys())
def test_GIVEN_cant_find_attribute_WHEN_reading_off_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json, attribute_to_remove
):
    n_warnings = len(off_shape_reader.warnings)

    attribute = off_shape_reader._get_shape_dataset_from_list(
        attribute_to_remove, off_shape_json["children"]
    )
    off_shape_json["children"].remove(attribute)

    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [attribute_to_remove, off_shape_reader.error_message], off_shape_reader.warnings
    )


@pytest.mark.parametrize("attribute_with_dataset_type_to_change", EXPECTED_TYPES.keys())
def test_GIVEN_type_value_is_not_expected_type_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_change
):
    n_warnings = len(off_shape_reader.warnings)

    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_change, off_shape_json["children"]
    )

    invalid_dataset["dataset"]["type"] = "string"
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Type attribute for {attribute_with_dataset_type_to_change} does not match expected type"
            f" {EXPECTED_TYPES[attribute_with_dataset_type_to_change]}.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_dataset_type_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_unable_to_find_type_value_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_delete
):
    n_warnings = len(off_shape_reader.warnings)

    faces_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_delete, off_shape_json["children"]
    )

    del faces_dataset["dataset"]["type"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
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
    n_warnings = len(off_shape_reader.warnings)

    dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_to_delete, off_shape_json["children"]
    )

    del dataset["dataset"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) > n_warnings
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
    n_warnings = len(off_shape_reader.warnings)

    dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_delete, off_shape_json["children"]
    )

    del dataset["values"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
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
    n_warnings = len(off_shape_reader.warnings)

    dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_change, off_shape_json["children"]
    )

    dataset["values"] = True
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"Values in {attribute_with_values_to_change} attribute is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_list_size_to_change", EXPECTED_TYPES.keys())
def test_GIVEN_inconsistent_list_size_WHEN_validating_faces_indices_list_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_list_size_to_change
):
    n_warnings = len(off_shape_reader.warnings)

    dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_list_size_to_change, off_shape_json["children"]
    )

    dataset["dataset"]["size"][0] -= 1
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Mismatch between length of {attribute_with_list_size_to_change} list",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("atribute_with_list_size_to_delete", EXPECTED_TYPES.keys())
def test_GIVEN_no_list_size_information_WHEN_validating_faces_indices_list_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, atribute_with_list_size_to_delete
):
    n_warnings = len(off_shape_reader.warnings)

    dataset = off_shape_reader._get_shape_dataset_from_list(
        atribute_with_list_size_to_delete, off_shape_json["children"]
    )

    del dataset["dataset"]["size"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Unable to find size attribute for {atribute_with_list_size_to_delete} dataset.",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_faces_value_is_not_int_WHEN_validating_faces_indices_list_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    n_warnings = len(off_shape_reader.warnings)

    faces_dataset = off_shape_reader._get_shape_dataset_from_list(
        "faces", off_shape_json["children"]
    )

    faces_dataset["values"][0] = "astring"
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Values in faces starting indices list in faces dataset do not all have type int",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_attributes_WHEN_finding_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    n_warnings = len(off_shape_reader.warnings)

    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    del vertices_dataset["attributes"]
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
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
    n_warnings = len(off_shape_reader.warnings)

    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    units = off_shape_reader._get_shape_dataset_from_list(
        "units", vertices_dataset["attributes"]
    )
    vertices_dataset["attributes"].remove(units)
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
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
    n_warnings = len(off_shape_reader.warnings)

    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        "vertices", off_shape_json["children"]
    )

    off_shape_reader._get_shape_dataset_from_list(
        "units", vertices_dataset["attributes"]
    )["values"] = invalid_units
    off_shape_reader.add_shape_to_component()

    assert len(off_shape_reader.warnings) == n_warnings + 1
    assert _any_warning_message_has_substrings(
        [off_shape_reader.error_message, invalid_units], off_shape_reader.warnings,
    )
