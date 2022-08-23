"""Tests for custom validators in the nexus_constructor.validators module"""
from io import StringIO
from typing import List

import attr
import numpy as np
import pytest
from mock import Mock
from PySide2.QtGui import QValidator

from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.unit_utils import METRES
from nexus_constructor.validators import (
    GEOMETRY_FILE_TYPES,
    BrokerAndTopicValidator,
    CommandDialogFileNameValidator,
    CommandDialogOKValidator,
    FieldType,
    FieldValueValidator,
    GeometryFileValidator,
    NameValidator,
    NullableIntValidator,
    NumpyDTypeValidator,
    OkValidator,
    UnitValidator,
)


@attr.s
class ObjectWithName:
    name = attr.ib(str)


def assess_names(
    names: List[ObjectWithName], new_name, expected_validity, invalid_names=None
):
    """
    Tests the validity of a given name at a given index in a TransformationModel and InstrumentModel with an existing
    list of named transforms

    :param names: The names to give to items in the model before validating a change
    :param new_name: The name to check the validity of a change/insert into the model
    :param expected_validity: Whether the name change/insert is expected to be valid
    """
    validator = NameValidator(names, invalid_names)
    assert (
        validator.validate(new_name, 0) == QValidator.Acceptable
    ) == expected_validity


def test_name_validator_name_in_invalid_names():
    invalid_names = ["test"]
    assess_names(
        [], invalid_names[0], expected_validity=False, invalid_names=invalid_names
    )


def test_name_validator_new_unique_name():
    """A name that's not already in the model, being added at a new index should be valid"""
    assess_names(
        [ObjectWithName("foo"), ObjectWithName("bar"), ObjectWithName("baz")],
        "asdf",
        True,
    )


def test_an_empty_name_is_not_valid():
    empty_name = ""
    assess_names(
        [ObjectWithName("foo"), ObjectWithName("bar"), ObjectWithName("baz")],
        empty_name,
        False,
    )


def test_name_validator_new_existing_name():
    """A name that is already in the model is not valid at a new index"""
    assess_names(
        [ObjectWithName("foo"), ObjectWithName("bar"), ObjectWithName("baz")],
        "foo",
        False,
    )


def test_name_validator_set_to_new_name():
    """A name that's not in the model should be valid at an existing index"""
    assess_names(
        [ObjectWithName("foo"), ObjectWithName("bar"), ObjectWithName("baz")],
        "asdf",
        True,
    )


def test_name_validator_set_to_duplicate_name():
    """A name that's already at an index should not be valid at another index"""
    assess_names(
        [ObjectWithName("foo"), ObjectWithName("bar"), ObjectWithName("baz")],
        "foo",
        False,
    )


def test_unit_validator_with_metres_set_as_expected_dimensionality():
    validator = UnitValidator(expected_dimensionality=METRES)

    lengths = ["mile", "cm", "centimetre", "yard", "km"]
    not_lengths = [
        "minute",
        "hour",
        "ounce",
        "stone",
        "pound",
        "amp",
        "abc",
        "c",
        "3.0",
        "123",
        "",
        "`?@#",
        "}",
        "2 metres",
    ]

    for unit in lengths:
        assert validator.validate(unit, 0) == QValidator.Acceptable

    for unit in not_lengths:
        assert validator.validate(unit, 0) == QValidator.Intermediate


def test_unit_validator_with_no_expected_dimensionality():
    validator = UnitValidator()

    valid_units = ["deg", "m", "cm", "dm", "rad"]

    invalid_units = ["asdfghj", "degre", "2 degrees"]

    for unit in valid_units:
        assert validator.validate(unit, 0) == QValidator.Acceptable

    for unit in invalid_units:
        assert validator.validate(unit, 0) == QValidator.Intermediate


def test_GIVEN_empty_string_WHEN_validating_field_value_THEN_returns_intermediate_and_emits_signal_with_false():
    validator = FieldValueValidator(object, object)
    validator.is_valid = Mock()

    assert validator.validate("", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


class DummyCombo:
    def __init__(self, current_item):
        self.current_text = current_item

    def currentText(self):
        return self.current_text


def test_GIVEN_valid_string_value_WHEN_validating_field_value_THEN_returns_acceptable_and_emits_signal_with_true():
    strvalue = "123a"

    field_type_combo = DummyCombo(FieldType.scalar_dataset.value)
    dataset_type_combo = DummyCombo(ValueTypes.STRING)

    validator = FieldValueValidator(
        field_type_combo, dataset_type_combo, FieldType.scalar_dataset.value
    )
    validator.is_valid = Mock()

    assert validator.validate(strvalue, 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)


def test_GIVEN_invalid_float_value_WHEN_validating_field_value_THEN_returns_intermediate_and_emits_signal_with_false():
    invalid_value = "sdfn"

    field_type_combo = DummyCombo(FieldType.scalar_dataset.value)
    dataset_type_combo = DummyCombo(ValueTypes.FLOAT)

    validator = FieldValueValidator(
        field_type_combo, dataset_type_combo, FieldType.scalar_dataset.value
    )
    validator.is_valid = Mock()

    assert validator.validate(invalid_value, 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_no_input_WHEN_validating_geometry_file_THEN_returns_intermediate_and_emits_signal_with_false():
    validator = GeometryFileValidator([])

    validator.is_valid = Mock()

    assert validator.validate("", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_invalid_file_WHEN_validating_geometry_file_THEN_returns_intermediate_and_emits_signal_with_false():
    validator = GeometryFileValidator([])

    validator.is_valid = Mock()
    validator.is_file = lambda x: False

    assert validator.validate("", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_file_not_ending_with_correct_suffix_WHEN_validating_geometry_file_THEN_emits_signal_with_false():
    file_types = {"OFF files": ["off", ["OFF"]]}
    validator = GeometryFileValidator(file_types)

    validator.is_valid = Mock()
    validator.is_file = lambda x: True
    assert validator.validate("something.json", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def create_content_ok_validator():
    """
    Create an OkValidator and button mocks that mimic the conditions for valid input.
    :return: An OkValidator that emits True when `validate_ok` is called and mocks for the no geometry and mesh buttons.
    """
    mock_no_geometry_button = Mock()
    mock_mesh_button = Mock()

    pixel_validator = Mock()
    pixel_validator.unacceptable_pixel_states = Mock(return_value=[])

    mock_no_geometry_button.isChecked = Mock(return_value=False)
    mock_mesh_button.isChecked = Mock(return_value=True)
    field_widget_list = None

    validator = OkValidator(
        mock_no_geometry_button, mock_mesh_button, pixel_validator, field_widget_list
    )
    validator.set_units_valid(True)
    validator.set_name_valid(True)
    validator.set_file_valid(True)

    return (validator, mock_mesh_button, mock_no_geometry_button)


def inspect_signal(result, expected):
    """
    Function for checking that the signal emitted matches an expected value. Used for the OkValidator tests.
    :param result: The value emitted by the signal.
    :param expected: The expected value required for the test to pass.
    """
    assert result == expected


def test_GIVEN_valid_name_units_and_file_WHEN_using_ok_validator_THEN_true_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=True))
    validator.validate_ok()


def test_GIVEN_invalid_name_WHEN_using_ok_validator_THEN_false_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=False))
    validator.set_name_valid(False)


def test_GIVEN_invalid_units_WHEN_using_ok_validator_with_no_geometry_button_unchecked_THEN_false_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=False))
    validator.set_units_valid(False)


def test_GIVEN_invalid_file_WHEN_using_ok_validator_with_mesh_button_checked_THEN_false_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=False))
    validator.set_file_valid(False)


def test_GIVEN_invalid_units_WHEN_using_ok_validator_with_no_geometry_button_checked_THEN_true_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    mock_no_geometry_button.isChecked = Mock(return_value=True)
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=True))
    validator.set_units_valid(False)


def test_GIVEN_invalid_file_WHEN_using_ok_validator_with_mesh_button_unchecked_THEN_true_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    mock_mesh_button.isChecked = Mock(return_value=False)
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=True))
    validator.set_file_valid(False)


def test_GIVEN_empty_string_WHEN_using_nullable_int_validator_THEN_returns_acceptable():

    validator = NullableIntValidator()
    assert validator.validate("", 0) == QValidator.Acceptable


@pytest.mark.parametrize("invalid_input", ["fff", "!", "       "])
def test_GIVEN_nonemptry_string_WHEN_using_nullable_int_validator_THEN_returns_invalid(
    invalid_input,
):

    validator = NullableIntValidator()
    assert validator.validate(invalid_input, 0)[0] == QValidator.State.Invalid


def test_GIVEN_integer_WHEN_using_nullable_int_validator_THEN_returns_acceptable():

    validator = NullableIntValidator()
    assert validator.validate("5", 0)[0] == QValidator.State.Acceptable


def test_GIVEN_no_input_WHEN_using_numpy_validator_with_byte_as_dtype_THEN_false_signal_is_emitted():
    validator = NumpyDTypeValidator(np.byte)
    validator.is_valid = Mock()

    assert validator.validate("", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_valid_input_WHEN_using_numpy_validator_with_integer_as_dtype_THEN_true_signal_is_emitted():
    validator = NumpyDTypeValidator(np.intc)
    validator.is_valid = Mock()

    assert validator.validate("1", 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)


def test_GIVEN_floating_point_value_WHEN_using_numpy_validator_with_integer_as_dtype_THEN_false_signal_is_emitted():
    validator = NumpyDTypeValidator(np.intc)
    validator.is_valid = Mock()

    assert validator.validate("1.2", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_alphabetical_chars_WHEN_using_numpy_validator_with_float_as_dtype_THEN_false_signal_is_emitted():
    validator = NumpyDTypeValidator(np.float64)
    validator.is_valid = Mock()

    assert validator.validate("test", 0) == QValidator.Intermediate


def test_GIVEN_string_when_using_numpy_validator_with_string_as_dtype_THEN_true_signal_is_emitted():
    validator = NumpyDTypeValidator(str)
    validator.is_valid = Mock()

    assert validator.validate("test", 0) == QValidator.Acceptable


def test_GIVEN_valid_off_WHEN_validating_geometry_THEN_validity_signal_is_emitted_with_true():
    validator = GeometryFileValidator(GEOMETRY_FILE_TYPES)
    validator.is_valid = Mock()

    valid_off_file = (
        "OFF\n"
        "#  cube.off\n"
        "#  A cube\n"
        "8 6 0\n"
        "-0.500000 -0.500000 0.500000\n"
        "0.500000 -0.500000 0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "0.500000 0.500000 0.500000\n"
        "-0.500000 0.500000 -0.500000\n"
        "0.500000 0.500000 -0.500000\n"
        "-0.500000 -0.500000 -0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "4 0 1 3 2\n"
        "4 2 3 5 4\n"
        "4 4 5 7 6\n"
        "4 6 7 1 0\n"
        "4 1 7 5 3\n"
        "4 6 0 2 4\n"
    )

    validator.open_file = Mock(return_value=StringIO("".join(valid_off_file)))
    validator.is_file = Mock(return_value=True)

    assert validator.validate("test.off", 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)


@pytest.mark.skip(
    reason="Due to performance improvement, this is not a valid test currently"
)
def test_GIVEN_invalid_off_WHEN_validating_geometry_THEN_validity_signal_is_emitted_with_false():
    validator = GeometryFileValidator(GEOMETRY_FILE_TYPES)
    validator.is_valid = Mock()

    # File missing a point
    invalid_off_file = (
        "OFF\n"
        "#  cube.off\n"
        "#  A cube\n"
        "8 6 0\n"
        "-0.500000 -0.500000 0.500000\n"
        "0.500000 -0.500000 0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "0.500000 0.500000 0.500000\n"
        "-0.500000 0.500000 -0.500000\n"
        "0.500000 0.500000 -0.500000\n"
        "-0.500000 -0.500000 -0.500000\n"
        "4 0 1 3 2\n"
        "4 2 3 5 4\n"
        "4 4 5 7 6\n"
        "4 6 7 1 0\n"
        "4 1 7 5 3\n"
        "4 6 0 2 4\n"
    )

    validator.open_file = Mock(return_value=StringIO("".join(invalid_off_file)))
    validator.is_file = Mock(return_value=True)

    assert validator.validate("test.off", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_valid_stl_file_WHEN_validating_geometry_THEN_validity_signal_is_emitted_with_true():
    validator = GeometryFileValidator(GEOMETRY_FILE_TYPES)
    validator.is_valid = Mock()

    valid_stl_file = (
        "solid dart\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "endsolid dart\n"
    )

    validator.open_file = Mock(return_value=StringIO("".join(valid_stl_file)))
    validator.is_file = Mock(return_value=True)

    assert validator.validate("test.stl", 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)


def test_GIVEN_invalid_stl_file_WHEN_validating_geometry_THEN_validity_signal_is_emitted_with_false():
    validator = GeometryFileValidator(GEOMETRY_FILE_TYPES)
    validator.is_valid = Mock()

    # File with missing endloop statement
    invalid_stl_file = (
        "solid dart\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "vertex 1.00000E+000 2.50000E-001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 0.00000E+000 0.00000E+000 -1.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "vertex 3.10000E+001 1.00000E+001 1.00000E+000\n"
        "endloop\n"
        "endfacet\n"
        "facet normal 8.09000E-001 5.87800E-001 0.00000E+000\n"
        "outer loop\n"
        "vertex 3.10000E+001 4.15500E+001 1.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 6.00000E+000\n"
        "vertex 6.10000E+001 2.50000E-001 1.00000E+000\n"
        "endfacet\n"
        "endsolid dart\n"
    )

    validator.open_file = Mock(return_value=StringIO("".join(invalid_stl_file)))
    validator.is_file = Mock(return_value=True)

    assert validator.validate("test.stl", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_blank_OFF_file_WHEN_validating_geometry_THEN_validity_signal_is_emitted_with_false():
    validator = GeometryFileValidator(GEOMETRY_FILE_TYPES)
    validator.is_valid = Mock()

    blank_off_file = ""

    validator.open_file = Mock(return_value=StringIO("".join(blank_off_file)))
    validator.is_file = Mock(return_value=True)

    assert validator.validate("test.off", 0) == QValidator.Intermediate
    validator.is_valid.emit.assert_called_once_with(False)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("file.nxs", QValidator.Acceptable),
        ("file.hdf5", QValidator.Acceptable),
        ("file.hdf", QValidator.Acceptable),
        ("file.json", QValidator.Intermediate),
        ("", QValidator.Intermediate),
        ("file", QValidator.Intermediate),
    ],
)
def test_GIVEN_valid_file_extensions_WHEN_validating_nexus_filename_for_filewriter_options_THEN_validator_emits_true(
    test_input, expected
):
    validator = CommandDialogFileNameValidator()
    validator.is_valid = Mock()
    assert validator.validate(test_input, 0) == expected


@pytest.mark.parametrize(
    "broker_valid,file_valid,expected",
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_GIVEN_valid_broker_and_filename_WHEN_validating_ok_button_for_command_dialog_THEN_validator_emits_true(
    broker_valid, file_valid, expected
):

    validator = CommandDialogOKValidator()
    validator.is_valid = Mock()

    validator.set_broker_valid(broker_valid)
    validator.set_filename_valid(file_valid)

    validator.is_valid.emit.assert_called_with(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("broker:9092/topic1", QValidator.Acceptable),
        ("broker/topic", QValidator.Acceptable),
        ("broker.io:9092/topic_1", QValidator.Acceptable),
        ("broker:9092", QValidator.Intermediate),
        ("b/t", QValidator.Acceptable),
        ("broker", QValidator.Intermediate),
        ("/topic", QValidator.Intermediate),
    ],
)
def test_GIVEN_valid_broker_and_topic_WHEN_validating_broker_topic_edit_THEN_validator_emits_correctly(
    test_input, expected
):
    validator = BrokerAndTopicValidator()
    validator.is_valid = Mock()
    assert validator.validate(test_input, 0) == expected
