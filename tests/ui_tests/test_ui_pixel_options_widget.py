from unittest.mock import mock_open

import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget
from mock import patch

from nexus_constructor.pixel_options import PixelOptions
from tests.ui_tests.ui_test_utils import (
    systematic_button_press,
    show_and_close_window,
    RED_SPIN_BOX_STYLE_SHEET,
    WHITE_SPIN_BOX_STYLE_SHEET,
)

VALID_CUBE_OFF_FILE = (
    "OFF\n"
    "#  cube.off\n"
    "#  A cube\n"
    "8 6 0\n"
    "-0.500000 -0.500000 0.500000\n"
    "0.500000 -0.500000 0.500000\n"
    "-0.500000 0.500000 0.500000\n"
    "0.500000 0.500000 0.500000\n"
    "-0.500000 0.500000 -0.500000\n"
    "0.500000 0.500000 -0.500000\n"
    "-0.500000 -0.500000 -0.500000\n"
    "-0.500000 0.500000 0.500000\n"
    "4 0 1 3 2\n"
    "4 2 3 5 4\n"
    "4 4 5 7 6\n"
    "4 6 7 1 0\n"
    "4 1 7 5 3\n"
    "4 6 0 2 4\n"
)


@pytest.fixture(scope="function")
def template(qtbot):
    template = QWidget()
    return template


@pytest.fixture(scope="function")
def pixel_options(qtbot, template):
    pixel_options = PixelOptions()
    template.ui = pixel_options
    template.ui.setupUi(template)
    qtbot.addWidget(template)
    return pixel_options


def manually_create_pixel_mapping_list(pixel_options: PixelOptions):
    """
    Manually creates a pixel mapping list by passing a mesh filename and opening a mesh by mocking open.
    :param pixel_options: The PixelOptions object that deals with opening the mesh file.
    """
    with patch(
        "nexus_constructor.geometry.geometry_loader.open",
        mock_open(read_data=VALID_CUBE_OFF_FILE),
    ):
        pixel_options.populate_pixel_mapping_list("filename.off")


def test_UI_GIVEN_component_with_pixel_fields_WHEN_choosing_pixel_layout_THEN_single_pixel_is_selected_and_visible_by_default(
    qtbot, template, pixel_options
):
    # Check that the single grid button is checked and the pixel grid option is visible by default
    assert pixel_options.singlePixelRadioButton.isChecked()
    assert pixel_options.pixelOptionsStack.currentIndex() == 0


def test_UI_GIVEN_user_selects_entire_shape_WHEN_choosing_pixel_layout_THEN_pixel_grid_box_becomes_invisible(
    qtbot, template, pixel_options
):
    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    # Check that the pixel mapping items are visible
    assert pixel_options.pixelOptionsStack.currentIndex() == 1


def test_UI_GIVEN_user_selects_no_pixels_THEN_pixel_grid_and_pixel_mapping_options_become_invisible(
    qtbot, template, pixel_options
):

    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, pixel_options.noPixelsButton)

    # Check that the pixel mapping items are visible
    assert not pixel_options.pixelOptionsStack.isVisible()


def test_UI_GIVEN_user_selects_pixel_grid_THEN_pixel_grid_is_set_to_true_in_ok_validator(
    qtbot, template, pixel_options
):

    # Press the pixel grid button
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    # Check that the pixel grid boolean has become true
    assert pixel_options.pixel_validator.pixel_grid_is_valid
    # Check that the pixel_mapping boolean has become false
    assert not pixel_options.pixel_validator.pixel_mapping_is_valid


def test_UI_GIVEN_user_selects_no_pixels_and_gives_valid_input_THEN_add_component_button_is_enabled(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.noPixelsButton)

    # Check that the add component button is enabled
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_valid_pixel_grid_WHEN_entering_pixel_options_THEN_changing_to_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change the first ID
    qtbot.keyClick(pixel_options.firstIDSpinBox, Qt.Key_Up)
    qtbot.keyClick(pixel_options.firstIDSpinBox, Qt.Key_Up)
    show_and_close_window(qtbot, template)

    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, False]

    # Switch to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, True]


def test_UI_GIVEN_zero_for_both_row_and_column_count_WHEN_entering_pixel_grid_options_THEN_both_fields_become_red(
    qtbot, template, pixel_options
):

    count_fields = [pixel_options.rowCountSpinBox, pixel_options.columnCountSpinBox]

    # Enter zero in the count fields by pressing the down key
    for field in count_fields:
        qtbot.keyClick(field, Qt.Key_Down)

    # Check that the background has turned red because the input in invalid
    for field in count_fields:
        assert field.styleSheet() == RED_SPIN_BOX_STYLE_SHEET


def test_UI_GIVEN_invalid_pixel_grid_WHEN_entering_pixel_options_THEN_changing_to_valid_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)

    # Change to the pixel mapping layout
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel mapping valid
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "22")

    # Check the test for unacceptable pixel states gives False
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_valid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_invalid_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel mapping invalid
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Check that test for unacceptable pixel states gives True
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, True]


def test_UI_GIVEN_invalid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_valid_pixel_grid_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    manually_create_pixel_mapping_list(pixel_options)

    # Give input that will be rejected by the validator
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Switch to pixel grid
    systematic_button_press(qtbot, template, pixel_options.singlePixelRadioButton)

    # Check that the test for unacceptable pixel states gives False
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_valid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_invalid_pixel_grid_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)

    manually_create_pixel_mapping_list(pixel_options)

    # Give valid input
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "22")

    # Change to pixel grid
    systematic_button_press(qtbot, template, pixel_options.singlePixelRadioButton)

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)

    # Check that the test for unacceptable pixel states gives True
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [True, False]


def test_UI_GIVEN_invalid_mapping_and_grid_WHEN_entering_pixel_options_THEN_changing_to_no_pixels_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entireShapeRadioButton)
    manually_create_pixel_mapping_list(pixel_options)

    # Give invalid input
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Change to no pixels
    systematic_button_press(qtbot, template, pixel_options.noPixelsButton)

    # Check that the test for unacceptable pixel states gives false
    assert pixel_options.pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_nothing_WHEN_pixel_mapping_options_are_visible_THEN_options_have_expected_default_values(
    qtbot, template, pixel_options
):

    # Check that the pixel-related fields start out with the expected default values
    assert pixel_options.rowCountSpinBox.value() == 1
    assert pixel_options.columnCountSpinBox.value() == 1
    assert pixel_options.rowHeightSpinBox.value() == 0.5
    assert pixel_options.columnWidthSpinBox.value() == 0.5
    assert pixel_options.firstIDSpinBox.value() == 0
    assert (
        pixel_options.startCountingComboBox.currentText()
        == list(pixel_options.initial_count_corner.keys())[0]
    )
    assert (
        pixel_options.countFirstComboBox.currentText()
        == list(pixel_options.count_direction.keys())[0]
    )


def test_UI_GIVEN_nonzero_value_for_both_row_and_column_count_WHEN_entering_pixel_grid_options_THEN_both_fields_become_white(
    qtbot, template, pixel_options
):

    count_fields = [pixel_options.rowCountSpinBox, pixel_options.columnCountSpinBox]

    # Set both spin boxes to zero
    for field in count_fields:
        qtbot.keyClick(field, Qt.Key_Down)

    # Set both spin boxes to one
    for field in count_fields:
        qtbot.keyClick(field, Qt.Key_Up)

    # Check that the background has turned white because the input is acceptable
    for field in count_fields:
        assert field.styleSheet() == WHITE_SPIN_BOX_STYLE_SHEET


def test_UI_GIVEN_row_count_is_zero_THEN_row_height_becomes_disabled(
    qtbot, template, pixel_options
):

    # Enter zero in the row count field by pressing the down key
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)

    # Check that the row height spin box is now disabled
    assert not pixel_options.rowHeightSpinBox.isEnabled()


def test_UI_GIVEN_row_count_is_not_zero_THEN_row_height_becomes_enabled(
    qtbot, template, pixel_options
):

    # Make the row count go to zero and then back to one again
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.rowCountSpinBox, Qt.Key_Up)

    # Check that the row height spin box is now enabled
    assert pixel_options.rowHeightSpinBox.isEnabled()


def test_UI_GIVEN_column_count_is_zero_THEN_column_width_becomes_disabled(
    qtbot, template, pixel_options
):

    # Enter zero in the column count field by pressing the down key
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)

    # Check that the column width spin box is now disabled
    assert not pixel_options.columnWidthSpinBox.isEnabled()


def test_UI_GIVEN_column_count_is_not_zero_THEN_column_width_becomes_enabled(
    qtbot, template, pixel_options
):

    # Make the column count go to zero and then back to one again
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Down)
    qtbot.keyClick(pixel_options.columnCountSpinBox, Qt.Key_Up)

    # Check that the column width spin box is now enabled
    assert pixel_options.columnWidthSpinBox.isEnabled()
