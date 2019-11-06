import pytest
from PySide2.QtWidgets import QWidget

from nexus_constructor.pixel_mapping_widget import PixelMappingWidget

CYLINDER_TEXT = "cylinder"
ID = 3


@pytest.fixture(scope="function")
def template(qtbot):
    template = QWidget()
    return template


@pytest.fixture(scope="function")
def pixel_mapping_widget(qtbot, template):
    return PixelMappingWidget(template, ID, CYLINDER_TEXT)


def test_GIVEN_id_number_and_text_WHEN_creating_pixel_mapping_widget_THEN_widget_is_created_with_expected_values(
    pixel_mapping_widget
):

    assert pixel_mapping_widget.pixelIDLabel.text() == "Pixel ID for {} #{}:".format(
        CYLINDER_TEXT, ID
    )
