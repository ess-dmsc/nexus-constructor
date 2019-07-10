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
    reason="Leads to seg faults. Clicking with QActions/QIcons doesn't seem to be possible."
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

    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    template.show()
    qtbot.waitForWindowShown(template)
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

    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    template.show()
    qtbot.waitForWindowShown(template)
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()


def test_GIVEN_correct_class_WHEN_selecting_nxclass_THEN_pixel_options_becomes_visible(
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


def create_add_component_dialog(test_count):
    nexus_name = "test" + str(test_count)
    instrument = Instrument(NexusWrapper(nexus_name))
    component = ComponentTreeModel(instrument)
    return AddComponentDialog(instrument, component)
