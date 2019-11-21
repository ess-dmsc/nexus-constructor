import pytest

from nexus_constructor.field_attrs import FieldAttrsDialog
import numpy as np
from tests.helpers import file  # noqa: F401


@pytest.mark.parametrize("attr_val", ["test", 123, 1.1, np.ushort(12)])
def test_GIVEN_existing_field_with_attr_WHEN_editing_component_THEN_both_field_and_attrs_are_filled_in_correctly(
    qtbot, file, attr_val
):
    attr_key = "units"

    ds = file.create_dataset(name="test", data=123)
    ds.attrs[attr_key] = attr_val

    dialog = FieldAttrsDialog()

    qtbot.addWidget(dialog)

    dialog.fill_existing_attrs(ds)

    assert len(dialog.get_attrs()) == 1
    assert dialog.get_attrs()[attr_key] == attr_val
