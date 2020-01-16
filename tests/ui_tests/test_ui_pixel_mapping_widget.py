import pytest
from PySide2.QtCore import Qt

from nexus_constructor.pixel_mapping_widget import PixelMappingWidget

CYLINDER_TEXT = "cylinder"
ID_NO = 3


@pytest.fixture(scope="function")
def pixel_mapping_widget(qtbot, template):
    return PixelMappingWidget(template, ID_NO, CYLINDER_TEXT)


def test_GIVEN_id_number_and_text_WHEN_creating_pixel_mapping_widget_THEN_widget_is_created_with_expected_values(
    pixel_mapping_widget
):

    assert pixel_mapping_widget.pixelIDLabel.text() == "Pixel ID for {} #{}:".format(
        CYLINDER_TEXT, ID_NO
    )


def test_GIVEN_id_WHEN_calling_set_id_THEN_id_is_set(pixel_mapping_widget):

    id = 5
    pixel_mapping_widget.id = id
    assert pixel_mapping_widget.pixelIDLineEdit.text() == str(id)


def test_GIVEN_id_has_been_given_WHEN_calling_get_id_THEN_id_is_returned(
    qtbot, pixel_mapping_widget
):

    id = 5
    qtbot.keyClick(pixel_mapping_widget.pixelIDLineEdit, Qt.Key_5)
    assert pixel_mapping_widget.id == id


def test_GIVEN_id_has_not_been_given_WHEN_calling_get_id_THEN_none_is_returned(
    pixel_mapping_widget
):

    assert pixel_mapping_widget.id is None
