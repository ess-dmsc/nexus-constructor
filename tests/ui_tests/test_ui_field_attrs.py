import pytest
from PySide2.QtWidgets import QDialog

from nexus_constructor.field_attrs import FieldAttrsDialog
import numpy as np
from tests.helpers import file  # noqa: F401


@pytest.fixture(scope="function")
def template(qtbot):
    return QDialog()


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


def test_GIVEN_attribute_value_is_byte_string_WHEN_setting_value_THEN_string_is_decoded_in_lineedit(
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
