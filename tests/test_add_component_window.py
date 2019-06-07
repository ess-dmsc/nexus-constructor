from PySide2.QtWidgets import QMainWindow, QDialog

from nexus_constructor.addcomponentwindow import validate_line_edit, AddComponentDialog
from nexus_constructor.mainwindow import MainWindow
from nexus_constructor.nexus_wrapper import NexusWrapper
from PySide2.QtCore import Qt


class DummyLineEdit:
    def setStyleSheet(self, str):
        self.stylesheet = str

    def styleSheet(self):
        return self.stylesheet


def test_GIVEN_invalid_WHEN_validating_line_edit_THEN_line_edit_turns_red():

    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, False)
    assert "background-color: #f6989d" in line_edit.styleSheet()


def test_GIVEN_valid_WHEN_validating_line_edit_THEN_line_edit_turns_white():
    line_edit = DummyLineEdit()
    validate_line_edit(line_edit, True)
    assert "background-color: #FFFFFF" in line_edit.styleSheet()


def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):
    template = QMainWindow()
    window = MainWindow(NexusWrapper("test1"))
    template.ui = window
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(window.pushButton, Qt.LeftButton)

    assert window.add_window.isVisible()

    window.add_window.close()


def test_UI_GIVEN_no_geometry_WHEN_selecting_geometry_type_THEN_geometry_options_are_hidden(
    qtbot
):
    template = QDialog()
    dialog = AddComponentDialog(NexusWrapper("test2"))
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    template = QDialog()
    dialog = AddComponentDialog(NexusWrapper("test3"))
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    assert dialog.cylinderOptionsBox.isEnabled()
    assert dialog.unitsbox.isEnabled()
