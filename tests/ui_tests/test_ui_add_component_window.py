from PySide2.QtWidgets import QMainWindow, QDialog
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.instrument import Instrument
from PySide2.QtCore import Qt


def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):
    template = QMainWindow()
    window = MainWindow(Instrument(NexusWrapper("test1")))
    template.ui = window
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(window.pushButton, Qt.LeftButton)

    assert window.add_component_window.isVisible()

    window.add_component_window.close()


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):
    template = QDialog()
    dialog = AddComponentDialog(Instrument(NexusWrapper("test2")))
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    template = QDialog()
    dialog = AddComponentDialog(Instrument(NexusWrapper("test3")))
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    assert dialog.cylinderOptionsBox.isEnabled()
    assert dialog.unitsbox.isEnabled()
