"""Tests for custom validators in the nexus_constructor.validators module"""
from typing import List

from mock import Mock

from nexus_constructor.validators import (
    NameValidator,
    UnitValidator,
    FieldValueValidator,
    FieldType,
    GeometryFileValidator,
)
import attr
from PySide2.QtGui import QValidator
from mock import Mock

from nexus_constructor.validators import NameValidator, UnitValidator, OkValidator


@attr.s
class ObjectWithName:
    name = attr.ib(str)


def assess_names(names: List[ObjectWithName], new_name, expected_validity):
    """
    Tests the validity of a given name at a given index in a TransformationModel and InstrumentModel with an existing
    list of named transforms

    :param names: The names to give to items in the model before validating a change
    :param new_name: The name to check the validity of a change/insert into the model
    :param expected_validity: Whether the name change/insert is expected to be valid
    """
    validator = NameValidator(names)
    assert (
        validator.validate(new_name, 0) == QValidator.Acceptable
    ) == expected_validity


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


def test_unit_validator():
    validator = UnitValidator()

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
    dataset_type_combo = DummyCombo("String")

    validator = FieldValueValidator(field_type_combo, dataset_type_combo)
    validator.is_valid = Mock()

    assert validator.validate(strvalue, 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)


def test_GIVEN_invalid_float_value_WHEN_validating_field_value_THEN_returns_intermediate_and_emits_signal_with_false():
    invalid_value = "sdfn"

    field_type_combo = DummyCombo(FieldType.scalar_dataset.value)
    dataset_type_combo = DummyCombo("Float")

    validator = FieldValueValidator(field_type_combo, dataset_type_combo)
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


def test_GIVEN_file_not_ending_with_correct_suffix_WHEN_validating_geometry_file_THEN_returns_invalid_and_emits_signal_with_false():
    file_types = {"OFF files": ["off", ["OFF"]]}
    validator = GeometryFileValidator(file_types)

    validator.is_valid = Mock()
    validator.is_file = lambda x: True
    assert validator.validate("something.json", 0) == QValidator.Invalid
    validator.is_valid.emit.assert_called_once_with(False)


def test_GIVEN_valid_file_WHEN_validating_geometry_file_THEN_returns_acceptable_and_emits_signal_with_true():
    file_types = {"OFF files": ["off", "OFF"]}

    validator = GeometryFileValidator(file_types)

    validator.is_valid = Mock()
    validator.is_file = lambda x: True

    assert validator.validate("test.OFF", 0) == QValidator.Acceptable
    validator.is_valid.emit.assert_called_once_with(True)
def create_content_ok_validator():
    """
    Create an OkValidator and button mocks that mimic the conditions for valid input.
    :return: An OkValidator that emits True when `validate_ok` is called and mocks for the no geometry and mesh buttons.
    """
    mock_no_geometry_button = Mock()
    mock_mesh_button = Mock()

    mock_no_geometry_button.isChecked = Mock(return_value=False)
    mock_mesh_button.isChecked = Mock(return_value=True)

    validator = OkValidator(mock_no_geometry_button, mock_mesh_button)
    validator.set_units_valid(True)
    validator.set_name_valid(True)
    validator.set_file_valid(True)

    return validator, mock_mesh_button, mock_no_geometry_button


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


def test_GIVEN_invalid_units_WHEN_using_ok_validator_WITH_no_geometry_button_checked_THEN_true_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    mock_no_geometry_button.isChecked = Mock(return_value=True)
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=True))
    validator.set_units_valid(False)


def test_GIVEN_invalid_file_WHEN_using_ok_validator_WITH_mesh_button_unchecked_THEN_true_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    mock_mesh_button.isChecked = Mock(return_value=False)
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=True))
    validator.set_file_valid(False)
