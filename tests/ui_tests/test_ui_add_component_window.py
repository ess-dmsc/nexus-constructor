import os

import PySide2
import pytest
import pytestqt
from PySide2.QtCore import Qt, QPoint
from PySide2.QtWidgets import QDialog, QRadioButton, QMainWindow
from pytestqt.qtbot import QtBot

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

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
GEOMETRY_BUTTONS = ["No Geometry", "Mesh", "Cylinder"]


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
    qtbot, template, dialog
):

    systematic_radio_button_press(qtbot, dialog.noGeometryRadioButton)
    assert not dialog.geometryOptionsBox.isVisible()


@pytest.mark.parametrize("geometry_button_name", GEOMETRY_BUTTONS)
def test_UI_GIVEN_nothing_WHEN_changing_component_geometry_type_THEN_add_component_button_is_always_disabled(
    qtbot, template, dialog, geometry_button_name
):

    systematic_radio_button_press(
        qtbot, get_geometry_button(dialog, geometry_button_name)
    )
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot, template, dialog
):

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the cylinder geometry button
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)
    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()


def test_UI_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot, template, dialog
):

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the mesh geometry button
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


@pytest.mark.parametrize("geometry_with_units", GEOMETRY_BUTTONS[1:])
def test_UI_GIVEN_nothing_WHEN_choosing_geometry_with_units_THEN_default_units_are_metres(
    qtbot, template, dialog, geometry_with_units
):

    systematic_radio_button_press(
        qtbot, get_geometry_button(dialog, geometry_with_units)
    )
    show_and_close_window(qtbot, template)
    assert dialog.unitsLineEdit.isVisible()
    assert dialog.unitsLineEdit.text() == "m"


@pytest.mark.parametrize("pixel_options", PIXEL_OPTIONS)
def test_UI_GIVEN_class_with_pixel_fields_WHEN_selecting_nxclass_for_component_with_mesh_geometry_THEN_pixel_options_becomes_visible(
    qtbot, template, dialog, pixel_options
):

    systematic_radio_button_press(qtbot, dialog.meshRadioButton)
    show_and_close_window(qtbot, template)

    # Change the pixel options to invisible manually
    dialog.pixelOptionsBox.setVisible(False)
    assert not dialog.pixelOptionsBox.isVisible()

    dialog.componentTypeComboBox.setCurrentIndex(pixel_options[1])

    show_and_close_window(qtbot, template)

    assert dialog.pixelOptionsBox.isVisible()


@pytest.mark.parametrize("no_pixel_options", NO_PIXEL_OPTIONS)
@pytest.mark.parametrize("pixel_options", PIXEL_OPTIONS)
def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_for_component_with_mesh_geometry_THEN_pixel_options_becomes_invisible(
    qtbot, template, dialog, no_pixel_options, pixel_options
):

    systematic_radio_button_press(qtbot, dialog.meshRadioButton)
    show_and_close_window(qtbot, template)

    # Make the pixel options become visible
    make_pixel_options_appear(qtbot, dialog, template, pixel_options[1])
    assert dialog.pixelOptionsBox.isVisible()

    # Change the index and check that the pixel options have become invisible again
    dialog.componentTypeComboBox.setCurrentIndex(no_pixel_options[1])
    assert not dialog.pixelOptionsBox.isVisible()


# @pytest.mark.skipif(os.name == "nt", reason="")
@pytest.mark.parametrize("component_type", ALL_COMPONENT_TYPES)
@pytest.mark.parametrize("pixel_options", PIXEL_OPTIONS)
@pytest.mark.parametrize("no_pixel_geometry", ["No Geometry", "Cylinder"])
def test_UI_GIVEN_any_class_WHEN_selecting_any_nxclass_for_component_that_does_not_have_mesh_geometry_THEN_pixel_options_are_never_visible(
    qtbot, template, dialog, component_type, pixel_options, no_pixel_geometry
):
    make_pixel_options_appear(qtbot, dialog, template, pixel_options[1])
    assert dialog.pixelOptionsBox.isVisible()

    no_pixel_button = get_geometry_button(dialog, no_pixel_geometry)

    systematic_radio_button_press(qtbot, no_pixel_button)

    show_and_close_window(qtbot, template)

    dialog.componentTypeComboBox.setCurrentIndex(component_type[1])
    show_and_close_window(qtbot, template)
    assert (
        dialog.componentTypeComboBox.currentText()
        == list(dialog.nx_component_classes.keys())[component_type[1]]
    )

    assert not dialog.pixelOptionsBox.isVisible()


def test_UI_GIVEN_component_with_pixel_fields_WHEN_choosing_pixel_layout_THEN_repeatable_grid_is_selected_and_visible_by_default(
    qtbot, template, dialog
):
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)


def test_UI_GIVEN_user_selects_face_mapped_mesh_WHEN_choosing_pixel_layout_THEN_pixel_grid_box_becomes_invisible(
    qtbot
):
    pass


def test_UI_GIVEN_user_selects_repeatable_grid_WHEN_choosing_pixel_layout_THEN_pixel_grid_box_becomes_visible(
    qtbot
):
    pass


def test_UI_GIVEN_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_is_populated(
    qtbot
):
    pass


def test_UI_GIVEN_same_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_remains_the_same(
    qtbot
):
    pass


def test_UI_GIVEN_different_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_changes(
    qtbot
):
    pass


def test_UI_GIVEN_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_length_of_list_matches_number_of_faces_in_mesh(
    qtbot
):
    pass


def test_UI_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot, template, dialog
):

    # Check that the background color of the ext field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot, template, dialog
):

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_remains_open(
    qtbot, template, dialog
):

    show_and_close_window(qtbot, template)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window won't close because the button is disabled
    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_window_closes(
    qtbot, template, dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_geometry_THEN_add_component_window_closes(
    qtbot, template, dialog
):

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
    qtbot, template, dialog
):
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
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(qtbot, dialog, NONUNIQUE_COMPONENT_NAME)

    # The Add Component button is disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # The Add Component button is disabled because no input was given
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_geometry_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no geometry component is
    # there
    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # No file name was given so we expect the file input box background to be red
    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user entering a bad file path
    enter_file_path(qtbot, dialog, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(qtbot, dialog, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.fileLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_file_path_box_has_white_background(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    # The file input box should now have a white background
    assert dialog.fileLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):
    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    show_and_close_window(qtbot, template)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(qtbot, dialog, NONEXISTENT_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_disabled(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(qtbot, dialog, WRONG_EXTENSION_FILE_PATH)

    show_and_close_window(qtbot, template)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user clearing the unit input box
    enter_units(qtbot, dialog, "")

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_red_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_units_box_has_white_background(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the replacing the default value with "km"
    enter_units(qtbot, dialog, VALID_UNITS)

    assert dialog.unitsLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_geometry_THEN_add_component_button_is_enabled(
    qtbot, template, dialog
):

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
    qtbot, template, dialog
):

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
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(qtbot, dialog, VALID_MESH_FILE_PATH)

    # Mimic the user giving invalid units input
    enter_units(qtbot, dialog, INVALID_UNITS)

    assert not dialog.buttonBox.isEnabled()


def test_UI_GIVEN_mesh_geometry_selected_THEN_relevant_fields_are_visible(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_mesh_geometry_selected_THEN_irrelevant_fields_are_invisible(
    qtbot, template, dialog
):

    # Mimic the user selecting a mesh geometry
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)

    show_and_close_window(qtbot, template)

    assert not dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_relevant_fields_are_visible(
    qtbot, template, dialog
):

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    show_and_close_window(qtbot, template)

    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_irrelevant_fields_are_invisible(
    qtbot, template, dialog
):

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)

    assert not dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_selected_THEN_default_values_are_correct(
    qtbot, template, dialog
):

    # Mimic the user selecting a cylinder geometry
    systematic_radio_button_press(qtbot, dialog.CylinderRadioButton)
    show_and_close_window(qtbot, template)

    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.cylinderHeightLineEdit.value() == 1.0
    assert dialog.cylinderRadiusLineEdit.value() == 1.0
    assert dialog.cylinderXLineEdit.value() == 0.0
    assert dialog.cylinderYLineEdit.value() == 0.0
    assert dialog.cylinderZLineEdit.value() == 1.0


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def make_another_qtest():
        bot = QtBot(request)
        bot.wait(1)

    request.addfinalizer(make_another_qtest)


def get_geometry_button(dialog: AddComponentDialog, button_name: str):
    """
    Finds the geometry button that contains the given text.
    :param dialog: An instance of an AddComponentDialog.
    :param button_name: The name of the desired button.
    :return: The QRadioButton for the given geometry type.
    """
    for child in dialog.geometryTypeBox.findChildren(PySide2.QtWidgets.QRadioButton):
        if child.text() == button_name:
            return child


def make_pixel_options_appear(
    qtbot: pytestqt.qtbot.QtBot,
    dialog: AddComponentDialog,
    template: PySide2.QtWidgets.QDialog,
    pixel_options_index: int,
):
    """
    Create the conditions to allow the appearance of the pixel options.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param pixel_options_index: The index of a component type for the combo box that has pixel fields.
    """
    systematic_radio_button_press(qtbot, dialog.meshRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(pixel_options_index)
    show_and_close_window(qtbot, template)


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

    for x in range(1, size.width()):
        for y in range(1, size.height()):
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
    dialog.geometry_file_name = file_path


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
