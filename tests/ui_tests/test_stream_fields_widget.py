from PySide2.QtWidgets import QSpinBox

from nexus_constructor.stream_fields_widget import (
    fill_in_advanced_options,
    check_if_advanced_options_should_be_enabled,
    StreamFieldsWidget,
)
from tests.helpers import file  # noqa: F401


def test_GIVEN_advanced_option_in_field_WHEN_filling_in_advanced_options_THEN_spinbox_is_created(
    qtbot, file
):
    group = file.create_group("group")
    field_name = "test"

    advanced_options = [field_name]
    spinner = QSpinBox()

    items = {advanced_options[0]: spinner}.items()
    value = 4

    group.create_dataset(name=field_name, data=value)

    fill_in_advanced_options(items, group)

    assert spinner.value() == value


def test_GIVEN_field_with_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_true(
    file
):

    group = file.create_group("group")

    field_name = "test"
    advanced_options = [field_name]
    group.create_dataset(name=field_name, data=1)
    assert check_if_advanced_options_should_be_enabled(advanced_options, group)


def test_GIVEN_field_without_advanced_option_WHEN_checking_if_advanced_options_should_be_enabled_THEN_returns_false(
    file
):
    group = file.create_group("group")

    field_name = "test"
    advanced_options = ["not_test"]
    group.create_dataset(name=field_name, data=1)
    assert not check_if_advanced_options_should_be_enabled(advanced_options, group)


def test_GIVEN_element_that_has_not_been_filled_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_not_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert not file.keys()


def test_GIVEN_element_that_has_been_set_to_zero_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_not_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    spinner.setValue(0)
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert not file.keys()


def test_GIVEN_element_that_has_been_filled_in_WHEN_creating_dataset_from_spinner_THEN_dataset_is_created(
    file, qtbot
):
    nexus_string = "advanced_option_1"
    spinner = QSpinBox()
    spinner.setValue(1024)
    qtbot.addWidget(spinner)

    StreamFieldsWidget._create_dataset_from_spinner(file, {nexus_string: spinner})

    assert nexus_string in file
