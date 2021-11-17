from typing import Any

import numpy as np
import pytest
from mock import Mock
from PySide2.QtWidgets import QListWidget

from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    FLOAT_TYPES,
    RADIUS_NAME,
    SLIT_EDGES_NAME,
    SLIT_HEIGHT_NAME,
    SLITS_NAME,
    UNITS_REQUIRED,
    ChopperChecker,
    _edges_array_has_correct_shape,
    _incorrect_data_type_message,
    _units_are_valid,
)
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes
from tests.geometry.chopper_test_helpers import (  # noqa: F401
    DEGREES_EDGES_ARR,
    N_SLITS,
    RADIANS_EDGES_ARR,
    RADIUS_LENGTH,
    SLIT_HEIGHT_LENGTH,
)


def create_dataset(name: str, dtype: str, val: Any):
    if np.isscalar(val):
        return Dataset(parent_node=None, name=name, type=dtype, values=str(val))
    return Dataset(parent_node=None, name=name, type=dtype, values=val)


@pytest.fixture(scope="function")
def mock_slits_widget():
    dtype = ValueTypes.INT
    mock_slits_widget = Mock(spec=FieldWidget)
    mock_slits_widget.name = SLITS_NAME
    mock_slits_widget.value = create_dataset(SLITS_NAME, dtype, N_SLITS)
    mock_slits_widget.dtype = dtype

    return mock_slits_widget


@pytest.fixture(scope="function")
def mock_slit_edges_widget():
    dtype = ValueTypes.FLOAT
    mock_slit_edges_widget = Mock(spec=FieldWidget)
    mock_slit_edges_widget.name = SLIT_EDGES_NAME
    mock_slit_edges_widget.value = create_dataset(
        SLIT_EDGES_NAME, dtype, np.array(DEGREES_EDGES_ARR)
    )
    mock_slit_edges_widget.dtype = dtype
    mock_slit_edges_widget.units = "deg"
    return mock_slit_edges_widget


@pytest.fixture(scope="function")
def mock_radius_widget():
    dtype = ValueTypes.FLOAT
    mock_radius_widget = Mock(spec=FieldWidget)
    mock_radius_widget.name = RADIUS_NAME
    mock_radius_widget.value = create_dataset(RADIUS_NAME, dtype, RADIUS_LENGTH)
    mock_radius_widget.dtype = dtype
    mock_radius_widget.units = "m"

    return mock_radius_widget


@pytest.fixture(scope="function")
def mock_slit_height_widget():
    dtype = ValueTypes.FLOAT
    mock_slit_height_widget = Mock(spec=FieldWidget)
    mock_slit_height_widget.name = SLIT_HEIGHT_NAME
    mock_slit_height_widget.value = create_dataset(
        SLIT_HEIGHT_NAME, dtype, SLIT_HEIGHT_LENGTH
    )
    mock_slit_height_widget.dtype = dtype
    mock_slit_height_widget.units = "m"

    return mock_slit_height_widget


@pytest.fixture(scope="function")
def mock_widget_list(
    mock_slits_widget,
    mock_slit_edges_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):

    return [
        mock_slits_widget,
        mock_slit_edges_widget,
        mock_radius_widget,
        mock_slit_height_widget,
    ]


@pytest.fixture(scope="function")
def mock_fields_list_widget(
    mock_widget_list,
):
    list_widget = Mock(spec=QListWidget)
    list_widget.count = Mock(return_value=len(mock_widget_list))

    list_widget.itemWidget = Mock(side_effect=mock_widget_list)

    return list_widget


@pytest.fixture(scope="function")
def fields_dict_mocks(
    mock_slits_widget,
    mock_slit_edges_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):

    return {
        SLITS_NAME: mock_slits_widget,
        SLIT_EDGES_NAME: mock_slit_edges_widget,
        RADIUS_NAME: mock_radius_widget,
        SLIT_HEIGHT_NAME: mock_slit_height_widget,
    }


@pytest.fixture(scope="function")
def units_dict_mocks(
    mock_radius_widget, mock_slit_edges_widget, mock_slit_height_widget
):
    return {
        RADIUS_NAME: mock_radius_widget.units,
        SLIT_EDGES_NAME: mock_slit_edges_widget.units,
        SLIT_HEIGHT_NAME: mock_slit_height_widget.units,
    }


@pytest.fixture(scope="function")
def chopper_checker(mock_fields_list_widget):
    return ChopperChecker(mock_fields_list_widget)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true(
    chopper_checker,
):
    assert chopper_checker._check_data_type(RADIUS_NAME, FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false(
    chopper_checker,
):
    assert not chopper_checker._check_data_type(SLITS_NAME, FLOAT_TYPES)


def test_GIVEN_fields_information_and_field_name_WHEN_calling_incorrect_field_type_message_THEN_expected_string_is_returned(
    mock_radius_widget,
):
    wrong_data_type = ValueTypes.STRING
    mock_radius_widget.dtype = wrong_data_type
    field_dict = {RADIUS_NAME: mock_radius_widget}
    error_message = _incorrect_data_type_message(
        field_dict, RADIUS_NAME, ValueTypes.FLOAT
    )

    assert (
        error_message
        == "Wrong radius type. Expected float but found " + wrong_data_type + "."
    )


def test_GIVEN_valid_fields_information_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_true(
    chopper_checker,
):
    assert chopper_checker._data_has_correct_type()


def test_GIVEN_invalid_slits_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    chopper_checker, fields_dict_mocks
):
    fields_dict_mocks[SLITS_NAME].dtype = FLOAT_TYPES[0]
    chopper_checker.fields_dict = fields_dict_mocks
    assert not chopper_checker._data_has_correct_type()


def test_GIVEN_edges_array_with_valid_shape_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():
    valid_array = np.array([i for i in range(6)])
    assert _edges_array_has_correct_shape(valid_array.ndim, valid_array.shape)


def test_GIVEN_edges_array_with_more_than_two_dimensions_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_false():
    three_dim_array = np.ones(shape=(5, 5, 5))
    assert not _edges_array_has_correct_shape(
        three_dim_array.ndim, three_dim_array.shape
    )


def test_GIVEN_edges_array_with_two_dimensions_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_false():
    two_dim_array = np.ones(shape=(5, 5))
    assert not _edges_array_has_correct_shape(two_dim_array.ndim, two_dim_array.shape)


def test_GIVEN_column_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():
    column_array = np.ones(shape=(5, 1))
    assert _edges_array_has_correct_shape(column_array.ndim, column_array.shape)


def test_GIVEN_row_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():
    row_array = np.ones(shape=(1, 5))
    assert _edges_array_has_correct_shape(row_array.ndim, row_array.shape)


def test_GIVEN_valid_values_WHEN_validating_chopper_input_THEN_returns_true(
    chopper_checker, mock_slit_edges_widget
):
    assert chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_invalid_shape_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values = np.array(
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)]
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLITS_NAME].value = create_dataset(
        SLITS_NAME, ValueTypes.INT, 5
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLITS_NAME].value = create_dataset(
        SLITS_NAME, ValueTypes.INT, 201
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    dataset_val = 20
    slit_height_dataset = create_dataset(SLIT_HEIGHT_NAME, ValueTypes.INT, dataset_val)

    chopper_checker.fields_dict[SLIT_HEIGHT_NAME].value = slit_height_dataset
    chopper_checker.fields_dict[RADIUS_NAME].value.values = dataset_val

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[0],
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[1],
    ) = (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[1],
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[0],
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[
        0
    ] = chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[1]

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[-1] = (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values[0] + 365
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].value.values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slits_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    del chopper_checker.fields_dict[SLITS_NAME]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    del chopper_checker.fields_dict[SLIT_EDGES_NAME]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_radius_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    del chopper_checker.fields_dict[RADIUS_NAME]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    del chopper_checker.fields_dict[SLIT_HEIGHT_NAME]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_chopper_details_WHEN_creating_chopper_geometry_THEN_details_matches_fields_widget_input(
    chopper_checker,
    mock_slit_edges_widget,
    mock_slits_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):
    chopper_checker.validate_chopper()
    details = chopper_checker.chopper_details

    assert np.allclose(details.slit_edges, RADIANS_EDGES_ARR)
    assert details.slits == int(mock_slits_widget.value.values)
    assert details.radius == pytest.approx(float(mock_radius_widget.value.values))
    assert details.slit_height == pytest.approx(
        float(mock_slit_height_widget.value.values)
    )


def test_GIVEN_nothing_WHEN_calling_get_chopper_details_THEN_expected_chopper_details_are_returned(
    chopper_checker,
):
    chopper_checker.validate_chopper()
    chopper_details = chopper_checker.chopper_details

    assert chopper_details.slits == N_SLITS
    assert chopper_details.radius == pytest.approx(RADIUS_LENGTH)
    assert chopper_details.slit_height == pytest.approx(SLIT_HEIGHT_LENGTH)
    assert np.allclose(chopper_details.slit_edges, RADIANS_EDGES_ARR)


@pytest.mark.parametrize("units_attribute", ["radians", "rad", "radian"])
def test_chopper_checker_GIVEN_different_ways_of_writing_radians_WHEN_creating_chopper_details_THEN_slit_edges_array_has_expected_values(
    chopper_checker, mock_slit_edges_widget, units_attribute
):

    mock_slit_edges_widget.value = create_dataset(
        SLIT_EDGES_NAME, ValueTypes.FLOAT, RADIANS_EDGES_ARR
    )
    mock_slit_edges_widget.units = units_attribute
    chopper_checker.validate_chopper()
    assert np.allclose(chopper_checker.chopper_details.slit_edges, RADIANS_EDGES_ARR)


def test_GIVEN_all_data_can_be_converted_WHEN_validating_chopper_THEN_data_can_be_converted_returns_true(
    chopper_checker,
):
    assert chopper_checker._data_can_be_converted()


@pytest.mark.parametrize("field_name", [SLITS_NAME, RADIUS_NAME, SLIT_HEIGHT_NAME])
def test_GIVEN_failed_conversion_WHEN_validating_chopper_THEN_data_can_be_converted_returns_false(
    chopper_checker, field_name
):
    chopper_checker.fields_dict[field_name].value = create_dataset(
        field_name, chopper_checker.fields_dict[field_name].dtype, "cantbeconverted"
    )
    assert not chopper_checker._data_can_be_converted()


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_arent_recognised_by_pint_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict_mocks, field
):

    units_dict_mocks[field] = "burger"
    assert not _units_are_valid(units_dict_mocks)


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_have_wrong_dimensionality_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict_mocks, field
):

    units_dict_mocks[field] = "nanoseconds"
    assert not _units_are_valid(units_dict_mocks)


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_have_wrong_magnitude_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict_mocks, field
):

    units_dict_mocks[field] = "2 " + units_dict_mocks[field]
    assert not _units_are_valid(units_dict_mocks)


@pytest.mark.parametrize(
    "field", [SLITS_NAME, RADIUS_NAME, SLIT_HEIGHT_NAME, SLIT_EDGES_NAME]
)
def test_GIVEN_fields_have_wrong_type_WHEN_validating_fields_THEN_data_has_correct_type_returns_false(
    chopper_checker, field
):

    chopper_checker.fields_dict[field].dtype = ValueTypes.STRING
    assert not chopper_checker._data_has_correct_type()


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_missing_units_WHEN_validating_chopper_THEN_required_fields_present_returns_false(
    chopper_checker, field
):

    chopper_checker.fields_dict[field].units = ""
    assert not chopper_checker.required_fields_present()


def test_GIVEN_qlistwidget_WHEN_initialising_chopper_checker_THEN_fields_dict_contents_matches_widgets(
    chopper_checker,
    mock_slits_widget,
    mock_radius_widget,
    mock_slit_height_widget,
    mock_slit_edges_widget,
):
    assert chopper_checker.fields_dict[SLITS_NAME] == mock_slits_widget
    assert chopper_checker.fields_dict[RADIUS_NAME] == mock_radius_widget
    assert chopper_checker.fields_dict[SLIT_HEIGHT_NAME] == mock_slit_height_widget
    assert chopper_checker.fields_dict[SLIT_EDGES_NAME] == mock_slit_edges_widget


def test_GIVEN_units_input_WHEN_checking_required_fields_are_present_THEN_units_dict_contents_matches_widgets(
    chopper_checker, mock_radius_widget, mock_slit_height_widget, mock_slit_edges_widget
):

    chopper_checker.required_fields_present()

    assert chopper_checker.units_dict[RADIUS_NAME] == mock_radius_widget.units
    assert chopper_checker.units_dict[SLIT_HEIGHT_NAME] == mock_slit_height_widget.units
    assert chopper_checker.units_dict[SLIT_EDGES_NAME] == mock_slit_edges_widget.units
