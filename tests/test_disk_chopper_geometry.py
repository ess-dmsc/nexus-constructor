import pytest
from PySide2.QtWidgets import QListWidget
from mock import Mock
import numpy as np

from nexus_constructor.component_fields import FieldWidget
from nexus_constructor.geometry.disk_chopper_geometry import (
    ChopperDetails,
    SLITS,
    SLIT_HEIGHT,
    RADIUS,
    SLIT_EDGES,
    UserDefinedChopperChecker,
    fields_have_correct_type,
    edges_array_has_correct_shape,
    check_data_type,
    INT_TYPES,
    FLOAT_TYPES,
    incorrect_field_type_message,
    NexusDefinedChopperChecker,
    NAME,
)
from tests.test_nexus_to_json import create_in_memory_file

N_SLITS = 3
EDGES_ARR = np.array(
    [
        0.0,
        0.757472895365539,
        1.4416419621473162,
        2.6197392072434886,
        3.839724354387525,
        4.368559117741807,
    ]
)
RADIUS_LENGTH = 200.3
SLIT_HEIGHT_LENGTH = 70.1


def degree_to_radian(x):
    return np.deg2rad(x) % (np.pi * 2)


CONVERT_DEGREES_TO_RADIANS = np.vectorize(degree_to_radian)


@pytest.fixture(scope="function")
def mock_slits_widget(chopper_details):

    mock_slits_widget = Mock(spec=FieldWidget)
    mock_slits_widget.name = "slits"
    mock_slits_widget.value = chopper_details.slits
    mock_slits_widget.dtype = np.intc

    return mock_slits_widget


@pytest.fixture(scope="function")
def mock_slit_edges_widget(chopper_details):

    mock_slit_edges_widget = Mock(spec=FieldWidget)
    mock_slit_edges_widget.name = "slit_edges"
    mock_slit_edges_widget.value = np.array([0.0, 43.4, 82.6, 150.1, 220.0, 250.3])
    mock_slit_edges_widget.dtype = np.single

    return mock_slit_edges_widget


@pytest.fixture(scope="function")
def mock_radius_widget(chopper_details):

    mock_radius_widget = Mock(spec=FieldWidget)
    mock_radius_widget.name = "radius"
    mock_radius_widget.value = chopper_details.radius
    mock_radius_widget.dtype = np.single

    return mock_radius_widget


@pytest.fixture(scope="function")
def mock_slit_height_widget(chopper_details):

    mock_slit_height_widget = Mock(spec=FieldWidget)
    mock_slit_height_widget.name = "slit_height"
    mock_slit_height_widget.value = chopper_details.slit_height
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
def chopper_details():
    return ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="rad",
    )


@pytest.fixture(scope="function")
def fields_dict_mocks(
    mock_slits_widget,
    mock_slit_edges_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):

    return {
        SLITS: mock_slits_widget,
        SLIT_EDGES: mock_slit_edges_widget,
        RADIUS: mock_radius_widget,
        SLIT_HEIGHT: mock_slit_height_widget,
    }


@pytest.fixture(scope="function")
def user_defined_chopper_checker(mock_fields_list_widget):
    return UserDefinedChopperChecker(mock_fields_list_widget)


@pytest.fixture(scope="function")
def nexus_disk_chopper():

    nexus_file = create_in_memory_file("test_disk_chopper")
    disk_chopper_group = nexus_file.create_group("Disk Chopper")
    disk_chopper_group[NAME] = "abc"
    disk_chopper_group[SLITS] = N_SLITS
    disk_chopper_group[SLIT_EDGES] = EDGES_ARR
    disk_chopper_group[RADIUS] = RADIUS_LENGTH
    disk_chopper_group[SLIT_HEIGHT] = SLIT_HEIGHT_LENGTH
    disk_chopper_group[SLIT_EDGES].attrs["units"] = str.encode("m")
    disk_chopper_group[RADIUS].attrs["units"] = str.encode("m")
    disk_chopper_group[SLIT_HEIGHT].attrs["units"] = str.encode("rad")
    yield disk_chopper_group
    nexus_file.close()


@pytest.fixture(scope="function")
def nexus_defined_chopper_checker(nexus_disk_chopper):
    return NexusDefinedChopperChecker(nexus_disk_chopper)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true():
    assert check_data_type(FLOAT_TYPES[0], FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false():
    assert not check_data_type(INT_TYPES[0], FLOAT_TYPES)


def test_GIVEN_fields_information_and_field_name_WHEN_calling_incorrect_field_type_message_THEN_expected_string_is_returned(
    fields_dict_mocks
):

    wrong_data_type_for_radius_field = np.int8

    fields_dict_mocks[RADIUS].dtype = wrong_data_type_for_radius_field
    error_message = incorrect_field_type_message(fields_dict_mocks, RADIUS)

    assert (
        error_message
        == "Wrong radius type. Expected float but found "
        + str(wrong_data_type_for_radius_field)
        + "."
    )


def test_GIVEN_valid_fields_information_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_true(
    fields_dict_mocks
):
    assert fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slits_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):

    fields_dict_mocks[SLITS].dtype = FLOAT_TYPES[0]
    assert not fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_radius_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):

    fields_dict_mocks[RADIUS].dtype = INT_TYPES[0]
    assert not fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slit_height_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):

    fields_dict_mocks[SLIT_HEIGHT].dtype = INT_TYPES[0]
    assert not fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_invalid_slit_edges_type_WHEN_validating_disk_chopper_THEN_fields_have_correct_type_returns_false(
    fields_dict_mocks
):

    fields_dict_mocks[SLIT_EDGES].dtype = INT_TYPES[0]
    assert not fields_have_correct_type(fields_dict_mocks)


def test_GIVEN_edges_array_with_valid_shape_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():

    valid_array = np.array([i for i in range(6)])
    assert edges_array_has_correct_shape(valid_array.ndim, valid_array.shape)


def test_GIVEN_edges_array_with_more_than_two_dimensions_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_false():

    three_dim_array = np.ones(shape=(5, 5, 5))
    assert not edges_array_has_correct_shape(
        three_dim_array.ndim, three_dim_array.shape
    )


def test_GIVEN_edges_array_with_two_dimensions_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_false():

    two_dim_array = np.ones(shape=(5, 5))
    assert not edges_array_has_correct_shape(two_dim_array.ndim, two_dim_array.shape)


def test_GIVEN_column_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():

    column_array = np.ones(shape=(5, 1))
    assert edges_array_has_correct_shape(column_array.ndim, column_array.shape)


def test_GIVEN_row_shaped_edges_array_WHEN_validating_disk_chopper_THEN_edges_array_has_correct_shape_returns_true():

    row_array = np.ones(shape=(1, 5))
    assert edges_array_has_correct_shape(row_array.ndim, row_array.shape)


def test_GIVEN_valid_values_WHEN_validating_chopper_input_THEN_returns_true(
    user_defined_chopper_checker
):
    assert user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_invalid_shape_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLIT_EDGES].value = np.array(
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)]
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    user_defined_chopper_checker.fields_dict[SLITS].value = 5

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[SLIT_HEIGHT].value = 201

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[
        SLIT_HEIGHT
    ].value = user_defined_chopper_checker.fields_dict[RADIUS].value = 20

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[
        0
    ], user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[1] = (
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[1],
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[0],
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[
        0
    ] = user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[1]

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[-1] = (
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value[0] + 365
    )

    assert user_defined_chopper_checker.required_fields_present()
    assert fields_have_correct_type(user_defined_chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        user_defined_chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slits_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    del user_defined_chopper_checker.fields_dict[SLITS]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):
    del user_defined_chopper_checker.fields_dict[SLIT_EDGES]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_radius_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    del user_defined_chopper_checker.fields_dict[RADIUS]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_slit_height_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    user_defined_chopper_checker
):

    del user_defined_chopper_checker.fields_dict[SLIT_HEIGHT]

    assert not user_defined_chopper_checker.required_fields_present()
    assert not user_defined_chopper_checker.validate_chopper()


def test_GIVEN_field_has_wrong_type_WHEN_validating_chopper_input_THEN_valid_chopper_returns_false(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.fields_dict[RADIUS].dtype = np.byte

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
    details = user_defined_chopper_checker.get_chopper_details()

    radian_slit_edges = CONVERT_DEGREES_TO_RADIANS(mock_slit_edges_widget.value)

    assert (details.slit_edges == radian_slit_edges).all()
    assert details.slits == mock_slits_widget.value
    assert details.radius == mock_radius_widget.value
    assert details.slit_height == mock_slit_height_widget.value


def test_GIVEN_nothing_WHEN_calling_get_chopper_details_THEN_expected_chopper_details_are_returned(
    user_defined_chopper_checker
):

    user_defined_chopper_checker.validate_chopper()
    chopper_details = user_defined_chopper_checker.get_chopper_details()

    assert chopper_details.slits == N_SLITS
    assert chopper_details.radius == RADIUS_LENGTH
    assert chopper_details.slit_height == SLIT_HEIGHT_LENGTH
    assert np.array_equal(chopper_details.slit_edges, EDGES_ARR)


def test_GIVEN_chopper_information_WHEN_initialising_chopper_details_THEN_chopper_details_object_contains_original_disk_chopper_info(
    chopper_details
):

    assert chopper_details.slits == N_SLITS
    assert np.array_equal(chopper_details.slit_edges, EDGES_ARR)
    assert chopper_details.radius == RADIUS_LENGTH
    assert chopper_details.slit_height == SLIT_HEIGHT_LENGTH


def test_GIVEN_angles_in_degrees_WHEN_initialising_chopper_details_object_THEN_angles_are_converted_to_radians():

    edges_array = np.array([i * 30 for i in range(4)])

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=np.array([i * 30 for i in range(4)]),
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        angle_units="deg",
    )

    assert np.array_equal(
        chopper_details.slit_edges, CONVERT_DEGREES_TO_RADIANS(edges_array)
    )


def test_GIVEN_slit_height_length_in_cm_WHEN_initialising_chopper_details_THEN_slit_height_is_converted_to_cm():

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        slit_height_units="cm",
    )

    assert chopper_details.slit_height * 100 == SLIT_HEIGHT_LENGTH


def test_GIVEN_radius_length_in_cm_WHEN_initialising_chopper_details_THEN_radius_is_converted_to_cm():

    chopper_details = ChopperDetails(
        slits=N_SLITS,
        slit_edges=EDGES_ARR,
        radius=RADIUS_LENGTH,
        slit_height=SLIT_HEIGHT_LENGTH,
        radius_units="cm",
    )

    assert chopper_details.radius * 100 == RADIUS_LENGTH


def test_GIVEN_complete_nexus_disk_chopper_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_true(
    nexus_defined_chopper_checker
):

    assert nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_name_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[NAME]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slits_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[SLITS]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_edges_array_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[SLIT_EDGES]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_radius_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[RADIUS]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_height_value_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[SLIT_HEIGHT]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_edge_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):

    del nexus_defined_chopper_checker._disk_chopper[SLITS]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_slit_height_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[SLIT_HEIGHT].attrs["units"]
    assert not nexus_defined_chopper_checker.required_fields_present()


def test_GIVEN_nexus_disk_chopper_with_no_radius_units_WHEN_validating_disk_chopper_THEN_required_fields_present_returns_false(
    nexus_defined_chopper_checker
):
    del nexus_defined_chopper_checker._disk_chopper[RADIUS].attrs["units"]
    assert not nexus_defined_chopper_checker.required_fields_present()
