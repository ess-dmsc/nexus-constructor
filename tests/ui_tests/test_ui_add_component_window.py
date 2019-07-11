import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog
from PySide2.QtWidgets import QMainWindow

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

# Workaround - even when skipping jenkins is not happy importing AddComponentDialog due to a missing lib

nexus_wrapper_count = 0
RED_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QLineEdit { background-color: #FFFFFF }"


@pytest.mark.skip(
    reason="Clicking with QActions/QIcons doesn't seem to be possible. This test causes seg faults at the moment."
)
def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):

    template = QMainWindow()
    window = MainWindow(Instrument(NexusWrapper("test")))
    template.ui = window
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Using trigger rather than clicking on the menu
    window.new_component_action.trigger()
    assert window.add_component_window.isVisible()

    window.add_component_window.close()


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    from PySide2.QtWidgets import QDialog
    from PySide2.QtCore import Qt

    template = QDialog()

    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the cylinder geometry button
    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)
    template.show()
    qtbot.waitForWindowShown(template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()


def test_UI_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Check that the relevant fields start as invisible
    assert not dialog.geometryOptionsBox.isVisible()
    assert not dialog.cylinderOptionsBox.isVisible()
    assert not dialog.unitsbox.isVisible()

    # Click on the mesh geometry button
    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)
    template.show()
    qtbot.waitForWindowShown(template)

    # Check that this has caused the relevant fields to become visible
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_UI_GIVEN_class_with_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_visible(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    classes = list(dialog.nx_component_classes.keys())
    pixel_options_class_indices = []

    for i, nx_class in enumerate(classes):
        if nx_class in component_type.PIXEL_COMPONENT_TYPES:
            pixel_options_class_indices.append(i)

    pixel_geometry_buttons = [dialog.meshRadioButton, dialog.CylinderRadioButton]

    for geometry_button in pixel_geometry_buttons:

        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        template.show()
        qtbot.waitForWindowShown(template)

        for index in pixel_options_class_indices:

            # Change the pixel options to invisible manually
            dialog.pixelOptionsBox.setVisible(False)
            assert not dialog.pixelOptionsBox.isVisible()

            dialog.componentTypeComboBox.setCurrentIndex(index)
            template.show()
            qtbot.waitForWindowShown(template)

            assert dialog.pixelOptionsBox.isVisible()


def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_invisible(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    classes = list(dialog.nx_component_classes.keys())
    no_pixel_options_class_indices = []

    for i, nx_class in enumerate(classes):
        if nx_class not in component_type.PIXEL_COMPONENT_TYPES:
            no_pixel_options_class_indices.append(i)

    # Put the first index at the end. Otherwise changing from 0 to 0 doesn't trigger the indexChanged signal.
    no_pixel_options_class_indices.append(no_pixel_options_class_indices.pop(0))

    all_geometry_buttons = [
        dialog.meshRadioButton,
        dialog.CylinderRadioButton,
    ]

    for geometry_button in all_geometry_buttons:

        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        template.show()
        qtbot.waitForWindowShown(template)

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

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Check that the background color of the ext field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "AUniqueName")

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == WHITE_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "sample")

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == RED_BACKGROUND_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_THEN_add_component_window_remains_open(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    template.show()
    qtbot.waitForWindowShown(template)

    # Mimic the user entering a non-unique name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "sample")
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_THEN_add_component_window_closes(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog()
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    template.show()
    qtbot.waitForWindowShown(template)

    # Mimic the user entering a non-unique name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "AUniqueName")
    qtbot.mouseClick(dialog.buttonBox, Qt.LeftButton)

    assert not template.isVisible()


def create_add_component_dialog():

    global nexus_wrapper_count
    nexus_name = "test" + str(nexus_wrapper_count)
    instrument = Instrument(NexusWrapper(nexus_name))
    component = ComponentTreeModel(instrument)
    nexus_wrapper_count += 1
    return AddComponentDialog(instrument, component)
