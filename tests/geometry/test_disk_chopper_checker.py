from typing import Any

import numpy as np
import pytest

from nexus_constructor.common_attrs import CommonAttrs
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
def slits_dataset():
    dtype = ValueTypes.INT
    slits_dataset = create_dataset(SLITS_NAME, dtype, N_SLITS)
    slits_dataset.type = dtype
    return slits_dataset


@pytest.fixture(scope="function")
def slit_edges_dataset():
    dtype = ValueTypes.FLOAT
    slit_edges_dataset: Dataset = create_dataset(
        SLIT_EDGES_NAME, dtype, np.array(DEGREES_EDGES_ARR)
    )
    slit_edges_dataset.type = dtype
    slit_edges_dataset.attributes.set_attribute_value(CommonAttrs.UNITS, "deg")
    return slit_edges_dataset


@pytest.fixture(scope="function")
def radius_dataset():
    dtype = ValueTypes.FLOAT
    radius_dataset = create_dataset(RADIUS_NAME, dtype, RADIUS_LENGTH)
    radius_dataset.type = dtype
    radius_dataset.attributes.set_attribute_value(CommonAttrs.UNITS, "m")
    return radius_dataset


@pytest.fixture(scope="function")
def slit_height_dataset():
    dtype = ValueTypes.FLOAT
    slit_height_dataset = create_dataset(SLIT_HEIGHT_NAME, dtype, SLIT_HEIGHT_LENGTH)
    slit_height_dataset.type = dtype
    slit_height_dataset.attributes.set_attribute_value(CommonAttrs.UNITS, "m")
    return slit_height_dataset


@pytest.fixture(scope="function")
def field_list(
    slits_dataset,
    slit_edges_dataset,
    radius_dataset,
    slit_height_dataset,
):
    return [
        slits_dataset,
        slit_edges_dataset,
        radius_dataset,
        slit_height_dataset,
    ]


@pytest.fixture(scope="function")
def fields_dict(
    slits_dataset,
    slit_edges_dataset,
    radius_dataset,
    slit_height_dataset,
):

    return {
        SLITS_NAME: slits_dataset,
        SLIT_EDGES_NAME: slit_edges_dataset,
        RADIUS_NAME: radius_dataset,
        SLIT_HEIGHT_NAME: slit_height_dataset,
    }


@pytest.fixture(scope="function")
def units_dict(radius_dataset, slit_edges_dataset, slit_height_dataset):
    return {
        RADIUS_NAME: radius_dataset.attributes.get_attribute_value(CommonAttrs.UNITS),
        SLIT_EDGES_NAME: slit_edges_dataset.attributes.get_attribute_value(
            CommonAttrs.UNITS
        ),
        SLIT_HEIGHT_NAME: slit_height_dataset.attributes.get_attribute_value(
            CommonAttrs.UNITS
        ),
    }


@pytest.fixture(scope="function")
def chopper_checker(field_list):
    return ChopperChecker(field_list)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true(
    chopper_checker,
):
    assert chopper_checker._check_data_type(RADIUS_NAME, FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false(
    chopper_checker,
):
    assert not chopper_checker._check_data_type(SLITS_NAME, FLOAT_TYPES)


def test_GIVEN_fields_information_and_field_name_WHEN_calling_incorrect_field_type_message_THEN_expected_string_is_returned(
    radius_dataset,
):
    wrong_data_type = ValueTypes.STRING
    radius_dataset.type = wrong_data_type
    field_dict = {RADIUS_NAME: radius_dataset}
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
    chopper_checker, fields_dict
):
    fields_dict[SLITS_NAME].type = FLOAT_TYPES[0]
    chopper_checker.fields_dict = fields_dict
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
    chopper_checker, slit_edges_dataset
):
    assert chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_invalid_shape_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].values = np.array(
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)]
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLITS_NAME] = create_dataset(
        SLITS_NAME, ValueTypes.INT, 5
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLITS_NAME] = create_dataset(
        SLITS_NAME, ValueTypes.INT, 201
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    dataset_val = 20
    slit_height_dataset = create_dataset(SLIT_HEIGHT_NAME, ValueTypes.INT, dataset_val)

    chopper_checker.fields_dict[SLIT_HEIGHT_NAME].value = slit_height_dataset
    chopper_checker.fields_dict[RADIUS_NAME].values = dataset_val

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values[0],
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values[1],
    ) = (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values[1],
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values[0],
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].values[
        0
    ] = chopper_checker.fields_dict[SLIT_EDGES_NAME].values[1]

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker,
):
    chopper_checker.fields_dict[SLIT_EDGES_NAME].values[-1] = (
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values[0] + 365
    )

    assert chopper_checker.required_fields_present()
    assert chopper_checker._data_has_correct_type()
    assert _edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.ndim,
        chopper_checker.fields_dict[SLIT_EDGES_NAME].values.shape,
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
    print(chopper_checker.fields_dict.keys())
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
    slit_edges_dataset,
    slits_dataset,
    radius_dataset,
    slit_height_dataset,
):
    chopper_checker.validate_chopper()
    details = chopper_checker.chopper_details

    assert np.allclose(details.slit_edges, RADIANS_EDGES_ARR)
    assert details.slits == int(slits_dataset.values)
    assert details.radius == pytest.approx(float(radius_dataset.values))
    assert details.slit_height == pytest.approx(float(slit_height_dataset.values))


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
    chopper_checker, slit_edges_dataset, units_attribute
):

    slit_edges_dataset.value = create_dataset(
        SLIT_EDGES_NAME, ValueTypes.FLOAT, RADIANS_EDGES_ARR
    )
    slit_edges_dataset.units = units_attribute
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
    chopper_checker.fields_dict[field_name] = create_dataset(
        field_name, chopper_checker.fields_dict[field_name].type, "cantbeconverted"
    )
    assert not chopper_checker._data_can_be_converted()


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_arent_recognised_by_pint_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict, field
):

    units_dict[field] = "burger"
    assert not _units_are_valid(units_dict)


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_have_wrong_dimensionality_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict, field
):

    units_dict[field] = "nanoseconds"
    assert not _units_are_valid(units_dict)


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_units_have_wrong_magnitude_WHEN_validating_units_THEN_units_are_valid_returns_false(
    units_dict, field
):

    units_dict[field] = "2 " + units_dict[field]
    assert not _units_are_valid(units_dict)


@pytest.mark.parametrize(
    "field", [SLITS_NAME, RADIUS_NAME, SLIT_HEIGHT_NAME, SLIT_EDGES_NAME]
)
def test_GIVEN_fields_have_wrong_type_WHEN_validating_fields_THEN_data_has_correct_type_returns_false(
    chopper_checker, field
):

    chopper_checker.fields_dict[field].type = ValueTypes.STRING
    assert not chopper_checker._data_has_correct_type()


@pytest.mark.parametrize("field", UNITS_REQUIRED)
def test_GIVEN_missing_units_WHEN_validating_chopper_THEN_required_fields_present_returns_false(
    chopper_checker, field
):

    chopper_checker.fields_dict[field].attributes.set_attribute_value(
        CommonAttrs.UNITS, ""
    )
    assert not chopper_checker.required_fields_present()


def test_GIVEN_qlistwidget_WHEN_initialising_chopper_checker_THEN_fields_dict_contents_matches_widgets(
    chopper_checker,
    slits_dataset,
    radius_dataset,
    slit_height_dataset,
    slit_edges_dataset,
):
    assert chopper_checker.fields_dict[SLITS_NAME] == slits_dataset
    assert chopper_checker.fields_dict[RADIUS_NAME] == radius_dataset
    assert chopper_checker.fields_dict[SLIT_HEIGHT_NAME] == slit_height_dataset
    assert chopper_checker.fields_dict[SLIT_EDGES_NAME] == slit_edges_dataset


def test_GIVEN_units_input_WHEN_checking_required_fields_are_present_THEN_units_dict_contents_matches_widgets(
    chopper_checker, radius_dataset, slit_height_dataset, slit_edges_dataset
):

    chopper_checker.required_fields_present()

    assert chopper_checker.units_dict[
        RADIUS_NAME
    ] == radius_dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
    assert chopper_checker.units_dict[
        SLIT_HEIGHT_NAME
    ] == slit_height_dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
    assert chopper_checker.units_dict[
        SLIT_EDGES_NAME
    ] == slit_edges_dataset.attributes.get_attribute_value(CommonAttrs.UNITS)
