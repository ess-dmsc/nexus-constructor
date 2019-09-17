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
)


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
        slits=3,
        slit_edges=np.array(
            [
                0.0,
                0.757472895365539,
                1.4416419621473162,
                2.6197392072434886,
                3.839724354387525,
                4.368559117741807,
            ]
        ),
        radius=200.3,
        slit_height=70.1,
    )


@pytest.fixture(scope="function")
def chopper_checker(mock_fields_list_widget):
    return UserDefinedChopperChecker(mock_fields_list_widget)


def test_GIVEN_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_true():
    assert check_data_type(FLOAT_TYPES[0], FLOAT_TYPES)


def test_GIVEN_non_matching_data_types_WHEN_checking_data_types_THEN_check_data_type_returns_false():
    assert not check_data_type(INT_TYPES[0], FLOAT_TYPES)


def test_GIVEN_valid_values_WHEN_validating_chopper_input_THEN_returns_true(
    chopper_checker
):
    assert chopper_checker.validate_chopper()


def test_GIVEN_column_array_WHEN_validating_chopper_input_THEN_returns_true(
    chopper_checker
):
    chopper_checker.fields_dict[SLIT_EDGES].value = np.array(
        [[i * 1.0] for i in range(6)]
    )
    assert chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_more_than_two_dimensions_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):
    chopper_checker.fields_dict[SLIT_EDGES].value = np.array(
        [[[i * 1.0 for i in range(6)] for _ in range(6)] for _ in range(6)]
    )

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert not edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_array_with_two_dimensions_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):
    chopper_checker.fields_dict[SLIT_EDGES].value = np.array(
        [[i * 1.0 for i in range(6)] for _ in range(6)]
    )

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert not edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):
    chopper_checker.fields_dict[SLITS].value = 5

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_HEIGHT].value = 201

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_HEIGHT].value = chopper_checker.fields_dict[
        RADIUS
    ].value = 20

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_EDGES].value[0], chopper_checker.fields_dict[
        SLIT_EDGES
    ].value[1] = (
        chopper_checker.fields_dict[SLIT_EDGES].value[1],
        chopper_checker.fields_dict[SLIT_EDGES].value[0],
    )

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_EDGES].value[0] = chopper_checker.fields_dict[
        SLIT_EDGES
    ].value[1]

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_EDGES].value[-1] = (
        chopper_checker.fields_dict[SLIT_EDGES].value[0] + 365
    )

    assert chopper_checker.required_fields_present()
    assert fields_have_correct_type(chopper_checker.fields_dict)
    assert edges_array_has_correct_shape(
        chopper_checker.fields_dict[SLIT_EDGES].value.ndim,
        chopper_checker.fields_dict[SLIT_EDGES].value.shape,
    )
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slits_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    del chopper_checker.fields_dict[SLITS]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):
    del chopper_checker.fields_dict[SLIT_EDGES]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_radius_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    del chopper_checker.fields_dict[RADIUS]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_field_is_missing_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    del chopper_checker.fields_dict[SLIT_HEIGHT]

    assert not chopper_checker.required_fields_present()
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slits_field_is_not_int_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLITS].dtype = np.float16

    assert chopper_checker.required_fields_present()
    assert not fields_have_correct_type(chopper_checker.fields_dict)
    assert not chopper_checker.validate_chopper()


def test_GIVEN_radius_field_is_not_float_or_double_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[RADIUS].dtype = np.byte

    assert chopper_checker.required_fields_present()
    assert not fields_have_correct_type(chopper_checker.fields_dict)
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_height_field_is_not_float_or_double_float_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_HEIGHT].dtype = np.byte

    assert chopper_checker.required_fields_present()
    assert not fields_have_correct_type(chopper_checker.fields_dict)
    assert not chopper_checker.validate_chopper()


def test_GIVEN_slit_edges_field_is_not_float_or_double_WHEN_validating_chopper_input_THEN_returns_false(
    chopper_checker
):

    chopper_checker.fields_dict[SLIT_EDGES].dtype = np.byte

    assert chopper_checker.required_fields_present()
    assert not fields_have_correct_type(chopper_checker.fields_dict)
    assert not chopper_checker.validate_chopper()


def test_GIVEN_chopper_details_WHEN_creating_chopper_geometry_THEN_details_matches_fields_widget_input(
    chopper_checker,
    mock_slit_edges_widget,
    mock_slits_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):

    chopper_checker.validate_chopper()
    details = chopper_checker.get_chopper_details()

    def convert_angle(x):
        return np.deg2rad(x) % (np.pi * 2)

    vfunc = np.vectorize(convert_angle)
    radian_slit_edges = vfunc(mock_slit_edges_widget.value)

    assert (details.slit_edges == radian_slit_edges).all()
    assert details.slits == mock_slits_widget.value
    assert details.radius == mock_radius_widget.value
    assert details.slit_height == mock_slit_height_widget.value
