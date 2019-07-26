import os

import PySide2
import pytest
import pytestqt
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QDialog, QRadioButton, QMainWindow

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.geometry import OFFGeometryNoNexus
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.validators import FieldType

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


def show_window_and_wait_for_interaction(
    qtbot: pytestqt.qtbot.QtBot, template: PySide2.QtWidgets.QDialog
):
    """
    Helper method that allows you to examine a window during testing. Just here for convenience.
    :param qtbot: The qtbot testing tool.
    :param template: The window/widget to be opened.
    """
    template.show()
    qtbot.stopForInteraction()


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


def enter_component_name(
    qtbot: pytestqt.qtbot.QtBot, dialog: AddComponentDialog, component_name: str
):
    """
    Mimics the user entering a component name in the Add Component dialog. Clicks on the text field and enters a given
    name.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog object.
    :param component_name: The desired component name.
    """
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, component_name)


def enter_file_path(
    qtbot: pytestqt.qtbot.QtBot, dialog: AddComponentDialog, file_path: str
):
    """
    Mimics the user entering a file path. Clicks on the text field and enters a given file path. Also sets the
    `geometry_file_name` attribute of the AddComponentDialog and this is usually only altered by opening a FileDialog.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog object.
    :param file_path: The desired file path.
    """
    qtbot.mouseClick(dialog.fileLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.fileLineEdit, file_path)
    dialog.cad_file_name = file_path


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


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    systematic_radio_button_press(qtbot, dialog.noShapeRadioButton)

    assert not dialog.shapeOptionsBox.isVisible()


def test_UI_GIVEN_nothing_WHEN_changing_component_geometry_type_THEN_add_component_button_is_always_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    all_geometry_buttons = [
        dialog.noShapeRadioButton,
        dialog.meshRadioButton,
        dialog.CylinderRadioButton,
    ]

    for geometry_button in all_geometry_buttons:
        systematic_radio_button_press(qtbot, geometry_button)
        assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the relevant fields start as invisible
    assert not dialog.shapeOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the cylinder geometry button
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)
    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()


def test_UI_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the relevant fields start as invisible
    assert not dialog.shapeOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the mesh geometry button
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_nothing_WHEN_choosing_geometry_with_units_THEN_default_units_are_metres(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    units_geometries = [dialog.meshRadioButton, dialog.CylinderRadioButton]

    for geometry_button in units_geometries:
        systematic_radio_button_press(qtbot, geometry_button)
        show_and_close_window(qtbot, template)
        assert dialog.unitsLineEdit.isVisible()
        assert dialog.unitsLineEdit.text() == "m"


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

        systematic_radio_button_press(qtbot, geometry_button)
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

        systematic_radio_button_press(qtbot, geometry_button)
        show_and_close_window(qtbot, template)

        for index in no_pixel_options_class_indices:

            # Manually set the pixel options to visible
            dialog.pixelOptionsBox.setVisible(True)
            dialog.shapeOptionsBox.setVisible(True)
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
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_remains_open(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    show_and_close_window(qtbot, template)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window won't close because the button is disabled
    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_closes(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_geometry_THEN_add_component_window_closes(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    # Mimic the user entering valid units
    enter_units(qtbot, dialog, VALID_UNITS)

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
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering valid units
    enter_units(qtbot, dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

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
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no geometry component is
    # there
    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # No file name was given so we expect the file input box background to be red
    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user entering a bad file path
    enter_file_path(qtbot, dialog, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(qtbot, dialog, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_white_background(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    # The file input box should now have a white background
    assert dialog.fileLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    show_and_close_window(qtbot, template)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(qtbot, dialog, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(qtbot, dialog, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user clearing the unit input box
    enter_units(qtbot, dialog, "")

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_white_background(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the replacing the default value with "km"
    enter_units(qtbot, dialog, VALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    # Mimic the user giving valid units
    enter_units(qtbot, dialog, VALID_UNITS)

    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    # Mimic the user clearing the units box
    enter_units(qtbot, dialog, "")

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_mesh_geometry_selected_THEN_relevant_fields_are_visible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_mesh_geometry_selected_THEN_irrelevant_fields_are_invisible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    assert not dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_relevant_fields_are_visible(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    show_and_close_window(qtbot, template)

    assert dialog.shapeOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_irrelevant_fields_are_invisible(
    qtbot
):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    assert not dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_default_values_are_correct(qtbot):

    dialog, template = create_add_component_template(qtbot)

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)
    show_and_close_window(qtbot, template)

    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.cylinderHeightLineEdit.value() == 1.0
    assert dialog.cylinderRadiusLineEdit.value() == 1.0
    assert dialog.cylinderXLineEdit.value() == 0.0
    assert dialog.cylinderYLineEdit.value() == 0.0
    assert dialog.cylinderZLineEdit.value() == 1.0


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_is_shown(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)
    qtbot.mouseClick(dialog.addFieldPushButton, Qt.LeftButton)
    field = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.edit_dialog.isEnabled()


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_table_is_shown(
    qtbot
):
    dialog, template = create_add_component_template(qtbot)
    qtbot.mouseClick(dialog.addFieldPushButton, Qt.LeftButton)
    field = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.table_view.isEnabled()


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
