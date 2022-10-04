from typing import Dict, List

import numpy as np
import pytest
from mock import Mock, call
from PySide6.QtGui import QVector3D

from nexus_constructor.common_attrs import (
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    GEOMETRY_GROUP_NAME,
    GEOMETRY_NX_CLASS,
    OFF_GEOMETRY_NX_CLASS,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.json.json_warnings import JsonWarningsContainer
from nexus_constructor.json.load_from_json_utils import (
    _find_attribute_from_list_or_dict,
)
from nexus_constructor.json.shape_reader import (
    DETECTOR_NUMBER,
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    Z_PIXEL_OFFSET,
    ShapeReader,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import (
    BoxGeometry,
    CylindricalGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.model.value_type import ValueTypes
from tests.json.shape_json import (
    box_shape_json,
    cylindrical_shape_json,
    off_shape_json,
    pixel_grid_list,
)

EXPECTED_OFF_TYPES = {
    "faces": ValueTypes.INT,
    "vertices": ValueTypes.FLOAT,
    "winding_order": ValueTypes.INT,
}
EXPECTED_CYLINDRICAL_TYPES = {"vertices": ValueTypes.FLOAT, "cylinders": ValueTypes.INT}
COMPONENT_NAME = "ComponentName"

component_shape = dict()


def getitem(name):
    return component_shape[name]


def setitem(name, val):
    component_shape[name] = val


def _get_data_type(json_object: Dict):
    if CommonKeys.DATA_TYPE in json_object:
        return json_object[CommonKeys.DATA_TYPE]
    elif CommonKeys.TYPE in json_object:
        return json_object[CommonKeys.TYPE]
    raise KeyError


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
def mock_cylindrical_shape():
    return Mock(spec=CylindricalGeometry)


@pytest.fixture(scope="function")
def mock_off_shape():
    return Mock(spec=OFFGeometryNexus)


@pytest.fixture(scope="function")
def off_shape_reader(mock_component, off_shape_json) -> ShapeReader:
    return ShapeReader(mock_component, off_shape_json)


@pytest.fixture(scope="function")
def cylindrical_shape_reader(mock_component, cylindrical_shape_json):
    return ShapeReader(mock_component, cylindrical_shape_json)


@pytest.fixture(scope="function")
def box_shape_reader(mock_component, box_shape_json):
    return ShapeReader(mock_component, box_shape_json)


def _any_warning_message_has_substrings(
    sub_strings: List[str], warning_messages: JsonWarningsContainer
) -> bool:
    """
    Checks that at least one of the warning messages from the shape reader contains all the given sub-strings.
    :param sub_strings: The list of the substrings.
    :param warning_messages: The warning messages from the shape reader.
    :return: True if at least of the warnings contains all the sub-strings, False otherwise.
    """
    return any(
        [
            all([substring in warning_message.message for substring in sub_strings])
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
    off_shape_json[CommonKeys.ATTRIBUTES][0][
        CommonKeys.VALUES
    ] = bad_geometry_type = "NotAValidGeometry"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [bad_geometry_type], off_shape_reader.warnings
    )


def test_GIVEN_no_attributes_field_WHEN_reading_shape_information_THEN_warning_message_is_created(
    off_shape_reader, off_shape_json
):
    del off_shape_json[CommonKeys.ATTRIBUTES]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        ["Unrecognised shape type for component"], off_shape_reader.warnings
    )


def test_GIVEN_missing_children_attribute_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    del off_shape_json[CommonKeys.CHILDREN]
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
    del off_shape_json[CommonKeys.NAME]
    off_shape_reader.add_shape_to_component()

    assert mock_component[SHAPE_GROUP_NAME].name == SHAPE_GROUP_NAME
    assert _any_warning_message_has_substrings(
        [off_shape_reader.issue_message, "Unable to find name of shape."],
        off_shape_reader.warnings,
    )


def test_GIVEN_children_is_not_a_list_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    off_shape_json[CommonKeys.CHILDREN] = "NotAList"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Children attribute in shape group is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_to_remove", EXPECTED_OFF_TYPES.keys())
def test_GIVEN_cant_find_attribute_WHEN_reading_off_information_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_to_remove
):
    attribute = off_shape_reader._get_shape_dataset_from_list(
        attribute_to_remove, off_shape_json[CommonKeys.CHILDREN]
    )
    off_shape_json[CommonKeys.CHILDREN].remove(attribute)

    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [attribute_to_remove, off_shape_reader.error_message], off_shape_reader.warnings
    )


@pytest.mark.parametrize(
    "attribute_with_dataset_type_to_change", EXPECTED_OFF_TYPES.keys()
)
def test_GIVEN_type_value_is_not_expected_type_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_change, off_shape_json[CommonKeys.CHILDREN]
    )

    invalid_dataset[NodeType.CONFIG][CommonKeys.DATA_TYPE] = "string"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Type attribute for {attribute_with_dataset_type_to_change} does not match expected type(s)",
            EXPECTED_OFF_TYPES[attribute_with_dataset_type_to_change],
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize(
    "attribute_with_dataset_type_to_delete", EXPECTED_OFF_TYPES.keys()
)
def test_GIVEN_unable_to_find_type_value_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_type_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_type_to_delete, off_shape_json[CommonKeys.CHILDREN]
    )

    del invalid_dataset[NodeType.CONFIG][CommonKeys.TYPE]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Type attribute for {attribute_with_dataset_type_to_delete} not found.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_dataset_to_delete", EXPECTED_OFF_TYPES.keys())
def test_GIVEN_unable_to_find_dataset_WHEN_checking_type_THEN_issue_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_dataset_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_dataset_to_delete, off_shape_json[CommonKeys.CHILDREN]
    )

    del invalid_dataset[NodeType.CONFIG][CommonKeys.TYPE]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.issue_message,
            f"Type attribute for {attribute_with_dataset_to_delete} not found.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_values_to_delete", EXPECTED_OFF_TYPES.keys())
def test_GIVEN_missing_values_attribute_WHEN_finding_values_attribute_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_values_to_delete
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_delete, off_shape_json[CommonKeys.CHILDREN]
    )

    del invalid_dataset[NodeType.CONFIG][CommonKeys.VALUES]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"Unable to find values in {attribute_with_values_to_delete} dataset.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_values_to_change", EXPECTED_OFF_TYPES.keys())
def test_GIVEN_values_attribute_is_not_a_list_WHEN_finding_values_attribute_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_values_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_change, off_shape_json[CommonKeys.CHILDREN]
    )

    invalid_dataset[NodeType.CONFIG][CommonKeys.VALUES] = True
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"values attribute in {attribute_with_values_to_change} dataset is not a list.",
        ],
        off_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_with_value_to_change", ["faces", "winding_order"])
def test_GIVEN_value_has_wrong_type_WHEN_validating_value_THEN_error_message_is_created(
    off_shape_reader, off_shape_json, attribute_with_value_to_change
):
    invalid_dataset = off_shape_reader._get_shape_dataset_from_list(
        attribute_with_value_to_change, off_shape_json[CommonKeys.CHILDREN]
    )

    invalid_dataset[NodeType.CONFIG][CommonKeys.VALUES][0] = "astring"
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            f"Values in {attribute_with_value_to_change} list do not all have type(s)",
            EXPECTED_OFF_TYPES[attribute_with_value_to_change],
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_attributes_WHEN_finding_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, off_shape_json[CommonKeys.CHILDREN]
    )

    del vertices_dataset[CommonKeys.ATTRIBUTES]
    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Unable to find attributes list in vertices dataset.",
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_missing_units_WHEN_finding_off_units_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, off_shape_json[CommonKeys.CHILDREN]
    )

    off_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.UNITS, vertices_dataset[CommonKeys.ATTRIBUTES]
    )
    del vertices_dataset[CommonKeys.ATTRIBUTES][0]
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
        CommonAttrs.VERTICES, off_shape_json[CommonKeys.CHILDREN]
    )

    vertices_dataset[CommonKeys.ATTRIBUTES][0][CommonKeys.VALUES] = invalid_units

    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [off_shape_reader.error_message, invalid_units],
        off_shape_reader.warnings,
    )


def test_GIVEN_vertices_cannot_be_converted_to_qvector3D_WHEN_converting_vertices_THEN_error_message_is_created(
    off_shape_reader, off_shape_json
):
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, off_shape_json[CommonKeys.CHILDREN]
    )
    vertices_dataset[NodeType.CONFIG][CommonKeys.VALUES][3] = [4.0, None, None]

    off_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            "Values in vertices list do not all have type(s)",
            EXPECTED_OFF_TYPES[CommonAttrs.VERTICES],
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_off_shape_json_WHEN_reading_shape_THEN_geometry_object_has_expected_properties(
    off_shape_reader, off_shape_json, mock_component
):
    children = off_shape_json[CommonKeys.CHILDREN]

    name = off_shape_json[CommonKeys.NAME]
    vertices_dataset = off_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, children
    )
    vertices = list(
        map(
            lambda vertex: QVector3D(*vertex),
            vertices_dataset[NodeType.CONFIG][CommonKeys.VALUES],
        )
    )
    faces = off_shape_reader._get_shape_dataset_from_list("faces", children)[
        NodeType.CONFIG
    ][CommonKeys.VALUES]
    units = _find_attribute_from_list_or_dict(
        CommonAttrs.UNITS, vertices_dataset[CommonKeys.ATTRIBUTES]
    )
    winding_order = off_shape_reader._get_shape_dataset_from_list(
        "winding_order", children
    )[NodeType.CONFIG][CommonKeys.VALUES]

    off_shape_reader.add_shape_to_component()

    shape = mock_component[SHAPE_GROUP_NAME]
    assert isinstance(shape, OFFGeometryNexus)
    assert shape.nx_class == OFF_GEOMETRY_NX_CLASS
    assert shape.name == name
    assert shape.units == units
    assert shape.get_field_value("faces") == faces
    assert shape.vertices == vertices
    assert shape.winding_order == winding_order


def test_GIVEN_missing_children_attribute_WHEN_reading_cylindrical_information_THEN_error_message_is_created(
    cylindrical_shape_reader, cylindrical_shape_json
):
    del cylindrical_shape_json[CommonKeys.CHILDREN]
    cylindrical_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            cylindrical_shape_reader.error_message,
            "Unable to find children list in shape group.",
        ],
        cylindrical_shape_reader.warnings,
    )


@pytest.mark.parametrize("attribute_to_remove", EXPECTED_CYLINDRICAL_TYPES.keys())
def test_GIVEN_cant_find_attribute_WHEN_reading_cylindrical_information_THEN_error_message_is_created(
    cylindrical_shape_reader, cylindrical_shape_json, attribute_to_remove
):
    attribute = cylindrical_shape_reader._get_shape_dataset_from_list(
        attribute_to_remove, cylindrical_shape_json[CommonKeys.CHILDREN]
    )
    cylindrical_shape_json[CommonKeys.CHILDREN].remove(attribute)

    cylindrical_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [attribute_to_remove, cylindrical_shape_reader.error_message],
        cylindrical_shape_reader.warnings,
    )


def test_GIVEN_missing_units_WHEN_finding_cylindrical_units_THEN_error_message_is_created(
    cylindrical_shape_reader, cylindrical_shape_json
):
    vertices_dataset = cylindrical_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, cylindrical_shape_json[CommonKeys.CHILDREN]
    )

    cylindrical_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.UNITS, vertices_dataset[CommonKeys.ATTRIBUTES]
    )
    del vertices_dataset[CommonKeys.ATTRIBUTES][0]
    cylindrical_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            cylindrical_shape_reader.error_message,
            "Unable to find units attribute in vertices dataset.",
        ],
        cylindrical_shape_reader.warnings,
    )


@pytest.mark.parametrize(
    "attribute_with_values_to_delete", EXPECTED_CYLINDRICAL_TYPES.keys()
)
def test_GIVEN_missing_values_WHEN_finding_cylindrical_values_THEN_error_message_is_created(
    cylindrical_shape_reader, cylindrical_shape_json, attribute_with_values_to_delete
):
    invalid_dataset = cylindrical_shape_reader._get_shape_dataset_from_list(
        attribute_with_values_to_delete, cylindrical_shape_json[CommonKeys.CHILDREN]
    )

    del invalid_dataset[NodeType.CONFIG][CommonKeys.VALUES]
    cylindrical_shape_reader.add_shape_to_component()

    assert _any_warning_message_has_substrings(
        [
            cylindrical_shape_reader.error_message,
            f"Unable to find values in {attribute_with_values_to_delete} dataset.",
        ],
        cylindrical_shape_reader.warnings,
    )


def test_GIVEN_cylindrical_shape_json_WHEN_reading_shape_THEN_geometry_object_has_expected_properties(
    cylindrical_shape_reader, cylindrical_shape_json, mock_component
):
    name = cylindrical_shape_json[CommonKeys.NAME]
    vertices_dataset = cylindrical_shape_reader._get_shape_dataset_from_list(
        CommonAttrs.VERTICES, cylindrical_shape_json[CommonKeys.CHILDREN]
    )
    vertices = vertices_dataset[NodeType.CONFIG][CommonKeys.VALUES]
    units = _find_attribute_from_list_or_dict(
        CommonAttrs.UNITS, vertices_dataset[CommonKeys.ATTRIBUTES]
    )
    cylinders_list = cylindrical_shape_reader._get_shape_dataset_from_list(
        "cylinders", cylindrical_shape_json[CommonKeys.CHILDREN]
    )[NodeType.CONFIG][CommonKeys.VALUES]

    cylindrical_shape_reader.add_shape_to_component()

    shape = mock_component[name]

    assert isinstance(shape, CylindricalGeometry)
    assert shape.name == name
    assert shape.nx_class == CYLINDRICAL_GEOMETRY_NX_CLASS
    assert shape.units == units
    assert np.allclose(shape.get_field_value("cylinders"), np.array(cylinders_list))
    assert np.allclose(shape.get_field_value(CommonAttrs.VERTICES), np.vstack(vertices))


def test_GIVEN_no_detector_number_dataset_and_no_pixel_shape_WHEN_reading_pixel_data_THEN_set_field_value_is_never_called(
    off_shape_reader, pixel_grid_list, mock_component
):
    pixel_grid_list.remove(
        off_shape_reader._get_shape_dataset_from_list(DETECTOR_NUMBER, pixel_grid_list)
    )

    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    # set field value is never called because the detector number dataset couldn't be found, and the shape is not a
    # pixel shape
    mock_component.set_field_value.assert_not_called()
    # no warning is created because the absence of a detector number dataset is not a problem in the case of "shape"
    assert not off_shape_reader.warnings


def test_GIVEN_pixel_shape_and_no_detector_number_WHEN_reading_pixel_data_THEN_error_message_is_created(
    off_shape_reader, pixel_grid_list, mock_component
):
    pixel_grid_list.remove(
        off_shape_reader._get_shape_dataset_from_list(DETECTOR_NUMBER, pixel_grid_list)
    )

    off_shape_reader.shape_info[CommonKeys.NAME] = PIXEL_SHAPE_GROUP_NAME
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    assert _any_warning_message_has_substrings(
        [off_shape_reader.error_message, DETECTOR_NUMBER], off_shape_reader.warnings
    )


@pytest.mark.parametrize("offset_to_delete", [X_PIXEL_OFFSET, Y_PIXEL_OFFSET])
def test_GIVEN_pixel_shape_and_no_x_y_offset_WHEN_reading_pixel_data_THEN_error_message_is_created(
    off_shape_reader, pixel_grid_list, offset_to_delete, mock_off_shape
):
    pixel_grid_list.remove(
        off_shape_reader._get_shape_dataset_from_list(offset_to_delete, pixel_grid_list)
    )

    off_shape_reader.shape = mock_off_shape
    off_shape_reader.shape_info[CommonKeys.NAME] = PIXEL_SHAPE_GROUP_NAME
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    assert _any_warning_message_has_substrings(
        [off_shape_reader.error_message, offset_to_delete], off_shape_reader.warnings
    )


def test_GIVEN_pixel_shape_and_no_z_offset_WHEN_reading_pixel_data_THEN_error_message_is_not_created(
    off_shape_reader, pixel_grid_list, mock_off_shape
):
    off_shape_reader.shape = mock_off_shape
    off_shape_reader.shape_info[CommonKeys.NAME] = PIXEL_SHAPE_GROUP_NAME
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    assert not _any_warning_message_has_substrings(
        [Z_PIXEL_OFFSET], off_shape_reader.warnings
    )


@pytest.mark.parametrize("offset_to_corrupt", [X_PIXEL_OFFSET, Y_PIXEL_OFFSET])
def test_GIVEN_x_y_offset_exists_but_fails_validation_WHEN_reading_pixel_data_THEN_error_message_is_created(
    off_shape_reader, pixel_grid_list, offset_to_corrupt, mock_off_shape
):
    offset_dataset = off_shape_reader._get_shape_dataset_from_list(
        offset_to_corrupt, pixel_grid_list
    )
    offset_dataset[NodeType.CONFIG][CommonKeys.VALUES][0] = "not a float"

    off_shape_reader.shape = mock_off_shape
    off_shape_reader.shape_info[CommonKeys.NAME] = PIXEL_SHAPE_GROUP_NAME
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    assert _any_warning_message_has_substrings(
        [
            off_shape_reader.error_message,
            offset_to_corrupt,
            "do not all have type(s)",
            ValueTypes.FLOAT,
        ],
        off_shape_reader.warnings,
    )


def test_GIVEN_valid_pixel_grid_WHEN_reading_pixel_data_THEN_set_field_value_is_called_with_expected_values(
    off_shape_reader, pixel_grid_list, mock_component, mock_off_shape
):
    off_shape_reader.shape = mock_off_shape
    off_shape_reader.shape_info[CommonKeys.NAME] = PIXEL_SHAPE_GROUP_NAME
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    detector_number_dataset = off_shape_reader._get_shape_dataset_from_list(
        DETECTOR_NUMBER, pixel_grid_list
    )
    detector_number = detector_number_dataset[NodeType.CONFIG][CommonKeys.VALUES]
    detector_number_dtype = _get_data_type(detector_number_dataset[NodeType.CONFIG])

    x_offset_dataset = off_shape_reader._get_shape_dataset_from_list(
        X_PIXEL_OFFSET, pixel_grid_list
    )
    x_pixel_offset = np.array(x_offset_dataset[NodeType.CONFIG][CommonKeys.VALUES])
    x_pixel_dtype = _get_data_type(x_offset_dataset[NodeType.CONFIG])

    y_offset_dataset = off_shape_reader._get_shape_dataset_from_list(
        Y_PIXEL_OFFSET, pixel_grid_list
    )
    y_pixel_offset = np.array(y_offset_dataset[NodeType.CONFIG][CommonKeys.VALUES])
    y_pixel_dtype = _get_data_type(y_offset_dataset[NodeType.CONFIG])

    mock_component.set_field_value.assert_has_calls(
        [
            call(
                DETECTOR_NUMBER,
                detector_number,
                detector_number_dtype,
            )
        ]
    )

    assert X_PIXEL_OFFSET == mock_component.set_field_value.call_args_list[1].args[0]
    np.array_equal(
        x_pixel_offset, mock_component.set_field_value.call_args_list[1].args[1]
    )
    assert x_pixel_dtype == mock_component.set_field_value.call_args_list[1].args[2]

    assert Y_PIXEL_OFFSET == mock_component.set_field_value.call_args_list[2].args[0]
    np.array_equal(
        y_pixel_offset, mock_component.set_field_value.call_args_list[2].args[1]
    )
    assert y_pixel_dtype == mock_component.set_field_value.call_args_list[2].args[2]


def test_GIVEN_valid_pixel_mapping_and_cylindrical_shape_WHEN_reading_pixel_data_THEN_set_field_value_is_called_with_expected_values(
    off_shape_reader, pixel_grid_list, mock_component, mock_cylindrical_shape
):
    off_shape_reader.shape = mock_cylindrical_shape
    off_shape_reader.add_pixel_data_to_component(pixel_grid_list)

    detector_number_dataset = off_shape_reader._get_shape_dataset_from_list(
        DETECTOR_NUMBER, pixel_grid_list
    )
    detector_number = detector_number_dataset[NodeType.CONFIG][CommonKeys.VALUES]
    detector_number_dtype = _get_data_type(detector_number_dataset[NodeType.CONFIG])

    mock_component.set_field_value.assert_called_once_with(
        DETECTOR_NUMBER, detector_number, detector_number_dtype
    )
    assert mock_cylindrical_shape.detector_number == detector_number


def test_GIVEN_box_shape_json_WHEN_reading_shape_THEN_geometry_object_has_expected_properties(
    box_shape_reader, box_shape_json, mock_component
):
    name = box_shape_json[CommonKeys.NAME]
    box_shape_reader.add_shape_to_component()
    shape = mock_component[name]
    assert isinstance(shape, BoxGeometry)
    assert shape.name == name
    assert shape.nx_class == GEOMETRY_NX_CLASS
    assert shape.size[0] == 6.0
    assert shape.size[1] == 12.0
    assert shape.size[2] == 15.0
    assert shape.units == "m"
    assert shape.name == GEOMETRY_GROUP_NAME
