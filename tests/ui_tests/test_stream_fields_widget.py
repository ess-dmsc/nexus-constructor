from PySide2.QtWidgets import QSpinBox

from nexus_constructor.stream_fields_widget import (
    fill_in_advanced_options,
    check_if_advanced_options_should_be_enabled,
)
from tests.helpers import InMemoryFile


def test_GIVEN_advanced_option_in_field_WHEN_filling_in_advanced_options_THEN_spinbox_is_created(
    qtbot
):
    with InMemoryFile("advanced_options_streams") as file:
        group = file.create_group("group")
        field_name = "test"

        advanced_options = [field_name]
        spinner = QSpinBox()

        items = {advanced_options[0]: spinner}.items()
        value = 4

        group.create_dataset(name=field_name, data=value)

        fill_in_advanced_options(items, group)

        assert spinner.value() == value


def test_GIVEN_field_with_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_true():
    with InMemoryFile("advanced_check") as file:
        group = file.create_group("group")

        field_name = "test"
        advanced_options = [field_name]
        group.create_dataset(name=field_name, data=1)
        assert check_if_advanced_options_should_be_enabled(advanced_options, group)


def test_GIVEN_field_without_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_false():
    with InMemoryFile("advanced_check") as file:
        group = file.create_group("group")

        field_name = "test"
        advanced_options = ["not_test"]
        group.create_dataset(name=field_name, data=1)
        assert not check_if_advanced_options_should_be_enabled(advanced_options, group)
