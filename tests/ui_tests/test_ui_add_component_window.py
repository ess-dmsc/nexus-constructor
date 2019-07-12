import os
import sys

import PySide2
import pytest
import pytestqt
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

# Workaround - even when skipping jenkins is not happy importing AddComponentDialog due to a missing lib
RUNNING_ON_WINDOWS = sys.platform.startswith("win")
WRONG_EXTENSION_FILE_PATH = os.path.join(os.getcwd(), "tests", "UITests.md")
NONEXISTENT_FILE_PATH = "doesntexist.off"
VALID_MESH_FILE_PATH = os.path.join(os.getcwd(), "tests", "cube.off")

nexus_wrapper_count = 0
RED_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #FFFFFF }"
UNIQUE_COMPONENT_NAME = "AUniqueName"
NONUNIQUE_COMPONENT_NAME = "sample"
VALID_UNITS = "km"
INVALID_UNITS = "abc"


@pytest.mark.skip(
    reason="Clicking with QActions/QIcons doesn't seem to be possible. This test causes seg faults at the moment."
)
def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    qtbot.addWidget(template)

    # Using trigger rather than clicking on the menu
    # window.new_component_action.trigger()
    # assert window.add_component_window.isVisible()
    #
    # window.add_component_window.close()


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_given_nothing_WHEN_changing_component_geometry_type_THEN_add_component_button_is_always_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    all_geometry_buttons = [
        dialog.noGeometryRadioButton,
        dialog.meshRadioButton,
        dialog.CylinderRadioButton,
    ]

    for geometry_button in all_geometry_buttons:
        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the cylinder geometry button
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)
    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the mesh geometry button
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_class_with_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_visible(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    classes = list(dialog.nx_component_classes.keys())
    pixel_options_class_indices = []

    for i, nx_class in enumerate(classes):
        if nx_class in component_type.PIXEL_COMPONENT_TYPES:
            pixel_options_class_indices.append(i)

    pixel_geometry_buttons = [dialog.meshRadioButton, dialog.CylinderRadioButton]

    for geometry_button in pixel_geometry_buttons:

        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        show_and_close_window(qtbot, template)

        for index in pixel_options_class_indices:

            # Change the pixel options to invisible manually
            dialog.pixelOptionsBox.setVisible(False)
            assert not dialog.pixelOptionsBox.isVisible()

            dialog.componentTypeComboBox.setCurrentIndex(index)
            show_and_close_window(qtbot, template)

            assert dialog.pixelOptionsBox.isVisible()


def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_invisible(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    classes = list(dialog.nx_component_classes.keys())
    no_pixel_options_class_indices = []

    for i, nx_class in enumerate(classes):
        if nx_class not in component_type.PIXEL_COMPONENT_TYPES:
            no_pixel_options_class_indices.append(i)

    # Put the first index at the end. Otherwise changing from 0 to 0 doesn't trigger the indexChanged signal.
    no_pixel_options_class_indices.append(no_pixel_options_class_indices.pop(0))

    all_geometry_buttons = [dialog.meshRadioButton, dialog.CylinderRadioButton]

    for geometry_button in all_geometry_buttons:

        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        show_and_close_window(qtbot, template)

        for index in no_pixel_options_class_indices:

            # Manually set the pixel options to visible
            dialog.pixelOptionsBox.setVisible(True)
            dialog.geometryOptionsBox.setVisible(True)
            assert dialog.pixelOptionsBox.isVisible()

            # Change the index and check that the pixel options have become invisible again
            dialog.componentTypeComboBox.setCurrentIndex(index)
            assert not dialog.pixelOptionsBox.isVisible()


def test_UI_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the background color of the ext field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(dialog, qtbot, NONUNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_remains_open(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    show_and_close_window(qtbot, template)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(dialog, qtbot, NONUNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window won't close because the button is disabled
    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_closes(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user entering a unique name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_geometry_THEN_add_component_window_closes(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    # Mimic the user entering valid units
    enter_units(dialog, qtbot, VALID_UNITS)

    show_and_close_window(qtbot, template)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_cylinder_geometry_THEN_add_component_window_closes(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering valid units
    enter_units(dialog, qtbot, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(dialog, qtbot, NONUNIQUE_COMPONENT_NAME)

    # The Add Component button is disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # The Add Component button is disabled because no input was given
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_enabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user entering a unique name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no geometry component is
    # there
    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    # No file name was given so we expect the file input box background to be red
    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user entering a bad file path
    enter_file_path(dialog, qtbot, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(dialog, qtbot, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_white_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    # The file input box should now have a white background
    assert dialog.fileLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    # Mimic the user entering a unique name in the text field
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    show_and_close_window(qtbot, template)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(dialog, qtbot, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(dialog, qtbot, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user clearing the unit input box (it will contain only 'm' by default)
    enter_units(dialog, qtbot, "")

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving invalid units input
    enter_units(dialog, qtbot, INVALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_white_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the replacing the default value with "km"
    enter_units(dialog, qtbot, VALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    # Mimic the user giving valid units
    enter_units(dialog, qtbot, VALID_UNITS)

    assert dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    # Mimic the user clearing the units box
    qtbot.keyClick(dialog.unitsLineEdit, Qt.Key_Backspace)

    assert not dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    # Mimic the user giving a valid component name
    enter_component_name(dialog, qtbot, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(dialog, qtbot, VALID_MESH_FILE_PATH)

    # Mimic the user giving invalid units input
    qtbot.keyClicks(dialog.unitsLineEdit, "111")

    assert not dialog.buttonBox.isEnabled()


@pytest.mark.skipif(RUNNING_ON_WINDOWS, reason="Fails on Windows.")
def test_UI_GIVEN_mesh_geometry_selected_THEN_relevant_fields_are_visible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_mesh_geometry_selected_THEN_irrelevant_fields_are_invisible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    assert not dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_relevant_fields_are_visible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a cylinder geometry
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    show_and_close_window(qtbot, template)

    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_irrelevant_fields_are_invisible(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a cylinder geometry
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    assert not dialog.geometryFileBox.isVisible()


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


def enter_component_name(
    dialog: AddComponentDialog, qtbot: pytestqt.qtbot.QtBot, component_name: str
):
    """
    Mimics the user entering a component name in the Add Component dialog. Clicks on the text field and enters a given
    name.
    :param dialog: An instance of an AddComponentDialog object.
    :param qtbot: The qtbot testing tool.
    :param component_name: The desired component name.
    """
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, component_name)


def enter_file_path(
    dialog: AddComponentDialog, qtbot: pytestqt.qtbot.QtBot, file_path: str
):
    """
    Mimics the user entering a file path. Clicks on the text field and enters a given file path. Also sets the
    `geometry_file_name` attribute of the AddComponentDialog and this is usually only altered by opening a FileDialog.
    :param dialog: An instance of an AddComponentDialog object.
    :param qtbot: The qtbost testing tool.
    :param file_path: The desired file path.
    """
    qtbot.mouseClick(dialog.fileLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.fileLineEdit, file_path)
    dialog.geometry_file_name = file_path


def enter_units(dialog: AddComponentDialog, qtbot: pytestqt.qtbot.QtBot, units: str):
    """
    Mimics the user entering unit information. Clicks on the text field and removes the default value then enters a
    given string.
    :param dialog: An instance of an AddComponentDialog object.
    :param qtbot: The qtbot testing tool.
    :param units: The desired units input.
    """
    qtbot.keyClick(dialog.unitsLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(dialog.unitsLineEdit, units)
