import pytest
from PySide2.QtWidgets import QListWidget
from mock import Mock
import numpy as np

from nexus_constructor.component_fields import FieldWidget
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    SLITS_NAME,
    SLIT_HEIGHT_NAME,
    RADIUS_NAME,
    SLIT_EDGES_NAME,
    UserDefinedChopperChecker,
    INT_TYPES,
    FLOAT_TYPES,
    _incorrect_field_type_message,
    NexusDefinedChopperChecker,
    NAME,
    _check_data_type,
    _fields_have_correct_type,
    _edges_array_has_correct_shape,
)
from tests.chopper_test_helpers import (
    N_SLITS,
    RADIUS_LENGTH,
    SLIT_HEIGHT_LENGTH,
    EDGES_ARR,
    CONVERT_DEGREES_TO_RADIANS,
)
from tests.test_nexus_to_json import create_in_memory_file


@pytest.fixture(scope="function")
def mock_slits_widget():
    mock_slits_widget = Mock(spec=FieldWidget)
    mock_slits_widget.name = SLITS_NAME
    mock_slits_widget.value = N_SLITS
    mock_slits_widget.dtype = np.intc

    return mock_slits_widget


@pytest.fixture(scope="function")
def mock_slit_edges_widget():
    mock_slit_edges_widget = Mock(spec=FieldWidget)
    mock_slit_edges_widget.name = SLIT_EDGES_NAME
    mock_slit_edges_widget.value = np.array([0.0, 43.4, 82.6, 150.1, 220.0, 250.3])
    mock_slit_edges_widget.dtype = np.single

    return mock_slit_edges_widget


@pytest.fixture(scope="function")
def mock_radius_widget():
    mock_radius_widget = Mock(spec=FieldWidget)
    mock_radius_widget.name = RADIUS_NAME
    mock_radius_widget.value = RADIUS_LENGTH
    mock_radius_widget.dtype = np.single

    return mock_radius_widget


@pytest.fixture(scope="function")
def mock_slit_height_widget():
    mock_slit_height_widget = Mock(spec=FieldWidget)
    mock_slit_height_widget.name = SLIT_HEIGHT_NAME
    mock_slit_height_widget.value = SLIT_HEIGHT_LENGTH
    mock_slit_height_widget.dtype = np.single

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
def mock_fields_list_widget(mock_widget_list,):
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
def user_defined_chopper_checker(mock_fields_list_widget):
    return UserDefinedChopperChecker(mock_fields_list_widget)


@pytest.fixture(scope="function")
def nexus_disk_chopper():
    nexus_file = create_in_memory_file("test_disk_chopper")
    disk_chopper_group = nexus_file.create_group("Disk Chopper")
    disk_chopper_group[NAME] = "abc"
    disk_chopper_group[SLITS_NAME] = N_SLITS
    disk_chopper_group[SLIT_EDGES_NAME] = EDGES_ARR
    disk_chopper_group[RADIUS_NAME] = RADIUS_LENGTH
    disk_chopper_group[SLIT_HEIGHT_NAME] = SLIT_HEIGHT_LENGTH
    disk_chopper_group[SLIT_EDGES_NAME].attrs["units"] = str.encode("rad")
    disk_chopper_group[RADIUS_NAME].attrs["units"] = str.encode("m")
    disk_chopper_group[SLIT_HEIGHT_NAME].attrs["units"] = str.encode("m")
    yield disk_chopper_group
    nexus_file.close()


@pytest.fixture(scope="function")
def nexus_defined_chopper_checker(nexus_disk_chopper):
    return NexusDefinedChopperChecker(nexus_disk_chopper)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true(
    mock_radius_widget
):
    assert _check_data_type(mock_radius_widget, FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false(
    mock_slits_widget
):
    assert not _check_data_type(mock_slits_widget, FLOAT_TYPES)


def test_GIVEN_fields_information_and_field_name_WHEN_calling_incorrect_field_type_message_THEN_expected_string_is_returned():
    field_dict = {RADIUS_NAME: "string"}
    error_message = _incorrect_field_type_message(field_dict, RADIUS_NAME)

    assert (
        error_message
        == "Wrong radius type. Expected float but found "
        + str(type(field_dict[RADIUS_NAME]))
        + "."
    )


def test_GIVEN_valid_fields_information_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_true(
    fields_dict_mocks
):
    assert _fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slits_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):
    fields_dict_mocks[SLITS_NAME].dtype = FLOAT_TYPES[0]
    assert not _fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_radius_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):
    fields_dict_mocks[RADIUS_NAME].dtype = INT_TYPES[0]
    assert not _fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slit_height_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):
    fields_dict_mocks[SLIT_HEIGHT_NAME].dtype = INT_TYPES[0]
    assert not _fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slit_edges_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):
    fields_dict_mocks[SLIT_EDGES_NAME].dtype = INT_TYPES[0]
    assert not _fields_have_correct_type(fields_dict_mocks)


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
    user_defined_chopper_checker
):
    assert user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_invalid_shape_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value = np.array(
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)]
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLITS_NAME].value = 5

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_HEIGHT_NAME].value = 201

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[
        SLIT_HEIGHT_NAME
    ].value = user_defined_chopper_checker.fields_dict[RADIUS_NAME].value = 20

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[
        0
    ], user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[1] = (
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[1],
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[0],
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[
        0
    ] = user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[1]

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[-1] = (
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value[0] + 365
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert _fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert _edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slits_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    del user_defined_chopper_checker.fields_dict[SLITS_NAME]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    del user_defined_chopper_checker.fields_dict[SLIT_EDGES_NAME]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_radius_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    del user_defined_chopper_checker.fields_dict[RADIUS_NAME]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    del user_defined_chopper_checker.fields_dict[SLIT_HEIGHT_NAME]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_field_has_wrong_type_WHEN_validating_chopper_input_THEN_valid_chopper_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[RADIUS_NAME].dtype = np.byte

    assert user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_chopper_details_WHEN_creating_chopper_geometry_THEN_details_matches_fields_widget_input(
    user_defined_chopper_checker,
    mock_slit_edges_widget,
    mock_slits_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):
    user_defined_chopper_checker.validate_chopper()
    details = user_defined_chopper_checker.chopper_details

    radian_slit_edges = CONVERT_DEGREES_TO_RADIANS(mock_slit_edges_widget.value)

    assert np.array_equal(details.slit_edges, radian_slit_edges)
    assert details.slits == mock_slits_widget.value
    assert details.radius == pytest.approx(mock_radius_widget.value)
    assert details.slit_height == pytest.approx(mock_slit_height_widget.value)


def test_GIVEN_nothing_WHEN_calling_get_chopper_details_THEN_expected_chopper_details_are_returned(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.validate_chopper()
    chopper_details = user_defined_chopper_checker.chopper_details

    assert chopper_details.slits == N_SLITS
    assert chopper_details.radius == pytest.approx(RADIUS_LENGTH)
    assert chopper_details.slit_height == pytest.approx(SLIT_HEIGHT_LENGTH)
    assert np.array_equal(chopper_details.slit_edges, EDGES_ARR)


def test_GIVEN_valid_nexus_disk_chopper_WHEN_validating_disk_chopper_THEN_validate_chopper_returns_true(
    nexus_defined_chopper_checker
):
    assert nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_complete_nexus_disk_chopper_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_true(
    nexus_defined_chopper_checker
):
    assert nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slits_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLITS_NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_edges_array_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLIT_EDGES_NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_radius_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[RADIUS_NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_height_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLIT_HEIGHT_NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_edge_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLITS_NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_height_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLIT_HEIGHT_NAME].attrs["units"]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_radius_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[RADIUS_NAME].attrs["units"]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_wrong_field_type_WHEN_validating_disk_chopper_THEN_validate_chopper_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLITS_NAME]
    nexus_defined_chopper_checker._disk_chopper[SLITS_NAME] = "string"
    assert nexus_defined_chopper_checker.required_fields_present()
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_nexus_disk_chopper_with_wrong_edges_array_shape_WHEN_validating_disk_chopper_THEN_validate_chopper_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLIT_EDGES_NAME]
    nexus_defined_chopper_checker._disk_chopper[SLIT_EDGES_NAME] = np.ones(shape=(5, 5))
    nexus_defined_chopper_checker._disk_chopper[SLIT_EDGES_NAME].attrs[
        "units"
    ] = str.encode("rad")
    assert nexus_defined_chopper_checker.required_fields_present()
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_invalid_nexus_disk_chopper_WHEN_validating_disk_chopper_THEN_validate_chopper_returns_true(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLITS_NAME]
    nexus_defined_chopper_checker._disk_chopper[SLITS_NAME] = 200
    assert nexus_defined_chopper_checker.required_fields_present()
    assert not nexus_defined_chopper_checker.validate_chopper()


def test_GIVEN_validation_passes_WHEN_validating_nexus_disk_chopper_THEN_chopper_details_has_expected_values(
    nexus_defined_chopper_checker
):
    nexus_defined_chopper_checker.validate_chopper()
    chopper_details = nexus_defined_chopper_checker.chopper_details

    assert chopper_details.slits == N_SLITS
    assert np.array_equal(chopper_details.slit_edges, EDGES_ARR)
    assert chopper_details.radius == pytest.approx(RADIUS_LENGTH)
    assert chopper_details.slit_height == pytest.approx(SLIT_HEIGHT_LENGTH)
