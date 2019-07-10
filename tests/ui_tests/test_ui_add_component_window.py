import pytest
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDialog

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.instrument import Instrument
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper


# Workaround - even when skipping jenkins is not happy importing AddComponentDialog due to a missing lib


@pytest.mark.skip(reason="Leads to seg faults. Clicking with QActions is not possible.")
def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot
):
    template = QMainWindow()
    window = MainWindow(Instrument(NexusWrapper("test1")))
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

    instrument = Instrument(NexusWrapper("test2"))
    template = QDialog()
    dialog = AddComponentDialog(instrument, ComponentTreeModel(instrument))
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.noGeometryRadioButton, Qt.LeftButton)

    assert not dialog.geometryOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):
    instrument = Instrument(NexusWrapper("test3"))
    component = ComponentTreeModel(instrument)
    template = QDialog()
    dialog = AddComponentDialog(instrument, component)
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.CylinderRadioButton, Qt.LeftButton)

    template.show()
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.cylinderOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()


def test_GIVEN_mesh_geometry_WHEN_selecting_geometry_type_THEN_relevant_fields_are_shown(
    qtbot
):

    instrument = Instrument(NexusWrapper("test4"))
    component = ComponentTreeModel(instrument)
    template = QDialog()
    dialog = AddComponentDialog(instrument, component)
    template.ui = dialog
    template.ui.setupUi(template)

    qtbot.addWidget(template)

    qtbot.mouseClick(dialog.meshRadioButton, Qt.LeftButton)

    template.show()
    assert dialog.geometryOptionsBox.isVisible()
    assert dialog.unitsbox.isVisible()
    assert dialog.geometryFileBox.isVisible()
