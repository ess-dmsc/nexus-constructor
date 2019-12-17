import os

import PySide2
import h5py
import pytest
import pytestqt
from PySide2.QtCore import Qt
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QDialog, QRadioButton, QMainWindow
from mock import Mock, call, patch, mock_open
from pytestqt.qtbot import QtBot
import numpy as np

from nexus_constructor.component import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.component.component import Component
from nexus_constructor.component.component_factory import create_component
from nexus_constructor.component.component_shape import ComponentShape
from nexus_constructor.component.pixel_shape import PixelShape
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.field_attrs import FieldAttrFrame
from nexus_constructor.geometry import NoShapeGeometry
from nexus_constructor.geometry import (
    OFFGeometryNoNexus,
    CylindricalGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.instrument import Instrument
from nexus_constructor.instrument_view import InstrumentView
from nexus_constructor.main_window import MainWindow
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, PixelData
from nexus_constructor.pixel_data_to_nexus_utils import PIXEL_FIELDS
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.validators import FieldType, PixelValidator, DATASET_TYPE
from tests.helpers import create_nexus_wrapper
from tests.test_utils import DEFINITIONS_DIR
from tests.ui_tests.ui_test_utils import (
    systematic_button_press,
    show_and_close_window,
    RED_LINE_EDIT_STYLE_SHEET,
    WHITE_LINE_EDIT_STYLE_SHEET,
    VALID_CUBE_OFF_FILE,
    VALID_OCTA_OFF_FILE,
)

MISMATCHING_PIXEL_GRID_VALUES = [("0", "5.3"), ("1", "")]

WRONG_EXTENSION_FILE_PATH = os.path.join(os.getcwd(), "requirements.txt")
NONEXISTENT_FILE_PATH = "doesntexist.off"
VALID_CUBE_MESH_FILE_PATH = os.path.join(os.getcwd(), "tests", "cube.off")
VALID_OCTA_MESH_FILE_PATH = os.path.join(os.getcwd(), "tests", "octa.off")

UNIQUE_COMPONENT_NAME = "AUniqueName"
NONUNIQUE_COMPONENT_NAME = "sample"
VALID_UNITS = "km"
INVALID_UNITS = "abc"

PIXEL_GRID_FIELDS = [
    "x_pixel_offset",
    "y_pixel_offset",
    "z_pixel_offset",
    "pixel_shape",
]

instrument = Instrument(NexusWrapper("pixels"), DEFINITIONS_DIR)
component = ComponentTreeModel(instrument)

PIXEL_OPTIONS = dict()
NO_PIXEL_OPTIONS = dict()
ALL_COMPONENT_TYPES = dict()

for i, component_class in enumerate(
    list(
        AddComponentDialog(
            instrument, component, definitions_dir=DEFINITIONS_DIR
        ).nx_component_classes.keys()
    )
):

    ALL_COMPONENT_TYPES[component_class] = i

    if component_class in component_type.PIXEL_COMPONENT_TYPES:
        PIXEL_OPTIONS[component_class] = i
    else:
        NO_PIXEL_OPTIONS[component_class] = i

# Select a subset of the component class to use in parameterised tests
# Should include any for which the UI is specialised
_components_subset = {"NXdetector", "NXdisk_chopper", "NXsensor"}
COMPONENT_TYPES_SUBSET = {
    class_name: position_in_combo_box
    for class_name, position_in_combo_box in ALL_COMPONENT_TYPES.items()
    if class_name in _components_subset
}
NO_PIXEL_OPTIONS_SUBSET = {
    class_name: position_in_combo_box
    for class_name, position_in_combo_box in NO_PIXEL_OPTIONS.items()
    if class_name in _components_subset
}

SHAPE_TYPE_BUTTONS = ["No Shape", "Mesh", "Cylinder"]

FIELDS_VALUE_TYPES = {key: i for i, key in enumerate(DATASET_TYPE.keys())}
FIELD_TYPES = {item.value: i for i, item in enumerate(FieldType)}


@pytest.fixture(scope="function")
def template(qtbot):
    return QDialog()


@pytest.fixture(scope="function")
def mock_pixel_options():
    """
    Creates a mock of the PixelOptions widget. Used for some basic testing of AddComponentDialog behaviour that requires
    interaction with the PixelOptions. Testing of the PixelOptions behaviour takes place in a dedicated file.
    """
    pixel_options = Mock(spec=PixelOptions)
    pixel_options.validator = Mock(spec=PixelValidator)
    pixel_options.validator.unacceptable_pixel_states = Mock(return_value=[])

    # When the method for creating a pixel mapping is called in PixelOptions, it causes the current mapping filename
    # stored in PixelOptions to change. This behaviour is going to be mimicked with a side effect mock.
    def change_mapping_filename(filename):
        pixel_options.get_current_mapping_filename = Mock(return_value=filename)

    pixel_options.populate_pixel_mapping_list_with_mesh = Mock(
        side_effect=change_mapping_filename
    )

    # Make the filename in PixelOptions start as None as this is what the PixelOptions has after its been initialised.
    change_mapping_filename(None)

    return pixel_options


@pytest.fixture(scope="function")
def add_component_dialog(qtbot, template, mock_pixel_options):

    instrument = Instrument(NexusWrapper("test"), DEFINITIONS_DIR)
    component = ComponentTreeModel(instrument)
    dialog = AddComponentDialog(instrument, component, definitions_dir=DEFINITIONS_DIR)
    template.ui = dialog
    template.ui.setupUi(template, mock_pixel_options)
    qtbot.addWidget(template)

    yield dialog

    # Close the file to avoid an error
    instrument.nexus.nexus_file.close()


@pytest.fixture(scope="function")
def component_with_cylindrical_geometry():
    nexus_wrapper = create_nexus_wrapper()
    shape_group = nexus_wrapper.create_nx_group(
        "shape", "NXcylindrical_geometry", nexus_wrapper.instrument
    )
    nexus_wrapper.create_nx_group(
        "detector_shape", "NXcylindrical_geometry", shape_group
    )
    component = create_component(nexus_wrapper, shape_group)
    component.set_cylinder_shape()
    component.nx_class = "NXdetector"
    component.name = "CylindricalComponent"
    return component


@pytest.fixture(scope="function")
def parent_mock():

    parent_mock = Mock(spec=MainWindow)
    parent_mock.sceneWidget = Mock(spec=InstrumentView)
    return parent_mock


@pytest.fixture(scope="function")
def edit_component_dialog(
    qtbot,
    template,
    component_with_cylindrical_geometry,
    mock_pixel_options,
    parent_mock,
):

    instrument = Instrument(NexusWrapper("test"), DEFINITIONS_DIR)
    instrument.nexus = component_with_cylindrical_geometry.file
    component_tree = ComponentTreeModel(instrument)
    dialog = AddComponentDialog(
        instrument,
        component_tree,
        component_with_cylindrical_geometry,
        definitions_dir=DEFINITIONS_DIR,
    )
    template.ui = dialog
    template.ui.setupUi(template, mock_pixel_options)
    qtbot.addWidget(template)

    dialog.parent = Mock(return_value=parent_mock)

    yield dialog

    # Close the file to avoid an error
    instrument.nexus.nexus_file.close()


@pytest.fixture(scope="function")
def mock_pixel_validator(add_component_dialog, mock_pixel_options):
    """
    Create a mock PixelValidator to give to the AddComponentDialog's OKValidator. The OKValidator requires knowledge of
    the PixelValidator's `unacceptable_pixel_states` so this will be mocked to mimic valid/invalid Pixel Data input.
    """
    pixel_validator = Mock(spec=PixelValidator)
    pixel_validator.unacceptable_pixel_states = Mock(return_value=[])

    add_component_dialog.ok_validator.pixel_validator = pixel_validator
    mock_pixel_options.pixel_validator = pixel_validator
    mock_pixel_options.get_validator = Mock(return_value=pixel_validator)

    return pixel_validator


@pytest.fixture(scope="function")
def mock_component():

    nexus_file = h5py.File("test_file", mode="x", driver="core", backing_store=False)
    test_group = nexus_file.create_group("test_component_group")
    mock_component = Mock(spec=Component, group=test_group, shape=(None, None))
    yield mock_component
    nexus_file.close()


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
    Create the conditions to allow the disappearance of the pixel options by pressing the NoShape button.
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
    pixel_options_index: int = PIXEL_OPTIONS["NXdetector"],
):
    """
    Create the conditions to allow the appearance of the pixel options by choosing NXdetector or NXdetector_module as
    the component type and NXcylindrical_geometry or NXoff_geometry as the shape type.
    :param qtbot: The qtbot testing tool.
    :param button: The Mesh or Cylinder radio button.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param pixel_options_index: The index of a component type for the combo box that has pixel fields.
    """
    systematic_button_press(qtbot, template, button)
    dialog.componentTypeComboBox.setCurrentIndex(pixel_options_index)
    show_and_close_window(qtbot, template)


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


def enter_disk_chopper_fields(
    qtbot: pytestqt.qtbot.QtBot,
    dialog: AddComponentDialog,
    template: PySide2.QtWidgets.QDialog,
    component_name: str = "ThisIsADiskChopper",
):
    """
    Mimics a user creating an NXdisk_chopper by filling in the related fields/attributes.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param component_name: The name of the Disk Chopper.
    """
    # Set the name and NXclass of the component
    qtbot.keyClicks(dialog.nameLineEdit, component_name)
    dialog.componentTypeComboBox.setCurrentIndex(ALL_COMPONENT_TYPES["NXdisk_chopper"])

    # Press the Add Field button four times and create a list of fields widgets
    for _ in range(4):
        systematic_button_press(qtbot, template, dialog.addFieldPushButton)
    fields_widgets = [
        dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(i))
        for i in range(4)
    ]

    # Enter the field names
    qtbot.keyClicks(fields_widgets[0].field_name_edit, "slits")
    qtbot.keyClicks(fields_widgets[1].field_name_edit, "slit_edges")
    qtbot.keyClicks(fields_widgets[2].field_name_edit, "radius")
    qtbot.keyClicks(fields_widgets[3].field_name_edit, "slit_height")

    show_and_close_window(qtbot, template)

    # Set the field types
    fields_widgets[0].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["Integer"])
    fields_widgets[1].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["Float"])
    fields_widgets[2].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["Float"])
    fields_widgets[3].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["Float"])

    show_and_close_window(qtbot, template)

    # Make the angles field an array type
    fields_widgets[1].field_type_combo.setCurrentIndex(
        FIELD_TYPES[FieldType.array_dataset.value]
    )

    show_and_close_window(qtbot, template)

    # Enter the field values
    qtbot.keyClicks(fields_widgets[0].value_line_edit, "6")
    qtbot.keyClicks(fields_widgets[2].value_line_edit, "200")
    qtbot.keyClicks(fields_widgets[3].value_line_edit, "100")

    # Manually edit the angles array
    fields_widgets[1].table_view.model.array = np.array(
        [[(i * 10.0)] for i in range(12)]
    )

    # Set the units attributes
    slit_edges_attribute_frame = FieldAttrFrame()
    slit_edges_attribute_frame.attr_dtype_combo.setCurrentText("String")
    slit_edges_attribute_frame.value = ("units", "deg")

    radius_attribute_frame = FieldAttrFrame()
    radius_attribute_frame.attr_dtype_combo.setCurrentText("String")
    radius_attribute_frame.value = ("units", "mm")

    slit_height_attribute_frame = FieldAttrFrame()
    slit_height_attribute_frame.attr_dtype_combo.setCurrentText("String")
    slit_height_attribute_frame.value = ("units", "mm")

    fields_widgets[1].attrs_dialog._add_attr(slit_edges_attribute_frame)
    fields_widgets[2].attrs_dialog._add_attr(radius_attribute_frame)
    fields_widgets[3].attrs_dialog._add_attr(slit_height_attribute_frame)

    show_and_close_window(qtbot, template)


def get_new_component_from_dialog(dialog: AddComponentDialog, name: str) -> Component:
    """
    Get the stored component from an AddComponentDialog after the "Add Component" button has been pressed.
    :param dialog: The AddComponentDialog.
    :param name: The name of the component that is being searched for.
    :return: The component.
    """
    for component in dialog.instrument.get_component_list():
        if component.name == name:
            return component


def enter_component_with_pixel_fields(
    add_component_dialog: AddComponentDialog,
    button: QRadioButton,
    component_name: str,
    mock_pixel_options: Mock,
    qtbot: pytestqt.qtbot.QtBot,
    template: QDialog,
    pixel_data: PixelData,
):
    """
    :param add_component_dialog: The AddComponentDialog.
    :param component_name: The name of the component.
    :param button: The button that is selected (Mesh or Cylinder) when creating the component with Pixel Data.
    :param mock_pixel_options: A mock of the PixelOptions that will be instructed to return a PixelGrid, a PixelMapping,
        or None.
    :param qtbot: The QtBot testing tool.
    :param template: The QDialog that stores the Add Component widget.
    """
    make_pixel_options_appear(qtbot, button, add_component_dialog, template)
    enter_component_name(qtbot, template, add_component_dialog, component_name)
    mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_data)


def enter_and_create_component_with_pixel_data(
    add_component_dialog: AddComponentDialog,
    component_name: str,
    cylinders: bool,
    mock_pixel_options: Mock,
    qtbot: pytestqt.qtbot.QtBot,
    template: QDialog,
    pixel_data: PixelData = None,
):
    """
    Mimics the user creating a component with PixelData and then pressing the "Add Component" button. Used for testing
    pixel data editing.
    :param add_component_dialog: The AddComponentDialog.
    :param cylinders: A bool that decides if the shape is a Cylinder or an OFF Mesh. Determines which button is pressed.
    :param mock_pixel_options: Mock Pixel Options that return Pixel Data.
    :param qtbot: The qtbot testing tool.
    :param template: The QDialog that stores the Add Component widget.
    :param pixel_data: The PixelData returned by the mock Pixel Options when the "Add Component" button is pressed.
    """
    if cylinders:
        button = add_component_dialog.CylinderRadioButton
        expected_geometry = CylindricalGeometry
    else:
        button = add_component_dialog.meshRadioButton
        expected_geometry = OFFGeometryNexus

    enter_component_with_pixel_fields(
        add_component_dialog,
        button,
        component_name,
        mock_pixel_options,
        qtbot,
        template,
        pixel_data,
    )
    if not cylinders:
        enter_file_path(
            qtbot,
            add_component_dialog,
            template,
            VALID_CUBE_MESH_FILE_PATH,
            VALID_CUBE_OFF_FILE,
        )
    add_component_dialog.on_ok()
    return expected_geometry


def edit_component_with_pixel_fields(
    add_component_dialog: AddComponentDialog,
    component_to_edit: Component,
    parent_mock: Mock,
    mock_pixel_options: Mock = None,
    pixel_data: PixelData = None,
):
    """
    Mimics a component with PixelData being edited.
    :param add_component_dialog: The AddComponentDialog.
    :param component_to_edit: The component being edited.
    :param parent_mock: A mock of the AddComponentDialog parent.
    :param mock_pixel_options: A PixelOptions mock that will generate new, different Pixel Data when the
        "Edit Component" button is pressed.
    :param pixel_data: The PixelData that is "generated" by the PixelOptions mock.
    """
    # Give the AddComponentDialog a component_to_edit value so it behaves like an Edit Component window
    add_component_dialog.component_to_edit = component_to_edit
    add_component_dialog.parent = Mock(return_value=parent_mock)

    # Instruct the pixel options mock to generate different pixel data
    if mock_pixel_options is not None:
        mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_data)

    add_component_dialog.on_ok()


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
    qtbot, template, add_component_dialog
):
    systematic_button_press(qtbot, template, add_component_dialog.noShapeRadioButton)
    assert not add_component_dialog.shapeOptionsBox.isVisible()


@pytest.mark.parametrize("shape_button_name", SHAPE_TYPE_BUTTONS)
def test_UI_GIVEN_nothing_WHEN_changing_component_shape_type_THEN_add_component_button_is_always_disabled(
    qtbot, template, add_component_dialog, shape_button_name
):
    systematic_button_press(
        qtbot, template, get_shape_type_button(add_component_dialog, shape_button_name)
    )

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nothing_WHEN_selecting_cylinder_type_THEN_relevant_fields_are_shown(
    qtbot, template, add_component_dialog
):
    # Click on the cylinder shape button
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    # Check that this has caused the relevant fields to become visible
    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.cylinderOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()

    # Check that the file input isn't visible as this is only available for the mesh
    assert not add_component_dialog.geometryFileBox.isVisible()
    # Check that the pixel grid options aren't visible as this is only available for certain NXclasses
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


def test_UI_GIVEN_nothing_WHEN_selecting_mesh_shape_THEN_relevant_fields_are_shown(
    qtbot, template, add_component_dialog
):
    # Click on the mesh shape button
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Check that this has caused the relevant fields to become visible
    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()
    assert add_component_dialog.geometryFileBox.isVisible()

    # Check that the cylinder options aren't visible
    assert not add_component_dialog.cylinderOptionsBox.isVisible()
    # Check that the pixel grid options aren't visible as this is only available for certain NXclasses
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


@pytest.mark.parametrize("shape_with_units", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_nothing_WHEN_selecting_shape_with_units_THEN_default_units_are_metres(
    qtbot, template, add_component_dialog, shape_with_units
):
    # Click on the button of a shape type with units
    systematic_button_press(
        qtbot, template, get_shape_type_button(add_component_dialog, shape_with_units)
    )

    # Check that the units line edit is visible and has metres by default
    assert add_component_dialog.unitsLineEdit.isVisible()
    assert add_component_dialog.unitsLineEdit.text() == "m"


@pytest.mark.parametrize("pixels_class", PIXEL_OPTIONS.keys())
@pytest.mark.parametrize("any_component_type", COMPONENT_TYPES_SUBSET)
@pytest.mark.parametrize("pixel_shape_name", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_class_and_shape_with_pixel_fields_WHEN_adding_component_THEN_pixel_options_go_from_invisible_to_visible(
    qtbot,
    template,
    add_component_dialog,
    pixels_class,
    any_component_type,
    pixel_shape_name,
):
    # Change the pixel options to visible by selecting a cylinder/mesh shape and a NXclass with pixel fields
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(add_component_dialog, pixel_shape_name),
        add_component_dialog,
        template,
        PIXEL_OPTIONS[pixels_class],
    )
    # Check that this has caused the pixel options to become visible
    assert add_component_dialog.pixelOptionsWidget.isVisible()


@pytest.mark.parametrize("any_component_type", COMPONENT_TYPES_SUBSET.keys())
def test_UI_GIVEN_any_nxclass_WHEN_adding_component_with_no_shape_THEN_pixel_options_go_from_visible_to_invisible(
    qtbot, template, add_component_dialog, any_component_type
):
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    # Change the pixel options to invisible
    make_pixel_options_disappear(
        qtbot, add_component_dialog, template, ALL_COMPONENT_TYPES[any_component_type]
    )
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


@pytest.mark.parametrize("no_pixels_class", NO_PIXEL_OPTIONS_SUBSET.keys())
@pytest.mark.parametrize("pixels_class", PIXEL_OPTIONS.keys())
@pytest.mark.parametrize("shape_name", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_for_component_with_mesh_or_cylinder_shape_THEN_pixel_options_becomes_invisible(
    qtbot, template, add_component_dialog, no_pixels_class, pixels_class, shape_name
):
    # Make the pixel options become visible
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(add_component_dialog, shape_name),
        add_component_dialog,
        template,
        PIXEL_OPTIONS[pixels_class],
    )
    assert add_component_dialog.pixelOptionsWidget.isVisible()

    # Change nxclass to one without pixel fields and check that the pixel options have become invisible again
    add_component_dialog.componentTypeComboBox.setCurrentIndex(
        NO_PIXEL_OPTIONS[no_pixels_class]
    )
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


def test_UI_GIVEN_user_changes_shape_WHEN_adding_component_THEN_validity_is_reassessed(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)
    mock_pixel_options.update_pixel_input_validity.assert_called_once()
    mock_pixel_options.reset_mock()

    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)
    mock_pixel_options.update_pixel_input_validity.assert_called_once()


def test_UI_GIVEN_cylinder_shape_WHEN_user_chooses_pixel_mapping_THEN_pixel_mapping_list_is_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, template
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_called_once_with(
        1
    )


@pytest.mark.xfail(
    reason="For the time being the number of cylinders is now frozen at one."
)
def test_UI_GIVEN_increasing_cylinder_count_WHEN_user_chooses_pixel_mapping_THEN_pixel_mapping_list_is_regenerated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, template
    )

    cylinder_count = 4
    calls = []

    for i in range(2, cylinder_count):
        qtbot.keyClick(add_component_dialog.cylinderCountSpinBox, Qt.Key_Up)
        calls.append(call(i))

    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_has_calls(
        calls
    )


def test_UI_GIVEN_same_mesh_file_twice_WHEN_user_selects_file_THEN_mapping_list_remains_the_same(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Provide the same file as before
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the method for populating the pixel mapping was only called once even though a file was selected twice
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_called_once_with(
        VALID_CUBE_MESH_FILE_PATH
    )


def test_UI_GIVEN_pixel_options_are_not_visible_WHEN_giving_mesh_file_THEN_mapping_list_is_not_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_pixel_options_are_not_visible_WHEN_changing_cylinder_count_THEN_mapping_list_is_not_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    qtbot.keyClick(add_component_dialog.cylinderCountSpinBox, Qt.Key_Up)

    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_not_called()


def test_UI_GIVEN_invalid_file_WHEN_giving_mesh_file_THEN_mapping_list_is_not_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    enter_file_path(qtbot, add_component_dialog, template, VALID_CUBE_OFF_FILE, "OFF")

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_different_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_changes(
    qtbot, template, add_component_dialog, mock_pixel_options
):
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    # Provide a path and file for a cube mesh
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Provide a path and file for an octahedron mesh
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_OCTA_MESH_FILE_PATH,
        VALID_OCTA_OFF_FILE,
    )

    # Check that two different files being given means the method was called twice
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_has_calls(
        [call(VALID_CUBE_MESH_FILE_PATH), call(VALID_OCTA_MESH_FILE_PATH)]
    )


def test_UI_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot, template, add_component_dialog
):
    # Check that the background color of the ext field starts as red
    assert add_component_dialog.nameLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET

    # Mimic the user entering a name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert add_component_dialog.nameLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_repeated_name_WHEN_choosing_component_name_THEN_background_remains_red(
    qtbot, template, add_component_dialog
):

    # Check that the background color of the text field starts as red
    assert add_component_dialog.nameLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(
        qtbot, template, add_component_dialog, NONUNIQUE_COMPONENT_NAME
    )

    # Check that the background color of the test field has remained red
    assert add_component_dialog.nameLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_shape_THEN_add_component_window_remains_open(
    qtbot, template, add_component_dialog
):

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(
        qtbot, template, add_component_dialog, NONUNIQUE_COMPONENT_NAME
    )

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.buttonBox, Qt.LeftButton)

    # The window won't close because the button is disabled
    assert template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_window_closes(
    qtbot, template, add_component_dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_shape_THEN_add_component_window_closes(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user entering valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_cylinder_shape_THEN_add_component_window_closes(
    qtbot, template, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.buttonBox, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not template.isVisible()


def test_UI_GIVEN_invalid_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a no shape
    systematic_button_press(qtbot, template, add_component_dialog.noShapeRadioButton)

    # Mimic the user entering a non-unique name in the text field
    enter_component_name(
        qtbot, template, add_component_dialog, NONUNIQUE_COMPONENT_NAME
    )

    # The Add Component button is disabled
    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # The Add Component button is disabled because no input was given
    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_enabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no shape component is
    # there
    assert add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # No file name was given so we expect the file input box background to be red
    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user entering a bad file path
    enter_file_path(qtbot, add_component_dialog, template, NONEXISTENT_FILE_PATH, "OFF")

    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(
        qtbot, add_component_dialog, template, WRONG_EXTENSION_FILE_PATH, "OFF"
    )

    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_white_background(
    qtbot, template, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # The file input box should now have a white background
    assert add_component_dialog.fileLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        NONEXISTENT_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        WRONG_EXTENSION_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user clearing the unit input box
    enter_units(qtbot, add_component_dialog, "")

    assert add_component_dialog.unitsLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert add_component_dialog.unitsLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_white_background(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the replacing the default value with "km"
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    assert (
        add_component_dialog.unitsLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET
    )


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user giving valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    assert add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user clearing the units box
    enter_units(qtbot, add_component_dialog, "")

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_nonunique_name_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user giving an invalid component name
    enter_component_name(
        qtbot, template, add_component_dialog, NONUNIQUE_COMPONENT_NAME
    )

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_cylinder_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    # Mimic the user giving valid component name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_invalid_name_WHEN_adding_component_with_cylinder_shape_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    # Mimic the user giving valid units input
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    # Mimic the user giving valid component name
    enter_component_name(
        qtbot, template, add_component_dialog, NONUNIQUE_COMPONENT_NAME
    )

    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_mesh_shape_selected_WHEN_choosing_shape_THEN_relevant_fields_are_visible(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()
    assert add_component_dialog.geometryFileBox.isVisible()

    assert not add_component_dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_shape_selected_WHEN_choosing_shape_THEN_relevant_fields_are_visible(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()
    assert add_component_dialog.cylinderOptionsBox.isVisible()

    assert not add_component_dialog.geometryFileBox.isVisible()


@pytest.mark.parametrize("no_pixels_class", NO_PIXEL_OPTIONS_SUBSET.keys())
def test_UI_GIVEN_file_chosen_WHEN_pixel_mapping_options_not_visible_THEN_pixel_mapping_list_remains_empty(
    qtbot, template, add_component_dialog, no_pixels_class, mock_pixel_options
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)

    # Mimic the user selecting a component type that doesn't have pixel fields
    add_component_dialog.componentTypeComboBox.setCurrentIndex(
        NO_PIXEL_OPTIONS[no_pixels_class]
    )

    # Mimic the user giving a valid mesh file
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the pixel mapping list is still empty
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_invalid_off_file_WHEN_creating_pixel_mapping_THEN_pixel_mapping_widget_isnt_populated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    # Give an invalid file
    enter_file_path(
        qtbot, add_component_dialog, template, VALID_CUBE_MESH_FILE_PATH, "hfhuihfiuhf"
    )

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_cylinder_shape_selected_WHEN_adding_component_THEN_default_values_are_correct(
    qtbot, template, add_component_dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)

    assert add_component_dialog.cylinderOptionsBox.isVisible()
    assert add_component_dialog.cylinderHeightLineEdit.value() == 0.0
    assert add_component_dialog.cylinderRadiusLineEdit.value() == 0.0
    assert add_component_dialog.cylinderXLineEdit.value() == 0.0
    assert add_component_dialog.cylinderYLineEdit.value() == 0.0
    assert add_component_dialog.cylinderZLineEdit.value() == 1.0


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_is_shown(
    qtbot, template, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.edit_dialog.isEnabled()


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_table_is_shown(
    qtbot, template, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.table_view.isEnabled()


def test_UI_GIVEN_user_provides_valid_pixel_configuration_WHEN_entering_pixel_data_THEN_add_component_button_is_enabled(
    qtbot, template, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking valid pixel info was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[False, False])

    # Enter a valid name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is enabled
    assert add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_user_provides_invalid_pixel_grid_WHEN_entering_pixel_data_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking an invalid Pixel Grid was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[True, False])

    # Enter a valid name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is disabled despite the valid name and file path
    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_user_provides_invalid_pixel_mapping_WHEN_entering_pixel_data_THEN_add_component_button_is_disabled(
    qtbot, template, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking an invalid Pixel Mapping was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[False, True])

    # Enter a valid name
    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is disabled despite the valid name and file path
    assert not add_component_dialog.buttonBox.isEnabled()


def test_UI_GIVEN_user_presses_cylinder_button_WHEN_mesh_pixel_mapping_list_has_been_generated_THEN_new_pixel_mapping_list_is_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    mock_pixel_options.reset_mock()

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, template
    )

    mock_pixel_options.reset_pixel_mapping_list.assert_called_once()
    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_called_once_with(
        1
    )


def test_UI_GIVEN_user_presses_mesh_button_WHEN_cylinder_pixel_mapping_list_has_been_generated_WHEN_new_pixel_mapping_list_is_generated(
    qtbot, template, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, template
    )

    mock_pixel_options.reset_mock()

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, template
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.reset_pixel_mapping_list.assert_called_once()
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_called_once_with(
        VALID_CUBE_MESH_FILE_PATH
    )


def test_UI_GIVEN_pixel_grid_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_is_stored_in_component(
    qtbot, template, add_component_dialog, mock_pixel_options, mock_component
):

    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        template,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    pixel_grid = PixelGrid()
    mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_grid)
    show_and_close_window(qtbot, template)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        "nexus_constructor.component.component_factory.Component",
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_grid.assert_called_once_with(pixel_grid)
        mock_component.record_pixel_mapping.assert_not_called()


def test_UI_GIVEN_pixel_mapping_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_is_stored_in_component(
    qtbot, template, add_component_dialog, mock_pixel_options, mock_component
):

    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        template,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    pixel_mapping = PixelMapping(pixel_ids=[1])
    mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_mapping)
    show_and_close_window(qtbot, template)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        "nexus_constructor.component.component_factory.Component",
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_mapping.assert_called_once_with(pixel_mapping)
        mock_component.record_pixel_grid.assert_not_called()


def test_UI_GIVEN_no_pixel_data_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_writing_methods_are_not_called(
    qtbot, template, add_component_dialog, mock_pixel_options, mock_component
):
    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        template,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, template, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.generate_pixel_data = Mock(return_value=None)
    show_and_close_window(qtbot, template)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        "nexus_constructor.component.component_factory.Component",
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_mapping.assert_not_called()
        mock_component.record_pixel_grid.assert_not_called()


def test_UI_GIVEN_component_name_and_description_WHEN_editing_component_THEN_correct_values_are_loaded_into_UI(
    qtbot
):
    instrument = Instrument(
        NexusWrapper("test_component_editing_name"), DEFINITIONS_DIR
    )

    component_model = ComponentTreeModel(instrument)

    name = "test"
    nx_class = "NXmonitor"
    desc = "description"

    component = instrument.create_component(
        name=name, nx_class=nx_class, description=desc
    )

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                instrument,
                component_model,
                component_to_edit=component,
                definitions_dir=DEFINITIONS_DIR,
                parent=None,
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
    component, instrument, model = create_group_with_component(
        "test", "test_component_editing_no_shape"
    )

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                instrument,
                model,
                component_to_edit=component,
                definitions_dir=DEFINITIONS_DIR,
                parent=None,
            )
            template = QDialog()
            template.ui = dialog
            template.ui.setupUi(template)
            qtbot.addWidget(template)

            assert dialog.noShapeRadioButton.isChecked()


def test_UI_GIVEN_component_with_cylinder_shape_WHEN_editing_component_THEN_cylinder_shape_radio_is_checked(
    qtbot
):
    instrument = Instrument(
        NexusWrapper("test_component_editing_cylinder"), DEFINITIONS_DIR
    )
    component_model = ComponentTreeModel(instrument)

    component_name = "test"
    component = instrument.create_component(component_name, "NXpinhole", "")
    component.set_cylinder_shape(QVector3D(1, 1, 1), height=3, radius=4)

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                instrument,
                component_model,
                component_to_edit=component,
                definitions_dir=DEFINITIONS_DIR,
            )
            dialog.pixel_options = Mock(spec=PixelOptions)
            template = QDialog()
            template.ui = dialog
            template.ui.setupUi(template)
            qtbot.addWidget(template)

            assert dialog.CylinderRadioButton.isChecked()
            assert dialog.cylinderOptionsBox.isEnabled()


def test_UI_GIVEN_component_with_scalar_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_value(
    qtbot
):

    component, instrument, model = create_group_with_component(
        "chopper1", "test_component_editing_scalar_field"
    )

    field_name = "scalar"
    field_value = "test"
    component.set_field(field_name, field_value, dtype=h5py.special_dtype(vlen=str))

    dialog = AddComponentDialog(
        instrument, model, component_to_edit=component, definitions_dir=DEFINITIONS_DIR
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.fieldsListWidget.model().hasIndex(0, 0)
    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "scalar dataset"

    assert widget.name == field_name
    assert widget.value[()] == field_value


def create_group_with_component(component_name: str, file_name: str):
    """
    Convenience method, for when we don't really care about the component and just want one to be added to a file
    """
    instrument = Instrument(NexusWrapper(file_name), DEFINITIONS_DIR)
    model = ComponentTreeModel(instrument)
    component = instrument.create_component(component_name, "NXdisk_chopper", "")
    return component, instrument, model


def test_UI_GIVEN_component_with_array_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_value(
    qtbot
):
    component, instrument, model = create_group_with_component(
        "chopper1", "test_component_editing_array_field"
    )

    field_name = "array"
    field_value = np.array([1, 2, 3, 4, 5])
    component.set_field(field_name, field_value)
    dialog = AddComponentDialog(
        instrument, model, component_to_edit=component, definitions_dir=DEFINITIONS_DIR
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    assert dialog.fieldsListWidget.model().hasIndex(0, 0)
    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "array dataset"
    assert widget.name == field_name
    assert np.array_equal(widget.value, field_value)


def test_UI_GIVEN_component_with_link_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_target(
    qtbot
):
    component, instrument, model = create_group_with_component(
        "chopper1", "test_component_editing_link_field"
    )

    entry = instrument.nexus.nexus_file["entry"]

    link_name = "link1"
    link = h5py.SoftLink(entry.name)

    component.set_field(link_name, link)

    dialog = AddComponentDialog(
        instrument, model, component_to_edit=component, definitions_dir=DEFINITIONS_DIR
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "link"
    assert widget.name == link_name
    assert widget.value.path == entry.name


def test_UI_GIVEN_component_with_multiple_fields_WHEN_editing_component_THEN_all_fields_appear_in_fields_list_with_correct_values(
    qtbot
):
    component, instrument, model = create_group_with_component(
        "chopper1", "test_component_editing_multiple_fields"
    )

    field_name1 = "array"
    field_value1 = np.array([1, 2, 3, 4, 5])
    component.set_field(field_name1, field_value1)

    field_name2 = "scalar"
    field_value2 = 1
    component.set_field(field_name2, field_value2)

    dialog = AddComponentDialog(
        instrument, model, component_to_edit=component, definitions_dir=DEFINITIONS_DIR
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(1))
    assert widget.field_type_combo.currentText().lower() == "array dataset"
    assert widget.name == field_name1
    assert np.array_equal(widget.value, field_value1)

    widget2 = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget2.field_type_combo.currentText().lower() == "scalar dataset"
    assert widget2.name == field_name2
    assert widget2.value[()] == field_value2


def test_UI_GIVEN_component_with_basic_f142_field_WHEN_editing_component_THEN_topic_and_source_are_correct(
    qtbot
):
    component, instrument, model = create_group_with_component(
        "chopper1", "test_component_editing_f142_stream_field"
    )

    field_name = "stream1"

    file = h5py.File("temp", driver="core", backing_store=False, mode="x")
    stream_group = file.create_group(name=field_name)
    stream_group.attrs["NX_class"] = "NCstream"

    topic = "topic1"
    pvname = "source1"
    pvtype = "double"

    stream_group.create_dataset(
        "writer_module", dtype=h5py.special_dtype(vlen=str), data="f142"
    )
    stream_group.create_dataset("topic", dtype=h5py.special_dtype(vlen=str), data=topic)
    stream_group.create_dataset(
        "source", dtype=h5py.special_dtype(vlen=str), data=pvname
    )
    stream_group.create_dataset("type", dtype=h5py.special_dtype(vlen=str), data=pvtype)

    field_name1 = "stream1"
    component.set_field(field_name1, stream_group)

    dialog = AddComponentDialog(
        instrument, model, component_to_edit=component, definitions_dir=DEFINITIONS_DIR
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    template = QDialog()
    template.ui = dialog
    template.ui.setupUi(template)
    qtbot.addWidget(template)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))

    stream_group = widget.value
    assert stream_group["topic"][()] == topic
    assert stream_group["source"][()] == pvname
    assert stream_group["type"][()] == pvtype

    assert widget.streams_widget.topic_line_edit.text() == topic
    assert widget.streams_widget.schema_combo.currentText() == "f142"
    assert widget.streams_widget.source_line_edit.text() == pvname
    assert widget.streams_widget.type_combo.currentText() == pvtype


def test_UI_GIVEN_component_with_off_shape_WHEN_editing_component_THEN_mesh_shape_radio_is_checked(
    qtbot
):
    instrument = Instrument(NexusWrapper("test_component_editing_off"), DEFINITIONS_DIR)
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
        instrument,
        component_model,
        component_to_edit=component,
        definitions_dir=DEFINITIONS_DIR,
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
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
    instrument = Instrument(
        NexusWrapper("test_component_editing_off_filepath"), DEFINITIONS_DIR
    )
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
        instrument,
        component_model,
        component_to_edit=component,
        definitions_dir=DEFINITIONS_DIR,
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
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


def test_UI_GIVEN_field_widget_with_string_type_THEN_value_property_is_correct(
    qtbot, add_component_dialog, template
):

    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.scalar_dataset.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    field.value_type_combo.setCurrentText("String")
    field.value_type_combo.currentTextChanged.emit(field.value_type_combo.currentText)

    field_name = "testfield"
    field_value = "testvalue"

    field.field_name_edit.setText(field_name)
    field.value_line_edit.setText(field_value)

    assert field.dtype == h5py.special_dtype(vlen=str)

    assert field.name == field_name
    assert field.value[...] == field_value


def test_UI_GIVEN_field_widget_with_stream_type_THEN_stream_dialog_shown(
    qtbot, add_component_dialog, template
):

    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()
    assert field.streams_widget.isEnabled()


def test_UI_GIVEN_field_widget_with_link_THEN_link_target_and_name_is_correct(
    qtbot, add_component_dialog, template
):

    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.link.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    field_name = "testfield"
    field_target = "/somewhere/"

    field.field_name_edit.setText(field_name)
    field.value_line_edit.setText(field_target)

    assert field.dtype == h5py.SoftLink

    assert field.name == field_name
    assert field.value.path == h5py.SoftLink(field_target).path


def test_UI_GIVEN_chopper_properties_WHEN_adding_component_with_no_shape_THEN_chopper_geometry_is_created(
    qtbot, add_component_dialog, template
):

    enter_disk_chopper_fields(qtbot, add_component_dialog, template)

    with patch(
        "nexus_constructor.add_component_window.DiskChopperGeometryCreator"
    ) as chopper_creator:
        add_component_dialog.on_ok()
        chopper_creator.assert_called_once()


def test_UI_GIVEN_chopper_properties_WHEN_adding_component_with_no_shape_THEN_nexus_chopper_creator_is_not_called(
    qtbot, add_component_dialog, template
):
    enter_disk_chopper_fields(qtbot, add_component_dialog, template)

    with patch(
        "nexus_constructor.component.chopper_shape.ChopperShape.get_shape"
    ) as get_shape_from_nexus:
        get_shape_from_nexus.return_value = (NoShapeGeometry(), None)
        add_component_dialog.on_ok()
        get_shape_from_nexus.assert_not_called()


def test_UI_GIVEN_chopper_properties_WHEN_adding_component_with_mesh_shape_THEN_chopper_geometry_is_not_created(
    qtbot, add_component_dialog, template
):

    systematic_button_press(qtbot, template, add_component_dialog.meshRadioButton)
    enter_file_path(
        qtbot,
        add_component_dialog,
        template,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )
    show_and_close_window(qtbot, template)

    enter_disk_chopper_fields(qtbot, add_component_dialog, template)

    with patch(
        "nexus_constructor.add_component_window.DiskChopperGeometryCreator"
    ) as chopper_creator:
        add_component_dialog.on_ok()
        chopper_creator.assert_not_called()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_f142_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget._schema_type_changed("f142")

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()
    assert streams_widget.source_label.isEnabled()
    assert streams_widget.source_line_edit.isEnabled()
    assert streams_widget.type_label.isEnabled()
    assert streams_widget.type_combo.isEnabled()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_ev42_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget._schema_type_changed("ev42")

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()

    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()
    assert not streams_widget.type_label.isVisible()
    assert not streams_widget.type_combo.isVisible()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_ns10_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget._schema_type_changed("ns10")

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()
    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()

    assert not streams_widget.type_label.isVisible()
    assert not streams_widget.type_combo.isVisible()


@pytest.mark.parametrize("test_input", ["TdcTime", "senv"])
def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_THEN_stream_dialog_shown_with_correct_options(
    qtbot, test_input, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget._schema_type_changed(test_input)

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()
    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()

    assert not streams_widget.type_label.isVisible()
    assert not streams_widget.type_combo.isVisible()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_hs00_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget._schema_type_changed("hs00")

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()
    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()

    assert not streams_widget.type_label.isVisible()
    assert not streams_widget.type_combo.isVisible()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_f142_and_type_to_double_THEN_stream_dialog_shown_with_array_size_option(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget.schema_combo.setCurrentText("f142")
    streams_widget.schema_combo.currentTextChanged.emit(
        streams_widget.schema_combo.currentText()
    )

    streams_widget.array_radio.setChecked(True)
    streams_widget.array_radio.clicked.emit()

    assert streams_widget.topic_label.isVisible()
    assert streams_widget.topic_line_edit.isVisible()
    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()
    assert streams_widget.type_label.isVisible()
    assert streams_widget.type_combo.isVisible()

    assert streams_widget.array_size_label.isVisible()
    assert streams_widget.array_size_spinbox.isVisible()


def test_UI_GIVEN_initial_component_THEN_webbrowser_url_contains_component_class(
    qtbot, add_component_dialog, template
):
    current_nx_class = add_component_dialog.componentTypeComboBox.currentText()
    assert current_nx_class in add_component_dialog.webEngineView.url().toString()


def test_UI_GIVEN_change_of_component_type_THEN_webbrowser_url_is_updated_and_contains_component_class(
    qtbot, add_component_dialog, template
):
    current_nx_class = add_component_dialog.componentTypeComboBox.currentText()

    new_nx_class = add_component_dialog.componentTypeComboBox.itemText(3)
    add_component_dialog.componentTypeComboBox.setCurrentIndex(3)

    assert new_nx_class in add_component_dialog.webEngineView.url().toString()
    assert current_nx_class not in add_component_dialog.webEngineView.url().toString()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_f142_THEN_stream_dialog_shown_with_array_size_option_and_correct_value_in_nexus_file(
    qtbot, add_component_dialog, template
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    name = "test"

    field.field_name_edit.setText(name)

    field.field_type_combo.setCurrentText(FieldType.kafka_stream.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    qtbot.mouseClick(field.edit_button, Qt.LeftButton)

    assert field.edit_dialog.isEnabled()

    streams_widget = field.streams_widget
    assert streams_widget.isEnabled()

    streams_widget.schema_combo.setCurrentText("f142")
    streams_widget.schema_combo.currentTextChanged.emit(
        streams_widget.schema_combo.currentText()
    )

    streams_widget.array_radio.setChecked(True)
    streams_widget.array_radio.clicked.emit()

    array_size = 2
    streams_widget.array_size_spinbox.setValue(array_size)

    group = streams_widget.get_stream_group()

    assert "array_size" in group

    assert group["array_size"][()] == array_size


def test_UI_GIVEN_chopper_properties_WHEN_adding_component_with_cylinder_shape_THEN_chopper_geometry_is_not_created(
    qtbot, add_component_dialog, template
):

    systematic_button_press(qtbot, template, add_component_dialog.CylinderRadioButton)
    show_and_close_window(qtbot, template)

    enter_disk_chopper_fields(qtbot, add_component_dialog, template)

    with patch(
        "nexus_constructor.add_component_window.DiskChopperGeometryCreator"
    ) as chopper_creator:
        add_component_dialog.on_ok()
        chopper_creator.assert_not_called()


def test_UI_GIVEN_component_with_pixel_data_WHEN_editing_a_component_THEN_pixel_options_become_visible(
    qtbot, edit_component_dialog, template, mock_pixel_options
):
    show_and_close_window(qtbot, template)
    mock_pixel_options.fill_existing_entries.assert_called_once()


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_grid_WHEN_editing_component_with_grid_THEN_new_pixel_grid_is_written(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    prev_pixel_grid_size = 5
    new_pixel_grid_size = 3

    # Create a component with a pixel grid
    component_name = "ComponentWithGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelGrid(rows=prev_pixel_grid_size, columns=prev_pixel_grid_size),
    )

    # Retrieve the newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelGrid(rows=new_pixel_grid_size, columns=new_pixel_grid_size),
    )

    # Check that the change in pixel data is now stored in the component
    for field in PIXEL_GRID_FIELDS[:-1] + ["detector_number"]:
        assert component_to_edit.get_field(field).shape == (
            new_pixel_grid_size,
            new_pixel_grid_size,
        )

    assert isinstance(component_to_edit.shape[0], expected_geometry)


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_mapping_WHEN_editing_component_with_mapping_THEN_new_pixel_mapping_is_written(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    prev_detector_numbers = [5]
    new_detector_numbers = [6]

    # Create a component with a pixel mapping
    component_name = "ComponentWithMapping"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelMapping(prev_detector_numbers),
    )

    # Retrieve newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelMapping(new_detector_numbers),
    )

    shape = component_to_edit.shape[0]

    # Check that the change in pixel mapping is now stored in the component
    assert component_to_edit.get_field("detector_number") == new_detector_numbers
    assert isinstance(shape, expected_geometry)

    if not cylinders:
        assert shape.detector_faces[1] == new_detector_numbers[0]


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_mapping_WHEN_editing_component_with_pixel_grid_THEN_mapping_replaces_grid(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with a pixel grid
    component_name = "GridToMapping"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelGrid(),
    )

    # Retrieve the newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    detector_number = [3]
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelMapping(detector_number),
    )

    # Check that the pixel grid values no longer exist
    for field in PIXEL_GRID_FIELDS:
        assert component_to_edit.get_field(field) is None

    # Check that the detector numbers field has the information from the Pixel Mapping
    assert component_to_edit.get_field("detector_number") == detector_number

    shape = component_to_edit.shape[0]

    # Check that _shape is a ComponentShape
    assert isinstance(component_to_edit._shape, ComponentShape)
    assert isinstance(shape, expected_geometry)

    if not cylinders:
        assert shape.detector_faces[1] == detector_number[0]


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_no_pixels_WHEN_editing_component_with_pixel_grid_THEN_pixel_grid_is_erased(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with a pixel grid
    component_name = "GridToNoPixels"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelGrid(),
    )

    # Retrieve the newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    edit_component_with_pixel_fields(
        add_component_dialog, component_to_edit, parent_mock, mock_pixel_options, None
    )

    # Check that all pixel data values no longer exist
    for field in PIXEL_FIELDS + ["pixel_shape"]:
        assert component_to_edit.get_field(field) is None

    assert isinstance(component_to_edit.shape[0], expected_geometry)


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_grid_WHEN_editing_component_with_pixel_mapping_THEN_grid_replaces_mapping(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with a pixel mapping
    component_name = "MappingToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelMapping([5]),
    )

    # Retrieve newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    grid_size = 5
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelGrid(rows=grid_size, columns=grid_size),
    )

    # Check that the change in pixel data is now stored in the component
    for field in PIXEL_GRID_FIELDS[:-1] + ["detector_number"]:
        assert component_to_edit.get_field(field).shape == (grid_size, grid_size)

    shape = component_to_edit.shape[0]

    if not cylinders:
        assert shape.detector_faces is None

    # Check that _shape is a PixelShape
    assert isinstance(component_to_edit._shape, PixelShape)
    assert isinstance(shape, expected_geometry)


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_no_pixels_WHEN_editing_component_with_pixel_mapping_THEN_mapping_is_erased(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with a pixel mapping
    component_name = "MappingToNoPixels"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
        PixelMapping([5]),
    )

    # Retrieve newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    edit_component_with_pixel_fields(
        add_component_dialog, component_to_edit, parent_mock, mock_pixel_options, None
    )

    shape = component_to_edit.shape[0]

    # Check that the pixel mapping data has been cleared
    assert component_to_edit.get_field("detector_number") is None
    if not cylinders:
        assert shape.detector_faces is None

    assert isinstance(shape, expected_geometry)


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_grid_WHEN_editing_component_with_no_pixel_data_THEN_pixel_grid_is_created(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with no pixel data
    component_name = "NoPixelsToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
    )

    # Retrieve newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog
    grid_size = 6
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelGrid(rows=grid_size, columns=grid_size),
    )

    # Check that the change in pixel data is now stored in the component
    for field in PIXEL_GRID_FIELDS[:-1] + ["detector_number"]:
        assert component_to_edit.get_field(field).shape == (grid_size, grid_size)

    assert isinstance(component_to_edit.shape[0], expected_geometry)


@pytest.mark.parametrize("cylinders", [True, False])
def test_UI_GIVEN_pixel_mapping_WHEN_editing_component_with_no_pixel_data_THEN_pixel_mapping_is_created(
    qtbot, template, add_component_dialog, mock_pixel_options, parent_mock, cylinders
):
    # Create a component with no pixel data
    component_name = "NoPixelsToMapping"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        cylinders,
        mock_pixel_options,
        qtbot,
        template,
    )

    # Retrieve newly created component
    component_to_edit = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    # Make the Add Component dialog behave like an Edit Component dialog and create a pixel mapping
    detector_number = [4]
    edit_component_with_pixel_fields(
        add_component_dialog,
        component_to_edit,
        parent_mock,
        mock_pixel_options,
        PixelMapping(detector_number),
    )

    shape = component_to_edit.shape[0]

    # Check that the change in pixel data is now stored in the component
    assert component_to_edit.get_field("detector_number") == detector_number
    if not cylinders:
        assert shape.detector_faces[1] == detector_number[0]

    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_changing_fields_WHEN_editing_a_component_with_a_chopper_mesh_THEN_previous_chopper_mesh_is_removed_from_instrument_view(
    qtbot, template, add_component_dialog, parent_mock
):

    component_name = "DiskChopper"
    enter_disk_chopper_fields(qtbot, add_component_dialog, template, component_name)
    add_component_dialog.on_ok()

    disk_chopper_component = get_new_component_from_dialog(
        add_component_dialog, component_name
    )

    add_component_dialog.component_to_edit = disk_chopper_component
    add_component_dialog.parent = Mock(return_value=parent_mock)

    widget = None
    for i in range(4):
        widget = add_component_dialog.fieldsListWidget.itemWidget(
            add_component_dialog.fieldsListWidget.item(i)
        )
        if widget.name == "radius":
            break

    assert widget is not None
    prev_value = widget.value[()]
    widget.value = prev_value + 50

    add_component_dialog.on_ok()

    parent_mock.sceneWidget.delete_component.assert_called_once_with(component_name)
