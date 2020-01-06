from unittest.mock import patch

import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QListWidget

from nexus_constructor.field_attrs import FieldAttrsDialog, FieldAttrFrame
import numpy as np
from tests.helpers import file  # noqa: F401
from tests.ui_tests.ui_test_utils import show_and_close_window


def get_attribute_widget(index: int, list_widget: QListWidget) -> FieldAttrFrame:
    item = list_widget.item(index)
    return list_widget.itemWidget(item)


def add_attribute(field_attributes_dialog, qtbot):
    qtbot.mouseClick(field_attributes_dialog.add_button, Qt.LeftButton)


def add_array_attribute(field_attributes_dialog, qtbot):
    add_attribute(field_attributes_dialog, qtbot)
    widget = get_attribute_widget(0, field_attributes_dialog.list_widget)
    widget.array_or_scalar_combo.setCurrentText("Array")
    return widget


@pytest.fixture(scope="function")
def field_attributes_dialog(qtbot, template):
    field_attributes_dialog = FieldAttrsDialog(template)
    qtbot.addWidget(field_attributes_dialog)
    return field_attributes_dialog


@pytest.mark.parametrize("attr_val", ["test", 123, 1.1, np.ushort(12)])
def test_GIVEN_existing_field_with_attr_WHEN_editing_component_THEN_both_field_and_attrs_are_filled_in_correctly(
    qtbot, file, attr_val, field_attributes_dialog
):
    attr_key = "units"

    ds = file.create_dataset(name="test", data=123)
    ds.attrs[attr_key] = attr_val

    field_attributes_dialog.fill_existing_attrs(ds)

    assert len(field_attributes_dialog.get_attrs()) == 1
    assert field_attributes_dialog.get_attrs()[attr_key] == attr_val


def test_GIVEN_add_attribute_button_pressed_WHEN_changing_attributes_THEN_new_attribute_is_created(
    qtbot, field_attributes_dialog
):
    add_attribute(field_attributes_dialog, qtbot)
    assert field_attributes_dialog.list_widget.count() == 1


def test_GIVEN_remove_attribute_button_pressed_WHEN_changing_attributes_THEN_selected_attribute_is_removed(
    qtbot, field_attributes_dialog
):
    add_attribute(field_attributes_dialog, qtbot)
    qtbot.mouseClick(
        get_attribute_widget(0, field_attributes_dialog.list_widget), Qt.LeftButton
    )
    qtbot.mouseClick(field_attributes_dialog.remove_button, Qt.LeftButton)
    assert field_attributes_dialog.list_widget.count() == 0


def test_GIVEN_data_type_changes_WHEN_editing_component_THEN_validate_method_is_called(
    qtbot, field_attributes_dialog
):
    add_attribute(field_attributes_dialog, qtbot)
    widget = get_attribute_widget(0, field_attributes_dialog.list_widget)

    with patch(
        "nexus_constructor.field_attrs.FieldValueValidator.validate"
    ) as mock_validate:
        widget.attr_dtype_combo.setCurrentIndex(2)
        mock_validate.assert_called_once()


def test_GIVEN_edit_array_button_pressed_WHEN_attribute_is_an_array_THEN_array_widget_opens(
    qtbot, field_attributes_dialog
):
    widget = add_array_attribute(field_attributes_dialog, qtbot)

    qtbot.mouseClick(widget.array_edit_button, Qt.LeftButton)
    assert widget.dialog.isVisible()


def test_GIVEN_attribute_is_an_array_WHEN_getting_data_THEN_array_is_returned(
    qtbot, field_attributes_dialog
):
    widget = add_array_attribute(field_attributes_dialog, qtbot)

    data = np.arange(9).reshape((3, 3))
    qtbot.mouseClick(widget.array_edit_button, Qt.LeftButton)
    widget.dialog.model.array = data

    attribute_name = "AttributeName"
    qtbot.keyClicks(widget.attr_name_lineedit, attribute_name)

    name, value = widget.value
    assert name == attribute_name
    assert np.array_equal(value, data)


def test_GIVEN_array_and_attribute_name_set_WHEN_changing_attribute_THEN_array_attribute_set(
    qtbot, field_attributes_dialog
):
    widget = add_array_attribute(field_attributes_dialog, qtbot)
    data = np.arange(9).reshape((3, 3))
    widget.value = ("AttributeName", data)

    assert np.array_equal(widget.array, data)


def test_GIVEN_type_changed_to_array_WHEN_changing_attribute_THEN_edit_array_button_is_visible(
    qtbot, field_attributes_dialog
):
    widget = add_array_attribute(field_attributes_dialog, qtbot)
    widget.type_changed("Array")
    show_and_close_window(qtbot, field_attributes_dialog)
    assert widget.array_edit_button.isVisible()
    assert not widget.attr_value_lineedit.isVisible()


def test_GIVEN_type_changed_to_scalar_WHEN_changing_attribute_THEN_value_line_edit_is_visible(
    qtbot, field_attributes_dialog
):
    widget = add_array_attribute(field_attributes_dialog, qtbot)
    widget.type_changed("Scalar")
    show_and_close_window(qtbot, field_attributes_dialog)
    assert not widget.array_edit_button.isVisible()
    assert widget.attr_value_lineedit.isVisible()


def test_GIVEN_attribute_value_is_byte_string_WHEN_filling_existing_values_THEN_string_is_decoded_in_lineedit(
    qtbot, field_attributes_dialog, file
):
    attribute_value_string = "yards"

    ds = file.create_dataset(name="test", data=123)
    ds.attrs["units"] = attribute_value_string.encode("utf-8")

    field_attributes_dialog.fill_existing_attrs(ds)
    assert (
        field_attributes_dialog.list_widget.itemWidget(
            field_attributes_dialog.list_widget.item(0)
        ).attr_value_lineedit.text()
        == attribute_value_string
    )
