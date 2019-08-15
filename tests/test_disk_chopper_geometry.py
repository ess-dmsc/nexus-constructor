import pytest
from PySide2.QtWidgets import QListWidget
from mock import Mock
import numpy as np
from typing import List

from nexus_constructor.component_fields import FieldWidget
from nexus_constructor.geometry.disk_chopper_geometry import (
    ChopperDetails,
    chopper_input_seems_reasonable,
)


@pytest.fixture(scope="function")
def chopper_details():
    return ChopperDetails(
        slits=3,
        slit_edges=np.array([0.0, 43.4, 82.6, 150.1, 220.0, 250.3]),
        radius=200.3,
        slit_height=70.1,
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
    mock_slit_edges_widget.value = chopper_details.slit_edges

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
def mock_fields_list_widget(
    mock_widget_list,
    mock_slits_widget,
    mock_slit_edges_widget,
    mock_radius_widget,
    mock_slit_height_widget,
):

    list_widget = Mock(spec=QListWidget)
    list_widget.count = Mock(return_value=4)

    list_widget.itemWidget = Mock(side_effect=mock_widget_list)
    list_widget.items = Mock(return_value=mock_widget_list)

    return list_widget


def remove_mock_widget_from_list(
    widget_mock_list: List, widget: Mock, mock_fields_list_widget: Mock
):

    widget_mock_list.remove(widget)

    mock_fields_list_widget.itemWidget = Mock(side_effect=widget_mock_list)
    mock_fields_list_widget.items = Mock(return_value=widget_mock_list)


def test_GIVEN_valid_values_WHEN_validating_chopper_details_THEN_returns_true(
    chopper_details
):

    assert chopper_details.validate()


def test_GIVEN_mismatch_between_slits_and_slit_edges_array_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slits = 5
    assert not chopper_details.validate()


def test_GIVEN_slit_height_is_larger_than_radius_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slit_height = 201
    assert not chopper_details.validate()


def test_GIVEN_slit_height_and_radius_are_equal_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details._slit_height = chopper_details._radius = 20
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_is_not_in_order_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[0], chopper_details.slit_edges[1] = (
        chopper_details.slit_edges[1],
        chopper_details.slit_edges[0],
    )
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_contains_repeated_values_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[0] = chopper_details.slit_edges[1]
    assert not chopper_details.validate()


def test_GIVEN_slit_edges_list_has_overlapping_slits_WHEN_validating_chopper_details_THEN_returns_false(
    chopper_details
):

    chopper_details.slit_edges[-1] = 365
    assert not chopper_details.validate()


def test_GIVEN_slits_field_is_missing_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_fields_list_widget, mock_widget_list, mock_slits_widget
):

    remove_mock_widget_from_list(
        mock_widget_list, mock_slits_widget, mock_fields_list_widget
    )
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_slit_edges_field_is_missing_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_fields_list_widget, mock_widget_list, mock_slit_edges_widget
):

    remove_mock_widget_from_list(
        mock_widget_list, mock_slit_edges_widget, mock_fields_list_widget
    )
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_radius_field_is_missing_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_fields_list_widget, mock_widget_list, mock_radius_widget
):

    remove_mock_widget_from_list(
        mock_widget_list, mock_radius_widget, mock_fields_list_widget
    )
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_slit_height_field_is_missing_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_fields_list_widget, mock_widget_list, mock_slit_height_widget
):

    remove_mock_widget_from_list(
        mock_widget_list, mock_slit_height_widget, mock_fields_list_widget
    )
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_slits_field_is_not_some_type_of_int_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_slits_widget, mock_fields_list_widget
):

    mock_slits_widget.dtype = np.byte
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_radius_field_is_not_some_type_of_float_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_radius_widget, mock_fields_list_widget
):

    mock_radius_widget.dtype = np.byte
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)


def test_GIVEN_slit_height_field_is_not_some_type_of_float_WHEN_checking_if_chopper_input_seems_reasonable_THEN_returns_false(
    mock_slit_height_widget, mock_fields_list_widget
):

    mock_slit_height_widget.dtype = np.byte
    assert not chopper_input_seems_reasonable(mock_fields_list_widget)
