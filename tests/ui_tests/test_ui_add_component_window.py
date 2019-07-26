import os
import sys
from typing import List

import PySide2
import pytest
import pytestqt
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QDialog, QAbstractButton, QLineEdit
from PySide2.QtWidgets import QRadioButton, QMainWindow
from mock import patch, mock_open, Mock
from pytestqt.qtbot import QtBot

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.geometry import OFFGeometryNoNexus
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.validators import FieldType

MISMATCHING_PIXEL_GRID_VALUES = [("0", "5.3"), ("1", "")]

WRONG_EXTENSION_FILE_PATH = os.path.join(os.getcwd(), "requirements.txt")
NONEXISTENT_FILE_PATH = "doesntexist.off"
VALID_CUBE_MESH_FILE_PATH = os.path.join(os.getcwd(), "tests", "cube.off")
VALID_OCTA_MESH_FILE_PATH = os.path.join(os.getcwd(), "tests", "octa.off")

nexus_wrapper_count = 0
RED_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #FFFFFF }"
UNIQUE_COMPONENT_NAME = "AUniqueName"
NONUNIQUE_COMPONENT_NAME = "sample"
VALID_UNITS = "km"
INVALID_UNITS = "abc"

RUNNING_ON_WINDOWS = sys.platform.startswith("win")

instrument = Instrument(NexusWrapper("pixels"))
component = ComponentTreeModel(instrument)
add_component_dialog = AddComponentDialog(instrument, component)
ALL_COMPONENT_TYPES = [
    (comp_type, i)
    for i, comp_type in enumerate(
        list(add_component_dialog.nx_component_classes.keys())
    )
][::-1]
PIXEL_OPTIONS = [
    comp_with_index
    for comp_with_index in ALL_COMPONENT_TYPES
    if comp_with_index[0] in component_type.PIXEL_COMPONENT_TYPES
]
NO_PIXEL_OPTIONS = [
    comp_with_index
    for comp_with_index in ALL_COMPONENT_TYPES
    if comp_with_index[0] not in component_type.PIXEL_COMPONENT_TYPES
]
SHAPE_TYPE_BUTTONS = ["No Shape", "Mesh", "Cylinder"]

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

VALID_OCTA_OFF_FILE = (
    "OFF\n"
    "#\n"
    "#  octa.off\n"
    "#  An octahedron.\n"
    "#\n"
    "6  8  12\n"
    "  0.0  0.0  1.0\n"
    "  1.0  0.0  0.0\n"
    "  0.0  1.0  0.0\n"
    " -1.0  0.0  0.0\n"
    "  0.0 -1.0  0.0\n"
    "  0.0  0.0 -1.0\n"
    "3  1 0 4  0.7 0 0\n"
    "3  4 0 3  0.7 0 0\n"
    "3  3 0 2  0.7 0 0\n"
    "3  2 0 1  0.7 0 0 \n"
    "3  1 5 2  0.7 0 0 \n"
    "3  2 5 3  0.7 0 0\n"
    "3  3 5 4  0.7 0 0\n"
    "3  4 5 1  0.7 0 0\n"
)


def get_expected_number_of_faces(off_file):
    """
    Finds the expected number of faces in an OFF file. Used to check this matches the number of items in a pixel
    mapping list.
    :param off_file: The OFF file.
    :return: The number of faces in the OFF file.
    """
    for line in off_file.split("\n")[1:]:
        if line[0] != "#":
            return int(line.split()[1])


CORRECT_CUBE_FACES = get_expected_number_of_faces(VALID_CUBE_OFF_FILE)
CORRECT_OCTA_FACES = get_expected_number_of_faces(VALID_OCTA_OFF_FILE)


@pytest.fixture(scope="function")
def template(qtbot):
    template = QDialog()
    return template


@pytest.fixture(scope="function")
def dialog(qtbot, template):
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)
    return dialog


def show_and_close_window(
    qtbot: pytestqt.qtbot.QtBot, template: PySide2.QtWidgets.QDialog
):
    """
    Function for displaying and then closing a window/widget. This appears to be necessary in order to make sure
    some interactions with the UI are recognised. Otherwise the UI can behave as though no clicks/button presses/etc
    actually took place which then causes tests to fail even though they ought to pass in theory.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget to be opened.
    """
    template.show()
    qtbot.waitForWindowShown(template)


def create_add_component_template(qtbot: pytestqt.qtbot.QtBot):
    """
    Creates a template Add Component Dialog and sets this up for testing.
    :param qtbot: The qtbot testing tool.
    :return: The AddComponentDialog object and the template that contains it.
    """
    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)
    return dialog, template


def create_add_component_dialog():
    """
    Creates an AddComponentDialog object for use in a testing template.
    :return: An instance of an AddComponentDialog object.
    """
    global nexus_wrapper_count
    nexus_name = "test" + str(nexus_wrapper_count)
    instrument = Instrument(NexusWrapper(nexus_name))
    component = ComponentTreeModel(instrument)
    nexus_wrapper_count += 1
    return AddComponentDialog(instrument, component)


def systematic_radio_button_press(qtbot: pytestqt.qtbot.QtBot, button: QRadioButton):
    """
    Left clicks on a radio button after finding the position to click using a systematic search.
    :param qtbot: The qtbot testing tool.
    :param button: The button to press.
    """
    qtbot.mouseClick(
        button, Qt.LeftButton, pos=find_radio_button_press_position(button)
    )


def find_radio_button_press_position(button: QRadioButton):
    """
    Systematic way of making sure a button press works. Goes through every point in the widget until it finds one that
    returns True for the `hitButton` method.
    :param button: The radio button to click.
    :return: A QPoint indicating where the button must be clicked in order for its event to be triggered.
    """
    size = button.size()

    for x in range(size.width()):
        for y in range(size.height()):
            click_point = QPoint(x, y)
            if button.hitButton(click_point):
                return click_point
    return None


def enter_units(qtbot: pytestqt.qtbot.QtBot, dialog: AddComponentDialog, units: str):
    """
    Mimics the user entering unit information. Clicks on the text field and removes the default value then enters a
    given string.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog object.
    :param units: The desired units input.
    """
    word_length = len(dialog.unitsLineEdit.text())
    for _ in range(word_length):
        qtbot.keyClick(dialog.unitsLineEdit, Qt.Key_Backspace)

    if len(units) > 0:
        qtbot.keyClicks(dialog.unitsLineEdit, units)


@pytest.mark.skip(reason="This test causes seg faults at the moment.")
def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):

    template = QMainWindow()
    window = MainWindow(Instrument(NexusWrapper("test")))
    template.ui = window
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    show_and_close_window(qtbot, template)

    qtbot.mouseClick(
        window.component_tool_bar.widgetForAction(window.new_component_action),
        Qt.LeftButton,
    )

    assert window.add_component_window.isVisible()

    window.add_component_window.close()


def test_UI_GIVEN_no_shape_WHEN_selecting_shape_type_THEN_shape_options_are_hidden(
    qtbot, template, dialog
):
    systematic_button_press(qtbot, template, dialog.noShapeRadioButton)
    assert not dialog.shapeOptionsBox.isVisible()


@pytest.mark.parametrize("shape_button_name", SHAPE_TYPE_BUTTONS)
def test_UI_GIVEN_nothing_WHEN_changing_component_shape_type_THEN_add_component_button_is_always_disabled(
    qtbot, template, dialog, shape_button_name
):
    systematic_button_press(
        qtbot, template, get_shape_type_button(dialog, shape_button_name)
    )
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nothong_WHEN_selecting_cylinder_type_THEN_relevant_fields_are_shown(
    qtbot, template, dialog
):
    # Click on the cylinder shape button
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    # Check that this has caused the relevant fields to become visible
    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()

    # Check that the file input isn't visible as this is only available for the mesh
    assert not dialog.geometryFileBox.isVisible()
    # Check that the pixel grid options aren't visible as this is only available for certain NXclasses
    assert not dialog.pixelGridBox.isVisible()


def test_UI_GIVEN_nothing_WHEN_selecting_mesh_shape_THEN_relevant_fields_are_shown(
    qtbot, template, dialog
):
    # Click on the mesh shape button
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Check that this has caused the relevant fields to become visible
    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()

    # Check that the cylinder options aren't visible
    assert not dialog.cylinderOptionsBox.isVisible()
    # Check that the pixel grid options aren't visible as this is only available for certain NXclasses
    assert not dialog.pixelGridBox.isVisible()


@pytest.mark.parametrize("shape_with_units", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_nothing_WHEN_selecting_shape_with_units_THEN_default_units_are_metres(
    qtbot, template, dialog, shape_with_units
):
    # Click on the button of a shape type with units
    systematic_button_press(
        qtbot, template, get_shape_type_button(dialog, shape_with_units)
    )

    # Check that the units line edit is visible and has metres by default
    assert dialog.unitsLineEdit.isVisible()
    assert dialog.unitsLineEdit.text() == "m"


@pytest.mark.parametrize("pixel_class, pixel_index", PIXEL_OPTIONS)
@pytest.mark.parametrize("any_component_type", ALL_COMPONENT_TYPES)
@pytest.mark.parametrize("pixel_shape_name", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_class_and_shape_with_pixel_fields_WHEN_adding_component_THEN_pixel_options_go_from_invisible_to_visible(
    qtbot,
    template,
    dialog,
    pixel_class,
    pixel_index,
    any_component_type,
    pixel_shape_name,
):
    # Change the pixel options to visible by selecting a cylinder/mesh shape and a NXclass with pixel fields
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(dialog, pixel_shape_name),
        dialog,
        template,
        pixel_index,
    )
    # Check that this has caused the pixel options to become visible
    assert dialog.pixelOptionsBox.isVisible()


@pytest.mark.parametrize("any_component_type", ALL_COMPONENT_TYPES)
def test_UI_GIVEN_any_nxclass_WHEN_adding_component_with_no_shape_THEN_pixel_options_go_from_visible_to_invisible(
    qtbot, template, dialog, any_component_type
):
    # Change the pixel options to visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Change the pixel options to invisible
    make_pixel_options_disappear(qtbot, dialog, template, any_component_type[1])
    assert not dialog.pixelOptionsBox.isVisible()


@pytest.mark.parametrize("no_pixel_options", NO_PIXEL_OPTIONS)
@pytest.mark.parametrize("pixel_options", PIXEL_OPTIONS)
@pytest.mark.parametrize("shape_name", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_for_component_with_mesh_or_cylinder_shape_THEN_pixel_options_becomes_invisible(
    qtbot, template, dialog, no_pixel_options, pixel_options, shape_name
):
    # Make the pixel options become visible
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(dialog, shape_name),
        dialog,
        template,
        pixel_options[1],
    )
    assert dialog.pixelOptionsBox.isVisible()

    # Change nxclass to one without pixel fields and check that the pixel options have become invisible again
    dialog.componentTypeComboBox.setCurrentIndex(no_pixel_options[1])
    assert not dialog.pixelOptionsBox.isVisible()


@pytest.mark.parametrize("shape_name", SHAPE_TYPE_BUTTONS[1:])
@pytest.mark.parametrize("pixel_options", PIXEL_OPTIONS)
def test_UI_GIVEN_component_with_pixel_fields_WHEN_choosing_pixel_layout_THEN_single_pixel_is_selected_and_visible_by_default(
    qtbot, template, dialog, shape_name, pixel_options
):
    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Check that the single grid button is checked and the pixel grid option is visible by default
    assert dialog.singlePixelRadioButton.isChecked()
    assert dialog.pixelGridBox.isVisible()

    # Check that the pixel mapping items are not visible
    assert not dialog.pixelMappingListWidget.isVisible()
    assert not dialog.pixelMappingLabel.isVisible()


def test_UI_GIVEN_user_selects_entire_shape_WHEN_choosing_pixel_layout_THEN_pixel_grid_box_becomes_invisible(
    qtbot, template, dialog
):
    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, dialog.entireShapeRadioButton)

    # Check that the pixel mapping items are visible
    assert dialog.pixelMappingLabel.isVisible()
    assert dialog.pixelMappingListWidget.isVisible()

    # Check that the pixel grid box is not visible
    assert not dialog.pixelGridBox.isVisible()


def test_UI_GIVEN_user_selects_no_pixels_THEN_pixel_grid_and_pixel_mapping_options_become_invisible(
    qtbot, template, dialog
):

    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Press the entire shape button under pixel layout
    systematic_button_press(qtbot, template, dialog.noPixelsButton)

    # Check that the pixel mapping items are visible
    assert not dialog.pixelMappingLabel.isVisible()
    assert not dialog.pixelMappingListWidget.isVisible()

    # Check that the pixel grid box is not visible
    assert not dialog.pixelGridBox.isVisible()


def test_UI_GIVEN_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_is_populated(
    qtbot, template, dialog
):
    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Press the entire shape button
    systematic_button_press(qtbot, template, dialog.entireShapeRadioButton)

    # Provide a valid file path and mesh file
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Check that the number of items in the pixel mapping list matches the number of faces in the mesh file
    assert dialog.pixelMappingListWidget.count() == CORRECT_CUBE_FACES


def test_UI_GIVEN_same_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_remains_the_same(
    qtbot, template, dialog
):

    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Press the entire shape radio button
    systematic_button_press(qtbot, template, dialog.entireShapeRadioButton)

    # Provide a valid file path and mesh file
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Mock the method that is used to create the pixel mapping list
    dialog.populate_pixel_mapping_list = Mock()

    # Provide the same file as before
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Check that the method for populating the pixel mapping list was not called
    dialog.populate_pixel_mapping_list.assert_not_called()

    # Check that the list still has the expected number of items
    assert dialog.pixelMappingListWidget.count() == CORRECT_CUBE_FACES


def test_UI_GIVEN_different_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_changes(
    qtbot, template, dialog
):
    # Make the pixel options visible
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Press the entire shape button
    systematic_button_press(qtbot, template, dialog.entireShapeRadioButton)

    # Provide a path and file for a cube mesh
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Provide a path and file for an octahedron mesh
    enter_file_path(
        qtbot, dialog, template, VALID_OCTA_MESH_FILE_PATH, VALID_OCTA_OFF_FILE
    )

    # Check that the pixel mapping list has updated
    assert dialog.pixelMappingListWidget.count() == CORRECT_OCTA_FACES


def test_UI_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot, template, dialog
):
    # Check that the background color of the ext field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot, template, dialog
):

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, template, dialog, NONUNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_shape_THEN_add_component_window_remains_open(
    qtbot, template, dialog
):

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, template, dialog, NONUNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window won't close because the button is disabled
    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_window_closes(
    qtbot, template, dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_shape_THEN_add_component_window_closes(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Mimic the user entering valid units
    enter_units(qtbot, dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_cylinder_shape_THEN_add_component_window_closes(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering valid units
    enter_units(qtbot, dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a no shape
    systematic_button_press(qtbot, template, dialog.noShapeRadioButton)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, template, dialog, NONUNIQUE_COMPONENT_NAME)

    # The Add Component button is disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # The Add Component button is disabled because no input was given
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no shape component is
    # there
    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # No file name was given so we expect the file input box background to be red
    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user entering a bad file path
    enter_file_path(qtbot, dialog, template, NONEXISTENT_FILE_PATH, "OFF")

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(qtbot, dialog, template, WRONG_EXTENSION_FILE_PATH, "OFF")

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_white_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # The file input box should now have a white background
    assert dialog.fileLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(qtbot, dialog, template, NONEXISTENT_FILE_PATH, VALID_CUBE_OFF_FILE)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(
        qtbot, dialog, template, WRONG_EXTENSION_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user clearing the unit input box
    enter_units(qtbot, dialog, "")

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_white_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the replacing the default value with "km"
    enter_units(qtbot, dialog, VALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Mimic the user giving valid units
    enter_units(qtbot, dialog, VALID_UNITS)

    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Mimic the user clearing the units box
    enter_units(qtbot, dialog, "")

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonunique_name_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user giving an invalid component name
    enter_component_name(qtbot, template, dialog, NONUNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_cylinder_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    # Mimic the user giving valid component name
    enter_component_name(qtbot, template, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_name_WHEN_adding_component_with_cylinder_shape_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    # Mimic the user giving valid units input
    enter_units(qtbot, dialog, VALID_UNITS)

    # Mimic the user giving valid component name
    enter_component_name(qtbot, template, dialog, NONUNIQUE_COMPONENT_NAME)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_mesh_shape_selected_THEN_relevant_fields_are_visible(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()

    assert not dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_shape_selected_THEN_relevant_fields_are_visible(
    qtbot, template, dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()

    assert not dialog.geometryFileBox.isVisible()


@pytest.mark.parametrize("comp_type_without_pixels", NO_PIXEL_OPTIONS)
def test_UI_GIVEN_file_chosen_WHEN_pixel_mapping_options_not_visible_THEN_pixel_mapping_list_remains_empty(
    qtbot, template, dialog, comp_type_without_pixels
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, dialog.meshRadioButton)

    # Mimic the user selecting a component type that doesn't have pixel fields
    dialog.componentTypeComboBox.setCurrentIndex(comp_type_without_pixels[1])

    # Mimic the user giving a valid mesh file
    enter_file_path(
        qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, VALID_CUBE_OFF_FILE
    )

    # Check that the pixel mapping list is still empty
    assert dialog.pixelMappingListWidget.count() == 0


def test_UI_GIVEN_nothing_WHEN_pixel_mapping_options_are_visible_THEN_options_have_expected_default_values(
    qtbot, template, dialog
):

    # Make the pixel options appear
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Check that the pixel-related fields start out with the expected default values
    assert dialog.rowLineEdit.text() == "1"
    assert dialog.columnsLineEdit.text() == "1"
    assert dialog.rowHeightLineEdit.text() == "1"
    assert dialog.columnsLineEdit.text() == "1"
    assert dialog.firstIDLineEdit.text() == "0"
    assert (
        dialog.startCountingComboBox.currentText()
        == list(dialog.initial_count_corner.keys())[0]
    )
    assert (
        dialog.countFirstComboBox.currentText()
        == list(dialog.count_direction.keys())[0]
    )


def test_UI_GIVEN_invalid_off_file_WHEN_creating_pixel_mapping_THEN_pixel_mapping_widget_isnt_populated(
    qtbot, template, dialog
):

    # Make the pixel options appear
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Choose the pixel mapping option
    systematic_button_press(qtbot, template, dialog.entireShapeRadioButton)

    # Give an invalid file
    enter_file_path(qtbot, dialog, template, VALID_CUBE_MESH_FILE_PATH, "hfhuihfiuhf")

    # Check that the number of items in the pixel mapping list is still zero
    assert dialog.pixelMappingListWidget.count() == 0


@pytest.mark.parametrize("row_count, row_height", MISMATCHING_PIXEL_GRID_VALUES)
def test_GIVEN_mismatching_row_values_WHEN_giving_pixel_grid_options_THEN_both_backgrounds_turn_red(
    qtbot, template, dialog, row_count, row_height
):

    # Make the pixel options appear
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Enter a value for row height
    qtbot.keyClick(dialog.rowHeightLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.rowHeightLineEdit, row_height)

    # Enter a value for row count
    qtbot.keyClick(dialog.rowLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.rowLineEdit, row_count)

    # Check that the background has turned red as a result of the values not matching
    assert dialog.rowLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET
    assert dialog.rowHeightLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


@pytest.mark.parametrize("column_count, column_width", MISMATCHING_PIXEL_GRID_VALUES)
def test_GIVEN_mismatching_column_values_WHEN_giving_pixel_grid_options_THEN_both_backgrounds_turn_red(
    qtbot, template, dialog, column_count, column_width
):

    # Make the pixel options appear
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Enter a value for column count
    qtbot.keyClick(dialog.columnsLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.columnsLineEdit, column_count)

    # Enter a value for column width
    qtbot.keyClick(dialog.columnWidthLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.columnWidthLineEdit, column_width)

    # Check that the background has become red as a result of the values not matching
    assert dialog.columnsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET
    assert dialog.columnWidthLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_GIVEN_acceptable_value_WHEN_giving_pixel_grid_options_THEN_row_count_background_turns_white(
    qtbot, template, dialog
):

    row_count = "2"
    row_height = "3.5"

    # Make the pixel options appear
    systematic_button_press(qtbot, template, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(PIXEL_OPTIONS[0][1])

    # Enter a value for row height
    qtbot.keyClick(dialog.rowHeightLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.rowHeightLineEdit, row_height)

    # Enter a value for row count
    qtbot.keyClick(dialog.rowLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.rowLineEdit, row_count)

    # Check that the background has turned white due to the values being valid
    assert dialog.rowLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_GIVEN_acceptable_value_WHEN_giving_pixel_grid_options_THEN_column_width_background_turns_white(
    qtbot, template, dialog
):

    column_count = "1"
    column_width = "0.1"

    # Enter a value for column count
    qtbot.keyClick(dialog.columnsLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.columnsLineEdit, column_count)

    # Enter a value for column width
    qtbot.keyClick(dialog.columnWidthLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.columnWidthLineEdit, column_width)

    # Check that the background has turned white due to the values being valid
    assert dialog.columnWidthLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_cylinder_shape_selected_WHEN_adding_component_THEN_default_values_are_correct(
    qtbot, template, dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, template, dialog.CylinderRadioButton)

    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.cylinderHeightLineEdit.value() == 1.0
    assert dialog.cylinderRadiusLineEdit.value() == 1.0
    assert dialog.cylinderXLineEdit.value() == 0.0
    assert dialog.cylinderYLineEdit.value() == 0.0
    assert dialog.cylinderZLineEdit.value() == 1.0


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_is_shown(
    qtbot, template, dialog
):
    qtbot.mouseClick(dialog.addFieldPushButton, Qt.LeftButton)
    field = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.edit_dialog.isEnabled()


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_table_is_shown(
    qtbot, template, dialog
):
    qtbot.mouseClick(dialog.addFieldPushButton, Qt.LeftButton)
    field = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.table_view.isEnabled()


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """
    Creates a QtBot at the end of all the tests and has it wait. This seems to be necessary in order to prevent
    the use of fixtures from causing a segmentation fault.
    """

    def make_another_qtest():
        bot = QtBot(request)
        bot.wait(1)

    request.addfinalizer(make_another_qtest)


def get_shape_type_button(dialog: AddComponentDialog, button_name: str):
    """
    Finds the shape type button that contains the given text.
    :param dialog: An instance of an AddComponentDialog.
    :param button_name: The name of the desired button.
    :return: The QRadioButton for the given shape type.
    """
    for child in dialog.shapeTypeBox.findChildren(PySide2.QtWidgets.QRadioButton):
        if child.text() == button_name:
            return child


def make_pixel_options_disappear(
    qtbot: pytestqt.qtbot.QtBot,
    dialog: AddComponentDialog,
    template: PySide2.QtWidgets.QDialog,
    component_index: int,
):
    """
    Create the conditions to allow the disappearance of the pixel options.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param component_index: The index of a component type.
    """
    systematic_button_press(qtbot, template, dialog.noShapeRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(component_index)
    show_and_close_window(qtbot, template)


def make_pixel_options_appear(
    qtbot: pytestqt.qtbot.QtBot,
    button: QRadioButton,
    dialog: AddComponentDialog,
    template: PySide2.QtWidgets.QDialog,
    pixel_options_index: int,
):
    """
    Create the conditions to allow the appearance of the pixel options.
    :param qtbot: The qtbot testing tool.
    :param button: The Mesh or Cylinder radio button.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param pixel_options_index: The index of a component type for the combo box that has pixel fields.
    """
    systematic_button_press(qtbot, template, button)
    dialog.componentTypeComboBox.setCurrentIndex(pixel_options_index)
    show_and_close_window(qtbot, template)


def show_window_and_wait_for_interaction(
    qtbot: pytestqt.qtbot.QtBot, template: PySide2.QtWidgets.QDialog
):
    """
    Helper method that allows you to examine a window during testing. Just here for convenience.
    Does nothing if the test is running on Windows because this is bad for Jenkins.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget to be opened.
    """
    if RUNNING_ON_WINDOWS:
        return
    template.show()
    qtbot.stopForInteraction()


def test_UI_GIVEN_component_name_and_description_WHEN_editing_component_THEN_correct_values_are_loaded_into_UI(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_name"))

    component_model = ComponentTreeModel(instrument)

    name = "test"
    nx_class = "NXmonitor"
    desc = "description"

    component = instrument.create_component(
        name=name, nx_class=nx_class, description=desc
    )

    dialog = AddComponentDialog(
        instrument, component_model, component_to_edit=component, parent=None
    )
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.nameLineEdit.text() == name
    assert dialog.descriptionPlainTextEdit.text() == desc
    assert dialog.componentTypeComboBox.currentText() == nx_class


def test_UI_GIVEN_component_with_no_shape_WHEN_editing_component_THEN_no_shape_radio_is_checked(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_no_shape"))
    component_model = ComponentTreeModel(instrument)

    component = instrument.create_component("test", "NXpinhole", "")

    dialog = AddComponentDialog(
        instrument, component_model, component_to_edit=component, parent=None
    )
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.noShapeRadioButton.isChecked()


def test_UI_GIVEN_component_with_cylinder_shape_WHEN_editing_component_THEN_cylinder_shape_radio_is_checked(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_cylinder"))
    component_model = ComponentTreeModel(instrument)

    component_name = "test"
    component = instrument.create_component(component_name, "NXpinhole", "")
    component.set_cylinder_shape(QVector3D(1, 1, 1), height=3, radius=4)

    dialog = AddComponentDialog(
        instrument, component_model, component_to_edit=component
    )
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.CylinderRadioButton.isChecked()
    assert dialog.cylinderOptionsBox.isEnabled()


def test_UI_GIVEN_component_with_off_shape_WHEN_editing_component_THEN_mesh_shape_radio_is_checked(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_off"))
    component_model = ComponentTreeModel(instrument)

    component_name = "test"

    component = instrument.create_component(component_name, "NXpinhole", "")
    component.set_off_shape(
        OFFGeometryNoNexus(
            [
                QVector3D(0.0, 0.0, 1.0),
                QVector3D(0.0, 1.0, 0.0),
                QVector3D(0.0, 0.0, 0.0),
            ],
            [[0, 1, 2]],
        ),
        units="m",
        filename=os.path.join(os.path.pardir, "cube.off"),
    )

    dialog = AddComponentDialog(
        instrument, component_model, component_to_edit=component
    )
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.meshRadioButton.isChecked()
    assert dialog.fileLineEdit.isEnabled()
    assert dialog.fileBrowseButton.isEnabled()


def test_UI_GIVEN_component_with_off_shape_WHEN_editing_component_THEN_mesh_data_is_in_line_edits(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_off_filepath"))
    component_model = ComponentTreeModel(instrument)

    component_name = "test"
    units = "m"
    filepath = os.path.join(os.path.pardir, "cube.off")

    component = instrument.create_component(component_name, "NXpinhole", "")
    component.set_off_shape(
        OFFGeometryNoNexus(
            [
                QVector3D(0.0, 0.0, 1.0),
                QVector3D(0.0, 1.0, 0.0),
                QVector3D(0.0, 0.0, 0.0),
            ],
            [[0, 1, 2]],
        ),
        units=units,
        filename=filepath,
    )

    dialog = AddComponentDialog(
        instrument, component_model, component_to_edit=component
    )
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.meshRadioButton.isChecked()
    assert dialog.fileLineEdit.isEnabled()
    assert dialog.unitsLineEdit.isEnabled()
    assert dialog.unitsLineEdit.text() == units

    assert dialog.fileBrowseButton.isEnabled()

    assert dialog.fileLineEdit.isEnabled()
    assert dialog.fileLineEdit.text() == filepath


def test_UI_GIVEN_field_widget_with_string_type_THEN_value_property_is_correct(qtbot):

    dialog, template = create_add_component_template(qtbot)

    qtbot.mouseClick(dialog.addFieldPushButton, Qt.LeftButton)
    field = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))

    field.field_type_combo.setCurrentText(FieldType.scalar_dataset.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    field.value_type_combo.setCurrentText("String")
    field.value_type_combo.currentTextChanged.emit(field.value_type_combo.currentText)

    field_name = "testfield"
    field_value = "testvalue"

    field.field_name_edit.setText(field_name)
    field.value_line_edit.setText(field_value)

    import h5py

    assert field.dtype == h5py.special_dtype(vlen=str)

    assert field.name == field_name
    assert field.value[...] == field_value


def get_pixel_grid_line_edits(dialog: AddComponentDialog) -> List[QLineEdit]:
    """
    Returns a list of the line edits in the Pixel Grid box. These are used to input the row/column size and count.
    :param dialog: An instance of an AddComponentDialog.
    :return: A list of the line edits in the Pixel Grid box.
    """
    return dialog.pixelGridBox.findChildren(QLineEdit)


def enter_file_path(
    qtbot: pytestqt.qtbot.QtBot,
    dialog: AddComponentDialog,
    template: PySide2.QtWidgets.QDialog,
    file_path: str,
    file_contents: str,
):
    """
    Mimics the user entering a file path. Mimics a button click and patches the methods that deal with loading a
    geometry file.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param file_path: The desired file path.
    :param file_contents: The file contents that are returned by the open mock.
    """
    with patch(
        "nexus_constructor.add_component_window.file_dialog", return_value=file_path
    ):
        with patch("builtins.open", mock_open(read_data=file_contents)):
            systematic_button_press(qtbot, template, dialog.fileBrowseButton)


def enter_component_name(
    qtbot: pytestqt.qtbot.QtBot,
    template: PySide2.QtWidgets.QDialog,
    dialog: AddComponentDialog,
    component_name: str,
):
    """
    Mimics the user entering a component name in the Add Component dialog. Clicks on the text field and enters a given
    name.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param component_name: The desired component name.
    """
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, component_name)
    show_and_close_window(qtbot, template)


def systematic_button_press(
    qtbot: pytestqt.qtbot.QtBot,
    template: PySide2.QtWidgets.QDialog,
    button: QAbstractButton,
):
    """
    Left clicks on a button after finding the position to click using a systematic search.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget that holds an AddComponentDialog.
    :param button: The button to press.
    """
    point = find_button_press_position(button)

    if point is not None:
        qtbot.mouseClick(button, Qt.LeftButton, pos=point)
    else:
        qtbot.mouseClick(button, Qt.LeftButton)

    show_and_close_window(qtbot, template)


def find_button_press_position(button: QAbstractButton):
    """
    Systematic way of making sure a button press works. Goes through every point in the widget until it finds one that
    returns True for the `hitButton` method.
    :param button: The radio button to click.
    :return: A QPoint indicating where the button must be clicked in order for its event to be triggered.
    """
    width = button.geometry().width()
    height = button.geometry().height()

    for x in range(1, width):
        for y in range(1, height):
            click_point = QPoint(x, y)
            if button.hitButton(click_point):
                return click_point
    return None
