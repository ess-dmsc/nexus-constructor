import pytest
import numpy as np

from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    SLITS_NAME,
    SLIT_HEIGHT_NAME,
    RADIUS_NAME,
    SLIT_EDGES_NAME,
    NexusDefinedChopperChecker,
    NAME,
    UNITS_REQUIRED,
    EXPECTED_UNIT_TYPE,
    _check_data_type,
    FLOAT_TYPES,
    _incorrect_data_type_message,
    INT_TYPES,
    REQUIRED_CHOPPER_FIELDS,
)
from tests.chopper_test_helpers import (  # noqa: F401
    N_SLITS,
    RADIUS_LENGTH,
    SLIT_HEIGHT_LENGTH,
    RADIANS_EDGES_ARR,
)
from tests.helpers import InMemoryFile

IMPROPER_UNITS = {
    SLIT_EDGES_NAME: "lumen",
    SLIT_HEIGHT_NAME: "terabytes",
    RADIUS_NAME: "rutherford",
}


def value_side_effect(given_key, expected_key, data):
    """
    Function for mimicking a call to dataset.value[()] or dataset.attrs[attribute_name]
    :param given_key: The key passed to __getitem__
    :param expected_key: The key which stores the data.
    :param data: The data returned from the call.
    :return: data if the correct key has been provided, otherwise a KeyError is raised.
    """
    if given_key == expected_key:
        return data
    raise KeyError


def change_nexus_value(chopper_group, field_name, new_value, units: str = None):

    del chopper_group[field_name]
    chopper_group[field_name] = new_value
    if units is not None:
        chopper_group[field_name].attrs["units"] = str.encode(units)


@pytest.fixture(scope="function")
def units_dict():
    return {RADIUS_NAME: "m", SLIT_EDGES_NAME: "rad", SLIT_HEIGHT_NAME: "m"}


@pytest.fixture(scope="function")
def fields_dict():
    return {
        SLITS_NAME: N_SLITS,
        RADIUS_NAME: RADIUS_LENGTH,
        SLIT_EDGES_NAME: RADIANS_EDGES_ARR,
        SLIT_HEIGHT_NAME: SLIT_HEIGHT_LENGTH,
    }


@pytest.fixture(scope="function")
def nexus_disk_chopper():
    with InMemoryFile("test_disk_chopper") as nexus_file:
        disk_chopper_group = nexus_file.create_group("Disk Chopper")
        disk_chopper_group[NAME] = "abc"
        disk_chopper_group[SLITS_NAME] = N_SLITS
        disk_chopper_group[SLIT_EDGES_NAME] = RADIANS_EDGES_ARR
        disk_chopper_group[RADIUS_NAME] = RADIUS_LENGTH
        disk_chopper_group[SLIT_HEIGHT_NAME] = SLIT_HEIGHT_LENGTH
        disk_chopper_group[SLIT_EDGES_NAME].attrs["units"] = str.encode("rad")
        disk_chopper_group[RADIUS_NAME].attrs["units"] = str.encode("m")
        disk_chopper_group[SLIT_HEIGHT_NAME].attrs["units"] = str.encode("m")
        yield disk_chopper_group


@pytest.fixture(scope="function")
def nexus_defined_chopper_checker(nexus_disk_chopper):
    return NexusDefinedChopperChecker(nexus_disk_chopper)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true(
    nexus_disk_chopper
):
    assert _check_data_type(nexus_disk_chopper[SLIT_EDGES_NAME][()], FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false(
    nexus_disk_chopper
):
    assert not _check_data_type(nexus_disk_chopper[SLIT_EDGES_NAME][()], INT_TYPES)


def test_GIVEN_fields_information_and_field_name_WHEN_calling_incorrect_field_type_message_THEN_expected_string_is_returned(
    fields_dict
):
    field_dict = {RADIUS_NAME: "string"}
    error_message = _incorrect_data_type_message(field_dict, RADIUS_NAME, "float")

    assert (
        error_message
        == "Wrong radius type. Expected float but found "
        + str(type(field_dict[RADIUS_NAME]))
        + "."
    )


@pytest.mark.parametrize("field_that_needs_units", UNITS_REQUIRED)
def test_GIVEN_invalid_units_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict, units_dict, field_that_needs_units, nexus_defined_chopper_checker
):
    units_dict[field_that_needs_units] = 123
    assert not nexus_defined_chopper_checker.data_has_correct_type(
        fields_dict, units_dict
    )


@pytest.mark.parametrize("required_field", REQUIRED_CHOPPER_FIELDS)
def test_GIVEN_invalid_field_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict, units_dict, required_field, nexus_defined_chopper_checker
):
    fields_dict[required_field] = False
    assert not nexus_defined_chopper_checker.data_has_correct_type(
        fields_dict, units_dict
    )


def test_GIVEN_edges_array_with_two_dimensions_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_false(
    nexus_defined_chopper_checker
):
    two_dim_array = np.ones(shape=(5, 5))
    assert not nexus_defined_chopper_checker.edges_array_has_correct_shape(
        two_dim_array.ndim, two_dim_array.shape
    )


def test_GIVEN_column_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true(
    nexus_defined_chopper_checker
):
    column_array = np.ones(shape=(5, 1))
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        column_array.ndim, column_array.shape
    )


def test_GIVEN_row_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true(
    nexus_defined_chopper_checker
):
    row_array = np.ones(shape=(1, 5))
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        row_array.ndim, row_array.shape
    )


def test_GIVEN_slit_edges_array_with_invalid_shape_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    change_nexus_value(
        nexus_disk_chopper,
        SLIT_EDGES_NAME,
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)],
        "rad",
    )

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert not nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    change_nexus_value(nexus_disk_chopper, SLITS_NAME, 200)

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    change_nexus_value(nexus_disk_chopper, SLIT_HEIGHT_NAME, 200000.1, "m")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    change_nexus_value(nexus_disk_chopper, SLIT_HEIGHT_NAME, 200000.1, "m")
    change_nexus_value(nexus_disk_chopper, RADIUS_NAME, 200000.1, "m")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    reversed_array = np.flip(RADIANS_EDGES_ARR)
    change_nexus_value(nexus_disk_chopper, SLIT_EDGES_NAME, reversed_array, "rad")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    repeating_array = np.copy(RADIANS_EDGES_ARR)
    repeating_array[0] = repeating_array[1]
    change_nexus_value(nexus_disk_chopper, SLIT_EDGES_NAME, repeating_array, "rad")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    overlapping_array = np.copy(RADIANS_EDGES_ARR)
    overlapping_array[-1] = (
        overlapping_array[0]
        + (2 * np.pi)
        + (overlapping_array[1] - overlapping_array[0]) * 0.5
    )
    change_nexus_value(nexus_disk_chopper, SLIT_EDGES_NAME, overlapping_array, "rad")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )
    assert nexus_defined_chopper_checker.edges_array_has_correct_shape(
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].ndim,
        nexus_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].shape,
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_field_has_wrong_type_WHEN_validating_chopper_input_THEN_valid_chopper_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_dict
):
    change_nexus_value(nexus_disk_chopper, SLITS_NAME, "5")

    assert nexus_defined_chopper_checker.required_fields_present()
    assert not nexus_defined_chopper_checker.data_has_correct_type(
        nexus_defined_chopper_checker.fields_dict, units_dict
    )


def test_GIVEN_chopper_details_WHEN_creating_chopper_geometry_THEN_details_matches_nexus_group(
    nexus_defined_chopper_checker, nexus_disk_chopper
):
    nexus_defined_chopper_checker.validate_chopper()
    details = nexus_defined_chopper_checker.chopper_details

    assert np.allclose(details.slit_edges, nexus_disk_chopper[SLIT_EDGES_NAME][()])
    assert details.slits == nexus_disk_chopper[SLITS_NAME][()]
    assert details.radius == pytest.approx(nexus_disk_chopper[RADIUS_NAME][()])
    assert details.slit_height == pytest.approx(
        nexus_disk_chopper[SLIT_HEIGHT_NAME][()]
    )


def test_GIVEN_valid_nexus_disk_chopper_WHEN_validating_disk_chopper_THEN_validate_chopper_returns_true(
    nexus_defined_chopper_checker
):
    assert nexus_defined_chopper_checker.validate_chopper()


@pytest.mark.parametrize("required_field", REQUIRED_CHOPPER_FIELDS)
def test_GIVEN_nexus_disk_chopper_with_no_slits_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker, required_field, nexus_disk_chopper
):
    del nexus_defined_chopper_checker._disk_chopper[required_field]
    assert not nexus_defined_chopper_checker.required_fields_present()


@pytest.mark.parametrize("field_that_needs_units", UNITS_REQUIRED)
def test_user_defined_chopper_checker_GIVEN_units_missing_WHEN_checking_that_required_fields_are_present_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper, field_that_needs_units
):
    del nexus_disk_chopper[field_that_needs_units].attrs["units"]
    assert not nexus_defined_chopper_checker.required_fields_present()


@pytest.mark.parametrize("field_that_needs_units", UNITS_REQUIRED)
def test_chopper_checker_GIVEN_input_cant_be_converted_to_any_units_WHEN_validating_units_THEN_returns_false(
    field_that_needs_units, units_dict, nexus_defined_chopper_checker
):
    units_dict[field_that_needs_units] = "notaunit"
    assert not nexus_defined_chopper_checker.units_are_valid(units_dict)


@pytest.mark.parametrize("field_that_needs_units", UNITS_REQUIRED)
def test_chopper_checker_GIVEN_unit_has_wrong_type_WHEN_validating_units_THEN_returns_false(
    field_that_needs_units, units_dict, nexus_defined_chopper_checker
):
    units_dict[field_that_needs_units] = IMPROPER_UNITS[field_that_needs_units]
    assert not nexus_defined_chopper_checker.units_are_valid(units_dict)


@pytest.mark.parametrize("field_that_needs_units", UNITS_REQUIRED)
def test_chopper_checker_GIVEN_units_have_wrong_dimension_WHEN_validating_units_THEN_returns_false(
    field_that_needs_units, units_dict, nexus_defined_chopper_checker
):
    units_dict[field_that_needs_units] = (
        "50 " + EXPECTED_UNIT_TYPE[field_that_needs_units]
    )
    assert not nexus_defined_chopper_checker.units_are_valid(units_dict)


def test_nexus_chopper_checker_GIVEN_units_attribute_has_wrong_type_WHEN_validating_chopper_THEN_returns_false(
    nexus_defined_chopper_checker, nexus_disk_chopper
):
    nexus_disk_chopper[SLIT_HEIGHT_NAME].attrs["units"] = np.array(
        [i for i in range(10)]
    )
    assert not nexus_defined_chopper_checker.validate_chopper()


@pytest.mark.parametrize("units_attribute", ["radians", "rad", "radian"])
def test_chopper_checker_GIVEN_different_ways_of_writing_radians_WHEN_creating_chopper_details_THEN_slit_edges_array_is_converted(
    nexus_defined_chopper_checker, nexus_disk_chopper, units_attribute
):
    del nexus_disk_chopper[SLIT_EDGES_NAME].attrs["units"]
    nexus_disk_chopper[SLIT_EDGES_NAME].attrs["units"] = str.encode(units_attribute)
    nexus_defined_chopper_checker.validate_chopper()
    assert np.allclose(
        nexus_defined_chopper_checker.chopper_details.slit_edges, RADIANS_EDGES_ARR
    )
