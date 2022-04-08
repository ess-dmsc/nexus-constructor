from io import StringIO
from unittest.mock import mock_open

import numpy as np
import pytest
from mock import patch
from PySide2.QtCore import Qt

from nexus_constructor.geometry.geometry_loader import load_geometry_from_file_object
from nexus_constructor.geometry.pixel_data import (
    Corner,
    CountDirection,
    PixelGrid,
    PixelMapping,
)
from nexus_constructor.geometry.pixel_data_utils import (
    get_detector_ids_from_pixel_grid,
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import OFFGeometryNexus
from nexus_constructor.pixel_options import (
    COUNT_DIRECTION,
    INITIAL_COUNT_CORNER,
    PIXEL_GRID_STACK_INDEX,
    PIXEL_MAPPING_STACK_INDEX,
    PixelOptions,
    data_is_an_array_with_more_than_one_element,
)
from tests.ui_tests.ui_test_utils import (
    CORRECT_CUBE_FACES,
    CORRECT_OCTA_FACES,
    VALID_CUBE_OFF_FILE,
    VALID_OCTA_OFF_FILE,
    show_and_close_window,
    systematic_button_press,
)


@pytest.fixture(scope="function")
def pixel_options(qtbot, template):
    pixel_options = PixelOptions()
    template.ui = pixel_options
    template.ui.setupUi(template)
    qtbot.addWidget(template)
    return pixel_options


@pytest.fixture(scope="function")
def pixel_grid():

    pixel_grid = PixelGrid()
    pixel_grid.rows = 5
    pixel_grid.columns = 4
    pixel_grid.row_height = 1.5
    pixel_grid.col_width = 0.4
    pixel_grid.first_id = 2
    pixel_grid.count_direction = CountDirection.ROW
    pixel_grid.initial_count_corner = Corner.BOTTOM_LEFT

    return pixel_grid


@pytest.fixture(scope="function")
def pixel_mapping_with_six_pixels():
    return PixelMapping([i if i % 3 != 0 else None for i in range(CORRECT_CUBE_FACES)])


@pytest.fixture(scope="function")
def pixel_mapping_with_single_pixel():
    return PixelMapping([3])


def widgets_match_pixel_mapping(
    pixel_mapping: PixelMapping, pixel_options: PixelOptions
) -> bool:
    """
    Checks that the contents of the pixel mapping widgets match the contents of a PixelMapping object.
    :param pixel_mapping: The Pixel Mapping object that is being edited via the PixelOptions interface.
    :param pixel_options: The PixelOptions widget.
    :return: True if the widget and PixelMapping match. False otherwise.
    """
    for i in range(len(pixel_mapping.pixel_ids)):
        id_in_interface = pixel_options.get_id_at_index(i)

        if not id_in_interface:
            if pixel_mapping.pixel_ids[i] is not None:
                return False
        else:
            if int(id_in_interface) != pixel_mapping.pixel_ids[i]:
                return False

    return True


def replace_pixel_mapping_in_off_component(
    component: Component, pixel_mapping: PixelMapping, off_geometry: OFFGeometryNexus
):
    """
    Change the pixel mapping that is currently stored in a Component. Used to see if everything behaves correctly even
    for pixel data with 'special' properties.
    :param component: The component to have its pixel data replaced.
    :param pixel_mapping: The PixelMapping or PixielGrid object.
    :param off_geometry: The OffGeometry.
    """
    component.record_pixel_mapping(pixel_mapping)
    component.set_off_shape(off_geometry, pixel_data=pixel_mapping)


def replace_pixel_grid_in_off_component(
    component: Component, pixel_grid: PixelGrid, off_geometry: OFFGeometryNexus
):
    """
    Change the pixel grid that is currently stored in a Component. Used to see if everything behaves correctly even
    for pixel data with 'special' properties.
    :param component: The component to have its pixel data replaced.
    :param pixel_grid: The PixelGrid object.
    :param off_geometry: The OffGeometry.
    """
    component.record_pixel_grid(pixel_grid)
    component.set_off_shape(off_geometry, pixel_data=pixel_grid)


@pytest.fixture(scope="function")
def component():
    return Component("Component", [])


@pytest.fixture(scope="function")
def off_geometry_file(pixel_mapping_with_six_pixels):

    off_string = StringIO("".join(VALID_CUBE_OFF_FILE))
    off_geometry = load_geometry_from_file_object(off_string, ".off", "m")
    return off_geometry


@pytest.fixture(scope="function")
def off_component_with_pixel_grid(pixel_grid, off_geometry_file, component):
    component.record_pixel_grid(pixel_grid)
    component.set_off_shape(off_geometry_file, pixel_data=pixel_grid)
    return component


@pytest.fixture(scope="function")
def off_component_with_pixel_mapping(
    pixel_mapping_with_six_pixels,
    off_geometry_file,
    component,
):
    component.record_pixel_mapping(pixel_mapping_with_six_pixels)
    component.set_off_shape(off_geometry_file, pixel_data=pixel_mapping_with_six_pixels)
    return component


@pytest.fixture(scope="function")
def off_component_with_no_pixel_data(off_geometry_file, component):
    component.set_off_shape(off_geometry_file)
    return component


@pytest.fixture(scope="function")
def cylindrical_component_with_pixel_mapping(
    component, pixel_mapping_with_single_pixel
):
    component.record_pixel_mapping(pixel_mapping_with_single_pixel)
    return component


def manually_create_pixel_mapping_list(
    pixel_options: PixelOptions,
    file_contents: str = VALID_CUBE_OFF_FILE,
    filename: str = "filename.off",
):
    """
    Manually creates a pixel mapping list by passing a mesh filename and opening a mesh by mocking open.
    :param pixel_options: The PixelOptions object that deals with opening the mesh file.
    :param file_contents: The OFF file in string format.
    :param filename: The filename passed to the mesh-opening method. Must end in off.
    """
    with patch(
        "nexus_constructor.geometry.geometry_loader.open",
        mock_open(read_data=file_contents),
    ):
        pixel_options.populate_pixel_mapping_list_with_mesh(filename)


def test_UI_GIVEN_component_with_pixel_fields_WHEN_choosing_pixel_layout_THEN_single_pixel_is_selected_and_visible_by_default(
    qtbot, template, pixel_options
):
    show_and_close_window(qtbot, template)

    # Check that the single grid button is checked and the pixel grid option is visible by default
    assert pixel_options.single_pixel_radio_button.isChecked()
    assert pixel_options.pixel_options_stack.isVisible()
    assert pixel_options.pixel_options_stack.currentIndex() == 0


def test_UI_GIVEN_user_selects_entire_shape_WHEN_choosing_pixel_layout_THEN_pixel_mapping_becomes_visible(
    qtbot, template, pixel_options
):
    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    # Check that the pixel mapping items are visible
    assert pixel_options.pixel_options_stack.isVisible()
    assert pixel_options.pixel_options_stack.currentIndex() == 1


def test_UI_GIVEN_user_selects_no_pixels_WHEN_changing_pixel_layout_THEN_pixel_options_stack_becomes_invisible(
    qtbot, template, pixel_options
):

    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, pixel_options.no_pixels_button)

    # Check that the pixel mapping items are visible
    assert not pixel_options.pixel_options_stack.isVisible()


def test_UI_GIVEN_user_selects_single_pixel_WHEN_changing_pixel_layout_THEN_pixel_grid_becomes_visible(
    qtbot, template, pixel_options
):

    # Single pixel is selected by default so switch to entire shape then switch back
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    systematic_button_press(qtbot, template, pixel_options.single_pixel_radio_button)

    assert pixel_options.pixel_options_stack.isVisible()
    assert pixel_options.pixel_options_stack.currentIndex() == 0


def test_UI_GIVEN_user_selects_pixel_grid_WHEN_changing_pixel_layout_THEN_pixel_grid_is_set_to_true_in_ok_validator(
    qtbot, template, pixel_options
):

    # Press the pixel grid button
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    # Check that the pixel grid boolean has become true
    assert pixel_options._pixel_validator.pixel_grid_is_valid
    # Check that the pixel_mapping boolean has become false
    assert not pixel_options._pixel_validator.pixel_mapping_is_valid


def test_UI_GIVEN_user_selects_no_pixels_and_gives_valid_nonpixel_input_WHEN_changing_pixel_layout_THEN_add_component_button_is_enabled(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.no_pixels_button)

    # Check that the add component button is enabled
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_valid_pixel_grid_WHEN_entering_pixel_options_THEN_changing_to_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change the first ID
    qtbot.keyClick(pixel_options.first_id_spin_box, Qt.Key_Up)
    qtbot.keyClick(pixel_options.first_id_spin_box, Qt.Key_Up)
    show_and_close_window(qtbot, template)

    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]

    # Switch to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, True]


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_invalid_pixel_grid_WHEN_entering_pixel_options_THEN_changing_to_valid_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Down)

    # Change to the pixel mapping layout
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel mapping valid
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "22")

    # Check the test for unacceptable pixel states gives False
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_valid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_invalid_pixel_mapping_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Down)

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    manually_create_pixel_mapping_list(pixel_options)

    # Make the pixel mapping invalid
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Check that test for unacceptable pixel states gives True
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, True]


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_invalid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_valid_pixel_grid_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    manually_create_pixel_mapping_list(pixel_options)

    # Give input that will be rejected by the validator
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Switch to pixel grid
    systematic_button_press(qtbot, template, pixel_options.single_pixel_radio_button)

    # Check that the test for unacceptable pixel states gives False
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_valid_pixel_mapping_WHEN_entering_pixel_options_THEN_changing_to_invalid_pixel_grid_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)

    manually_create_pixel_mapping_list(pixel_options)

    # Give valid input
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "22")

    # Change to pixel grid
    systematic_button_press(qtbot, template, pixel_options.single_pixel_radio_button)

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Down)

    # Check that the test for unacceptable pixel states gives True
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_invalid_mapping_and_grid_WHEN_entering_pixel_options_THEN_changing_to_no_pixels_causes_validity_to_change(
    qtbot, template, pixel_options
):

    # Make the pixel grid invalid
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Down)

    # Change to pixel mapping
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options)

    # Give invalid input
    qtbot.keyClicks(pixel_options.pixel_mapping_widgets[0].pixelIDLineEdit, "abc")

    # Change to no pixels
    systematic_button_press(qtbot, template, pixel_options.no_pixels_button)

    # Check that the test for unacceptable pixel states gives false
    assert pixel_options._pixel_validator.unacceptable_pixel_states() == [False, False]


def test_UI_GIVEN_nothing_WHEN_pixel_mapping_options_are_visible_THEN_options_have_expected_default_values(
    qtbot, template, pixel_options
):

    # Check that the pixel-related fields start out with the expected default values
    assert pixel_options.row_count_spin_box.value() == 1
    assert pixel_options.column_count_spin_box.value() == 1
    assert pixel_options.row_height_spin_box.value() == 0.5
    assert pixel_options.column_width_spin_box.value() == 0.5
    assert pixel_options.first_id_spin_box.value() == 0
    assert (
        pixel_options.start_counting_combo_box.currentText()
        == list(INITIAL_COUNT_CORNER.keys())[0]
    )
    assert (
        pixel_options.count_first_combo_box.currentText()
        == list(COUNT_DIRECTION.keys())[0]
    )


def test_UI_GIVEN_row_count_is_not_zero_WHEN_entering_pixel_grid_THEN_row_height_becomes_enabled(
    qtbot, template, pixel_options
):

    # Make the row count go to zero and then back to one again
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.row_count_spin_box, Qt.Key_Up)

    # Check that the row height spin box is now enabled
    assert pixel_options.row_height_spin_box.isEnabled()


def test_UI_GIVEN_column_count_is_not_zero_WHEN_entering_pixel_grid_THEN_column_width_becomes_enabled(
    qtbot, template, pixel_options
):

    # Make the column count go to zero and then back to one again
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Down)
    qtbot.keyClick(pixel_options.column_count_spin_box, Qt.Key_Up)

    # Check that the column width spin box is now enabled
    assert pixel_options.column_width_spin_box.isEnabled()


def test_UI_GIVEN_user_provides_mesh_file_WHEN_entering_pixel_mapping_THEN_pixel_mapping_list_is_populated_with_correct_number_of_widgets(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options)
    assert pixel_options.get_pixel_mapping_table_size() == CORRECT_CUBE_FACES


def test_UI_GIVEN_mesh_file_changes_WHEN_entering_pxixel_mapping_THEN_pixel_mapping_list_changes(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options)
    manually_create_pixel_mapping_list(pixel_options, VALID_OCTA_OFF_FILE)
    assert pixel_options.get_pixel_mapping_table_size() == CORRECT_OCTA_FACES


def test_UI_GIVEN_cylinder_number_WHEN_entering_pixel_mapping_THEN_pixel_mapping_list_is_populated_with_correct_number_of_widgets(
    qtbot, template, pixel_options
):

    cylinder_number = 6
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    pixel_options.populate_pixel_mapping_list_with_cylinder_number(cylinder_number)
    assert pixel_options.get_pixel_mapping_table_size() == cylinder_number


def test_UI_GIVEN_cylinder_number_changes_WHEN_entering_pixel_mapping_THEN_pixel_mapping_list_changes(
    qtbot, template, pixel_options
):

    first_cylinder_number = 6
    second_cylinder_number = first_cylinder_number - 1
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    pixel_options.populate_pixel_mapping_list_with_cylinder_number(
        first_cylinder_number
    )
    pixel_options.populate_pixel_mapping_list_with_cylinder_number(
        second_cylinder_number
    )
    assert pixel_options.get_pixel_mapping_table_size() == second_cylinder_number


def test_UI_GIVEN_user_switches_to_pixel_mapping_WHEN_creating_component_THEN_pixel_mapping_signal_is_emitted(
    qtbot, template, pixel_options
):

    global emitted
    emitted = False

    def check_that_signal_is_emitted():
        global emitted
        emitted = not emitted

    pixel_options.pixel_mapping_button_pressed.connect(check_that_signal_is_emitted)
    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    assert emitted


def test_UI_GIVEN_mesh_file_WHEN_generating_mapping_list_THEN_filename_returned_by_pixel_options_matches_filename_of_mesh(
    qtbot, template, pixel_options
):

    filename = "a/mesh/file.off"

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options, filename=filename)

    assert pixel_options.get_current_mapping_filename() == filename


def test_UI_GIVEN_user_opens_two_different_files_WHEN_creating_off_geometry_THEN_filename_stored_by_pixel_options_changes(
    qtbot, template, pixel_options
):

    first_filename = "a/mesh/file.off"
    second_filename = "a/different/mesh/file.off"

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options, filename=first_filename)
    manually_create_pixel_mapping_list(pixel_options, filename=second_filename)

    assert pixel_options.get_current_mapping_filename() == second_filename


def test_UI_GIVEN_user_switches_from_mesh_to_cylinder_WHEN_creating_cylindrical_geometry_THEN_pixel_mapping_filename_is_changed_to_none(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    manually_create_pixel_mapping_list(pixel_options)

    pixel_options.populate_pixel_mapping_list_with_cylinder_number(12)

    assert pixel_options.get_current_mapping_filename() is None


def test_UI_GIVEN_entire_shape_button_is_not_selected_WHEN_calling_pixel_mapping_method_THEN_pixel_mapping_method_returns_without_populating_list(
    qtbot, template, pixel_options
):

    manually_create_pixel_mapping_list(pixel_options)
    assert pixel_options.get_pixel_mapping_table_size() == 0

    pixel_options.populate_pixel_mapping_list_with_cylinder_number(4)
    assert pixel_options.get_pixel_mapping_table_size() == 0


@pytest.mark.skip(reason="editing table widget using qbot is unpractical")
def test_UI_GIVEN_mapping_list_provided_by_user_WHEN_entering_pixel_data_THEN_calling_generate_pixel_data_returns_mapping_with_list_that_matches_user_input(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.entire_shape_radio_button)
    num_faces = 6
    expected_id_list = [i if i % 2 != 0 else None for i in range(num_faces)]
    manually_create_pixel_mapping_list(pixel_options)

    for i in range(num_faces):
        table_cell = pixel_options.pixel_mapping_table_widget.cellWidget(i, 1)
        qtbot.keyClicks(
            table_cell,
            str(expected_id_list[i]),
        )

    assert pixel_options.generate_pixel_data().pixel_ids == expected_id_list


def test_UI_GIVEN_no_pixels_button_is_pressed_WHEN_entering_pixel_data_THEN_calling_generate_pixel_data_returns_none(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.no_pixels_button)
    assert pixel_options.generate_pixel_data() is None


def test_GIVEN_scalar_value_WHEN_calling_check_data_is_an_array_THEN_returns_false():

    data = 3.5
    assert not data_is_an_array_with_more_than_one_element(data)


def test_GIVEN_array_with_single_element_WHEN_calling_check_data_is_an_array_THEN_returns_false():

    data = np.array([3.5])
    assert not data_is_an_array_with_more_than_one_element(data)


def test_GIVEN_array_with_multiple_elements_WHEN_calling_check_data_is_an_array_THEN_returns_true():

    data = np.arange(5)
    assert data_is_an_array_with_more_than_one_element(data)


def test_GIVEN_array_of_pixel_offsets_WHEN_finding_row_properties_THEN_expected_values_are_returned(
    pixel_options, pixel_grid
):
    y_pixel_offsets = get_y_offsets_from_pixel_grid(pixel_grid)
    n_rows, row_height = pixel_options._get_row_information(y_pixel_offsets)

    assert n_rows == pixel_grid.rows
    assert np.isclose(row_height, pixel_grid.row_height)


def test_GIVEN_pixel_grid_with_single_row_WHEN_finding_row_properties_THEN_expected_values_are_returned(
    pixel_options, pixel_grid
):
    pixel_grid.rows = 1
    y_pixel_offsets = get_y_offsets_from_pixel_grid(pixel_grid)
    n_rows, row_height = pixel_options._get_row_information(y_pixel_offsets)

    assert n_rows == pixel_grid.rows
    assert row_height is None


def test_GIVEN_array_of_pixel_offsets_WHEN_finding_column_properties_THEN_expected_values_are_returned(
    pixel_options, pixel_grid
):
    x_pixel_offsets = get_x_offsets_from_pixel_grid(pixel_grid)
    n_columns, column_width = pixel_options._get_column_information(x_pixel_offsets)

    assert n_columns == pixel_grid.columns
    assert np.isclose(column_width, pixel_grid.col_width)


def test_GIVEN_pixel_grid_with_single_column_WHEN_finding_column_properties_THEN_expected_values_are_returned(
    pixel_options, pixel_grid
):
    pixel_grid.columns = 1
    x_pixel_offsets = get_x_offsets_from_pixel_grid(pixel_grid)

    n_columns, column_width = pixel_options._get_column_information(x_pixel_offsets)

    assert n_columns == pixel_grid.columns
    assert column_width is None


@pytest.mark.xfail(
    reason=(
        "The function for recovering Pixel Grid information expects an array with more"
        " than one column/row. A single row of pixels isn't handled yet."
    )
)
def test_GIVEN_row_of_pixels_WHEN_calling_get_detector_number_information_THEN_expected_start_counting_is_returned(
    pixel_options, pixel_grid
):
    pixel_options.rows = 1
    detector_numbers = get_detector_ids_from_pixel_grid(pixel_grid)

    _, start_counting_text, _ = pixel_options._get_detector_number_information(
        detector_numbers
    )

    assert start_counting_text in ["Right", "Left"]


@pytest.mark.xfail(
    reason=(
        "The function for recovering Pixel Grid information expects an array with more"
        " than one column/row. A single column of pixels isn't handled yet."
    )
)
def test_GIVEN_column_of_pixels_WHEN_calling_get_detector_number_information_THEN_expected_start_counting_is_returned(
    pixel_options, pixel_grid
):
    pixel_options.columns = 1
    detector_numbers = get_detector_ids_from_pixel_grid(pixel_grid)

    _, start_counting_text, _ = pixel_options._get_detector_number_information(
        detector_numbers
    )

    assert start_counting_text in ["Top", "Bottom"]


def test_GIVEN_detector_numbers_WHEN_calling_get_detector_number_information_THEN_expected_first_id_is_returned(
    pixel_options, pixel_grid
):
    pixel_grid.first_id = 4

    detector_numbers = get_detector_ids_from_pixel_grid(pixel_grid)
    first_id, _, _ = pixel_options._get_detector_number_information(detector_numbers)

    assert first_id == pixel_grid.first_id


def test_GIVEN_component_with_a_pixel_grid_WHEN_editing_a_component_THEN_pixel_grid_options_are_checked_and_visible(
    qtbot, template, pixel_options, off_component_with_pixel_grid
):
    pixel_options.fill_existing_entries(off_component_with_pixel_grid)
    show_and_close_window(qtbot, template)

    assert pixel_options.single_pixel_radio_button.isChecked()
    assert pixel_options.pixel_options_stack.isVisible()
    assert pixel_options.pixel_options_stack.currentIndex() == PIXEL_GRID_STACK_INDEX


def test_GIVEN_component_with_a_pixel_mapping_WHEN_editing_a_component_THEN_pixel_mapping_options_are_checked_and_visible(
    qtbot, template, pixel_options, off_component_with_pixel_mapping
):
    pixel_options.fill_existing_entries(off_component_with_pixel_mapping)
    show_and_close_window(qtbot, template)

    assert pixel_options.entire_shape_radio_button.isChecked()
    assert pixel_options.pixel_options_stack.isVisible()
    assert pixel_options.pixel_options_stack.currentIndex() == PIXEL_MAPPING_STACK_INDEX


def test_GIVEN_component_with_no_pixel_data_WHEN_editing_component_THEN_pixel_options_arent_visible(
    qtbot, template, pixel_options, off_component_with_no_pixel_data
):
    pixel_options.fill_existing_entries(off_component_with_no_pixel_data)
    show_and_close_window(qtbot, template)

    assert pixel_options.no_pixels_button.isChecked()
    assert not pixel_options.pixel_options_stack.isVisible()


def test_GIVEN_component_with_pixel_grid_WHEN_editing_a_component_THEN_pixel_grid_properties_are_recovered(
    pixel_options, pixel_grid, off_component_with_pixel_grid
):
    pixel_options.fill_existing_entries(off_component_with_pixel_grid)

    assert pixel_options.row_count_spin_box.value() == pixel_grid.rows
    assert pixel_options.column_count_spin_box.value() == pixel_grid.columns

    assert pixel_options.row_height_spin_box.value() == pixel_grid.row_height
    assert pixel_options.column_width_spin_box.value() == pixel_grid.col_width

    assert pixel_options.first_id_spin_box.value() == pixel_grid.first_id

    assert (
        INITIAL_COUNT_CORNER[pixel_options.start_counting_combo_box.currentText()]
        == pixel_grid.initial_count_corner
    )


@pytest.mark.parametrize("count_along", COUNT_DIRECTION.values())
def test_GIVEN_detector_numbers_WHEN_calling_get_detector_number_information_THEN_expected_count_direction_is_returned(
    pixel_options,
    pixel_grid,
    count_along,
    off_component_with_pixel_grid,
    off_geometry_file,
):
    pixel_grid.count_direction = count_along
    replace_pixel_grid_in_off_component(
        off_component_with_pixel_grid, pixel_grid, off_geometry_file
    )
    pixel_options.fill_existing_entries(off_component_with_pixel_grid)

    assert (
        COUNT_DIRECTION[pixel_options.count_first_combo_box.currentText()]
        == pixel_grid.count_direction
    )


@pytest.mark.parametrize("corner", INITIAL_COUNT_CORNER.values())
def test_GIVEN_detector_numbers_WHEN_calling_get_detector_number_information_THEN_expected_start_counting_are_returned(
    pixel_options, pixel_grid, corner, off_geometry_file, off_component_with_pixel_grid
):
    pixel_grid.initial_count_corner = corner
    replace_pixel_grid_in_off_component(
        off_component_with_pixel_grid, pixel_grid, off_geometry_file
    )
    pixel_options.fill_existing_entries(off_component_with_pixel_grid)

    assert (
        INITIAL_COUNT_CORNER[pixel_options.start_counting_combo_box.currentText()]
        == corner
    )


def test_GIVEN_component_with_pixel_mapping_WHEN_editing_pixel_data_THEN_correct_number_of_mapping_widgets_are_created(
    pixel_options, pixel_mapping_with_six_pixels, off_component_with_pixel_mapping
):
    pixel_options.fill_existing_entries(off_component_with_pixel_mapping)
    assert pixel_options.get_pixel_mapping_table_size() == len(
        pixel_mapping_with_six_pixels.pixel_ids
    )


def test_GIVEN_component_with_pixel_mapping_WHEN_editing_pixel_data_THEN_correct_ids_are_present(
    pixel_options, pixel_mapping_with_six_pixels, off_component_with_pixel_mapping
):
    pixel_options.fill_existing_entries(off_component_with_pixel_mapping)
    assert widgets_match_pixel_mapping(pixel_mapping_with_six_pixels, pixel_options)


def test_GIVEN_component_with_single_id_WHEN_editing_pixel_data_THEN_correct_number_of_mapping_widgets_are_created(
    pixel_options,
    pixel_mapping_with_six_pixels,
    off_component_with_pixel_mapping,
    off_geometry_file,
):
    pixel_mapping_with_six_pixels.pixel_ids = [
        None for _ in range(CORRECT_CUBE_FACES - 1)
    ] + [4]
    replace_pixel_mapping_in_off_component(
        off_component_with_pixel_mapping,
        pixel_mapping_with_six_pixels,
        off_geometry_file,
    )
    pixel_options.fill_existing_entries(off_component_with_pixel_mapping)

    assert widgets_match_pixel_mapping(pixel_mapping_with_six_pixels, pixel_options)


def test_GIVEN_cylindrical_geometry_WHEN_editing_pixel_mapping_with_single_pixel_THEN_pixel_data_is_recovered(
    pixel_options,
    cylindrical_component_with_pixel_mapping,
    pixel_mapping_with_single_pixel,
):
    cylindrical_geometry = cylindrical_component_with_pixel_mapping.set_cylinder_shape(
        pixel_data=pixel_mapping_with_single_pixel
    )
    pixel_options.fill_existing_entries(cylindrical_component_with_pixel_mapping)

    n_cylinders = cylindrical_geometry.cylinders.size / 3
    assert n_cylinders == pixel_options.get_pixel_mapping_table_size()
    assert (
        pixel_options.get_id_at_index(0) == pixel_mapping_with_single_pixel.pixel_ids[0]
    )


def test_GIVEN_pixel_grid_information_WHEN_creating_pixel_grid_THEN_calling_generate_pixel_data_returns_grid_that_matches_user_input(
    qtbot, template, pixel_options
):

    systematic_button_press(qtbot, template, pixel_options.single_pixel_radio_button)

    pixel_grid = pixel_options.generate_pixel_data()

    assert pixel_grid.rows == 1
    assert pixel_grid.columns == 1
    assert pixel_grid.row_height == 0.5
    assert pixel_grid.col_width == 0.5
    assert pixel_grid.first_id == 0
    assert pixel_grid.initial_count_corner == INITIAL_COUNT_CORNER["Bottom Left"]
    assert pixel_grid.count_direction == COUNT_DIRECTION["Rows"]
