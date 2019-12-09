import pytest
from PySide2.QtCore import Qt

from nexus_constructor.field_attrs import FieldAttrsDialog
import numpy as np
from tests.helpers import file  # noqa: F401


@pytest.fixture(scope="function")
def field_attrs_dialog(qtbot):

    dialog = FieldAttrsDialog()
    qtbot.addWidget(dialog)
    return dialog


@pytest.mark.parametrize("attr_val", ["test", 123, 1.1, np.ushort(12)])
def test_GIVEN_existing_field_with_attr_WHEN_editing_component_THEN_both_field_and_attrs_are_filled_in_correctly(
    qtbot, file, attr_val, field_attrs_dialog
):
    attr_key = "units"

    ds = file.create_dataset(name="test", data=123)
    ds.attrs[attr_key] = attr_val

    field_attrs_dialog.fill_existing_attrs(ds)

    assert len(field_attrs_dialog.get_attrs()) == 1
    assert field_attrs_dialog.get_attrs()[attr_key] == attr_val


def test_GIVEN_add_attribute_button_pressed_WHEN_changing_attributes_THEN_new_attribute_is_created(
    qtbot, field_attrs_dialog
):

    qtbot.mouseClick(field_attrs_dialog.add_button, Qt.LeftButton)
    assert field_attrs_dialog.list_widget.count() == 1


def test_GIVEN_remove_attribute_button_pressed_WHEN_changing_attributes_THEN_selected_attribute_is_removed(
    qtbot, field_attrs_dialog
):

    qtbot.mouseClick(field_attrs_dialog.add_button, Qt.LeftButton)
    field_attrs_dialog.list_widget.setCurrentRow(0)
    qtbot.mouseClick(field_attrs_dialog.remove_button, Qt.LeftButton)
    assert field_attrs_dialog.list_widget.count() == 0
