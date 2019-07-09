"""Tests for custom validators in the nexus_constructor.validators module"""
from typing import List

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


def create_content_ok_validator():
    """
    :return:
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
    assert result == expected


def test_GIVEN_invalid_name_WHEN_using_ok_validator_THEN_false_signal_is_emitted():

    validator, mock_mesh_button, mock_no_geometry_button = create_content_ok_validator()
    validator.is_valid.connect(lambda x: inspect_signal(x, expected=False))
    validator.set_name_valid(False)
