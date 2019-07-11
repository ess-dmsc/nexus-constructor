import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDialog

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


# Workaround - even when skipping jenkins is not happy importing AddComponentDialog due to a missing lib


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
    template.show()
    assert window.add_component_window.isVisible()

    window.add_component_window.close()


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):
    template = QDialog()
    dialog = create_add_component_dialog(1)
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    template = QDialog()
    dialog = create_add_component_dialog(2)
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


def test_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    template = QDialog()
    dialog = create_add_component_dialog(3)
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


def test_GIVEN_class_with_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_visible(
    qtbot
):
    template = QDialog()
    dialog = create_add_component_dialog(4)
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

        for index in pixel_options_class_indices:
            dialog.componentTypeComboBox.setCurrentIndex(index)
            template.show()
            qtbot.waitForWindowShown(template)
            assert dialog.pixelOptionsBox.isVisible()


def test_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_THEN_pixel_options_becomes_invisible(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog(5)
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
        dialog.noGeometryRadioButton,
        dialog.meshRadioButton,
        dialog.CylinderRadioButton,
    ]

    for geometry_button in all_geometry_buttons:

        qtbot.mouseClick(geometry_button, Qt.LeftButton)
        template.show()
        qtbot.waitForWindowShown(template)

        for index in no_pixel_options_class_indices:

            # Check that it starts off invisible
            assert not dialog.pixelOptionsBox.isVisible()

            # Set the pixel options to visible
            dialog.pixelOptionsBox.setVisible(True)
            dialog.geometryOptionsBox.setVisible(True)
            assert dialog.pixelOptionsBox.isVisible()

            # Change the index and check that the pixel options have become invisible again
            dialog.componentTypeComboBox.setCurrentIndex(index)
            assert not dialog.pixelOptionsBox.isVisible()


def test_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog(6)
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    # Check that the background color of the ext field starts as red
    assert dialog.nameLineEdit.styleSheet() == "QLineEdit { background-color: #f6989d }"

    # Mimic the user entering a name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "AUniqueName")

    # Check that the background color of the test field has changed to white
    assert dialog.nameLineEdit.styleSheet() == "QLineEdit { background-color: #FFFFFF }"


def test_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot
):

    template = QDialog()
    dialog = create_add_component_dialog(7)
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    red_background_style_sheet = "QLineEdit { background-color: #f6989d }"

    # Check that the background color of the text field starts as red
    assert dialog.nameLineEdit.styleSheet() == red_background_style_sheet

    # Mimic the user entering a non-unique name in the text field
    qtbot.mouseClick(dialog.nameLineEdit, Qt.LeftButton)
    qtbot.keyClicks(dialog.nameLineEdit, "sample")

    # Check that the background color of the test field has remained red
    assert dialog.nameLineEdit.styleSheet() == red_background_style_sheet


def create_add_component_dialog(test_count):
    nexus_name = "test" + str(test_count)
    instrument = Instrument(NexusWrapper(nexus_name))
    component = ComponentTreeModel(instrument)
    return AddComponentDialog(instrument, component)
