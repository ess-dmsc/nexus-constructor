import os

import h5py
import numpy as np
import PySide2
import pytest
import pytestqt
from mock import Mock, call, mock_open, patch
from PySide2.QtCore import Qt
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QMainWindow, QRadioButton
from pytestqt.qtbot import QtBot

from nexus_constructor import component_type
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.component_tree_model import NexusTreeModel as ComponentTreeModel
from nexus_constructor.geometry.pixel_data import PixelData, PixelGrid, PixelMapping
from nexus_constructor.instrument_view.instrument_view import InstrumentView
from nexus_constructor.main_window import MainWindow
from nexus_constructor.widgets import CustomDialog as QDialog
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.geometry import (
    CylindricalGeometry,
    OFFGeometryNexus,
    OFFGeometryNoNexus,
)
from nexus_constructor.model.group import Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import F142Stream, Link
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP, ValueTypes
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.validators import FieldType, PixelValidator
from tests.test_utils import NX_CLASS_DEFINITIONS
from tests.ui_tests.ui_test_utils import (
    RED_LINE_EDIT_STYLE_SHEET,
    VALID_CUBE_OFF_FILE,
    VALID_OCTA_OFF_FILE,
    WHITE_LINE_EDIT_STYLE_SHEET,
    show_and_close_window,
    systematic_button_press,
)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
WRONG_EXTENSION_FILE_PATH = os.path.join(BASE_PATH, "..", "..", "requirements.txt")
NONEXISTENT_FILE_PATH = "doesntexist.off"
VALID_CUBE_MESH_FILE_PATH = os.path.join(BASE_PATH, "..", "cube.off")
VALID_OCTA_MESH_FILE_PATH = os.path.join(BASE_PATH, "..", "octa.off")

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

COMPONENT_CLASS_PATH = "nexus_constructor.add_component_window.Component"
CHOPPER_GEOMETRY_CREATOR_PATH = "nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator.DiskChopperGeometryCreator.create_disk_chopper_geometry"

model = Model()
component = ComponentTreeModel(model)
entry = Entry()
group = Group(name="some_name", parent_node=entry)
entry.children.append(group)

PIXEL_OPTIONS = dict()
NO_PIXEL_OPTIONS = dict()
ALL_COMPONENT_TYPES = dict()

for i, component_class in enumerate(
    list(
        AddComponentDialog(
            None, model, component, group_to_edit=group, initial_edit=False, nx_classes=NX_CLASS_DEFINITIONS, scene_widget=None
        ).nx_component_classes.keys()
    )
):

    ALL_COMPONENT_TYPES[component_class] = i

    if component_class in component_type.PIXEL_COMPONENT_TYPES:
        PIXEL_OPTIONS[component_class] = i
    else:
        NO_PIXEL_OPTIONS[component_class] = i

# Select a subset of the component class to use in parameterised tests.
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

FIELDS_VALUE_TYPES = {key: i for i, key in enumerate(VALUE_TYPE_TO_NP)}
FIELD_TYPES = {item.value: i for i, item in enumerate(FieldType)}


def get_component_combobox_index(
    add_component_dialog: AddComponentDialog, nx_class: str
):
    all_items = [
        add_component_dialog.componentTypeComboBox.itemText(i)
        for i in range(add_component_dialog.componentTypeComboBox.count())
    ]
    for i, item in enumerate(all_items):
        if item == nx_class:
            return i


@pytest.fixture(scope="function")
def parent_mock():

    parent_mock = Mock(spec=MainWindow)
    parent_mock.sceneWidget = Mock(spec=InstrumentView)
    return parent_mock


@pytest.fixture(scope="function")
def instrument():
    return Model()


@pytest.fixture(scope="function")
def add_component_dialog(qtbot, model, mock_pixel_options):
    entry = Entry()
    group = Group(name="some_name", parent_node=entry)
    entry.children.append(group)

    dialog = AddComponentDialog(None, model=model, component_model=ComponentTreeModel(model), nx_classes=NX_CLASS_DEFINITIONS, group_to_edit=group, scene_widget=None, initial_edit=False)
    qtbot.addWidget(dialog)

    return dialog


@pytest.fixture(scope="function")
def component_with_cylindrical_geometry():
    component = Component(name="cylindrical_component")
    component.nx_class = "NXdetector"
    component.set_cylinder_shape()
    return component


@pytest.fixture(scope="function")
def edit_component_dialog(
    qtbot,
    model,
    component_with_cylindrical_geometry,
    mock_pixel_options,
    parent_mock,
):
    component_tree = ComponentTreeModel(model)
    dialog = AddComponentDialog(None,
        model=model,
        component_model=component_tree,
        group_to_edit=component_with_cylindrical_geometry,
        scene_widget=None,
        initial_edit=False,
        nx_classes=NX_CLASS_DEFINITIONS,
    )
    qtbot.addWidget(dialog)

    dialog.parent = Mock(return_value=parent_mock)

    return dialog


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
    mock_component.name = "Mock name"
    yield mock_component
    nexus_file.close()


def enter_component_name(
    qtbot: pytestqt.qtbot.QtBot,
    template: QDialog,
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
    show_and_close_window(qtbot, dialog)


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
    template: QDialog,
    component_index: int,
):
    """
    Create the conditions to allow the disappearance of the pixel options by pressing the NoShape button.
    :param qtbot: The qtbot testing tool.
    :param dialog: An instance of an AddComponentDialog.
    :param template: The window/widget that holds the AddComponentDialog.
    :param component_index: The index of a component type.
    """
    systematic_button_press(qtbot, dialog, dialog.noShapeRadioButton)
    dialog.componentTypeComboBox.setCurrentIndex(component_index)
    show_and_close_window(qtbot, dialog)


def make_pixel_options_appear(
    qtbot: pytestqt.qtbot.QtBot,
    button: QRadioButton,
    dialog: AddComponentDialog,
    template: QDialog,
    pixel_options_index: int = None,
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
    if not pixel_options_index:
        pixel_options_index = get_component_combobox_index(dialog, "NXdetector")
    systematic_button_press(qtbot, dialog, button)
    dialog.componentTypeComboBox.setCurrentIndex(pixel_options_index)
    show_and_close_window(qtbot, dialog)


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
            systematic_button_press(qtbot, dialog, dialog.fileBrowseButton)


def enter_disk_chopper_fields(
    qtbot: pytestqt.qtbot.QtBot,
    dialog: AddComponentDialog,
    template: QDialog,
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
        systematic_button_press(qtbot, add_component_dialog, dialog.addFieldPushButton)
    fields_widgets = [
        dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(i))
        for i in range(4)
    ]

    # Enter the field names
    qtbot.keyClicks(fields_widgets[0].field_name_edit, "slits")
    qtbot.keyClicks(fields_widgets[1].field_name_edit, "slit_edges")
    qtbot.keyClicks(fields_widgets[2].field_name_edit, "radius")
    qtbot.keyClicks(fields_widgets[3].field_name_edit, "slit_height")

    show_and_close_window(qtbot, add_component_dialog)

    # Set slits field type
    fields_widgets[0].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["int32"])
    # Set slit edges field type
    fields_widgets[1].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["float"])
    # Set radius field type
    fields_widgets[2].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["float"])
    # Set slit height field type
    fields_widgets[3].value_type_combo.setCurrentIndex(FIELDS_VALUE_TYPES["float"])

    show_and_close_window(qtbot, add_component_dialog)

    # Make the angles field an array type
    fields_widgets[1].field_type_combo.setCurrentIndex(
        FIELD_TYPES[FieldType.array_dataset.value]
    )

    show_and_close_window(qtbot, add_component_dialog)

    # Enter the field values
    qtbot.keyClicks(fields_widgets[0].value_line_edit, "6")
    qtbot.keyClicks(fields_widgets[2].value_line_edit, "200")
    qtbot.keyClicks(fields_widgets[3].value_line_edit, "100")

    # Manually edit the angles array
    fields_widgets[1].table_view.model.array = np.array(
        [[(i * 10.0)] for i in range(12)]
    ).astype(np.single)

    # Set the units attributes
    qtbot.keyClicks(fields_widgets[1].units_line_edit, "deg")  # Slit edges
    qtbot.keyClicks(fields_widgets[2].units_line_edit, "mm")  # Radius
    qtbot.keyClicks(fields_widgets[3].units_line_edit, "mm")  # Slit height

    show_and_close_window(qtbot, add_component_dialog)


def get_new_component_from_dialog(dialog: AddComponentDialog, name: str) -> Component:
    """
    Get the stored component from an AddComponentDialog after the "Add Component" button has been pressed.
    :param dialog: The AddComponentDialog.
    :param name: The name of the component that is being searched for.
    :return: The component.
    """
    for component in dialog.model.get_components():
        if component.name == name:
            return component


def enter_component_with_pixel_fields(
    add_component_dialog: AddComponentDialog,
    button: QRadioButton,
    component_name: str,
    mock_pixel_options: Mock,
    qtbot: pytestqt.qtbot.QtBot,
    pixel_data: PixelData,
):
    """
    Mimics the user entering a component with pixel data by having the pixel options appear and then instructing it to
    return pixel data.
    :param add_component_dialog: The AddComponentDialog.
    :param button: The shape type button that is pressed in order to make the PixelOptions appear. Can be either mesh or
        cylinder.
    :param component_name: The component name.
    :param mock_pixel_options: A mock of the PixelOptions widget that returns fake pixel data when the OK button is
        pressed.
    :param qtbot: The QtBot testing tool.
    :param template: The window/widget that holds the AddComponentDialog.
    :param pixel_data: The pixel data that is returned by the mock PixelOptions.
    """
    make_pixel_options_appear(qtbot, button, add_component_dialog, add_component_dialog)
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, component_name)
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
    Mimics the user entering the details of a component with pixel data and pressing OK.
    :param add_component_dialog: The AddComponentDialog.
    :param component_name: The component name.
    :param cylinders: A bool indicating whether the component has a Cylinder or a Mesh shape.
    :param mock_pixel_options: A mock of the PixelOptions object.
    :param qtbot: The QtBot testing tool.
    :param template: The widget/window that contains the AddComponentDialog.
    :param pixel_data: The mock pixel data that is returned when the OK button is pressed.
    :return The expected geometry type of the new component.
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
        pixel_data,
    )
    if not cylinders:
        enter_file_path(
            qtbot,
            add_component_dialog,
            VALID_CUBE_MESH_FILE_PATH,
            VALID_CUBE_OFF_FILE,
        )
    add_component_dialog.on_ok()
    return expected_geometry


def edit_component_with_pixel_fields(
    add_component_dialog: AddComponentDialog,
    component_to_edit: Component,
    parent_mock: Mock,
    mock_pixel_options: Mock,
    new_pixel_data: PixelData = None,
):
    """
    Mimics a user editing the pixel data of an existing component and pressing OK.
    :param add_component_dialog: The AddComponentDialog.
    :param component_to_edit: The component to edit.
    :param parent_mock: A mock of the AddComponentDialog parent. Required only when editing components.
    :param mock_pixel_options: A mock of the PixelOptions object.
    :param new_pixel_data: The new pixel data that will be generated when the OK button is pressed. None is used when
        testing the scenario in which a user removes the existing pixel data.
    """
    # Give the AddComponentDialog a component_to_edit value so it behaves like an Edit Component window
    add_component_dialog.component_to_edit = component_to_edit
    add_component_dialog.parent = Mock(return_value=parent_mock)

    # Instruct the pixel options mock to generate different pixel data
    mock_pixel_options.generate_pixel_data = Mock(return_value=new_pixel_data)

    add_component_dialog.on_ok()


@pytest.mark.skip(reason="This test causes seg faults at the moment.")
def test_UI_GIVEN_nothing_WHEN_clicking_add_component_button_THEN_add_component_window_is_shown(
    qtbot,
):

    template = QMainWindow()
    # window = MainWindow(Instrument(NexusWrapper("test")))
    # Disabled whilst working on model change
    window = None
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
    qtbot, add_component_dialog
):
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.noShapeRadioButton)
    assert not add_component_dialog.shapeOptionsBox.isVisible()


@pytest.mark.parametrize("shape_button_name", SHAPE_TYPE_BUTTONS)
def test_UI_GIVEN_nothing_WHEN_changing_component_shape_type_THEN_add_component_button_is_always_disabled(
    qtbot, add_component_dialog, shape_button_name
):
    systematic_button_press(
        qtbot, add_component_dialog, get_shape_type_button(add_component_dialog, shape_button_name)
    )

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_nothing_WHEN_selecting_cylinder_type_THEN_relevant_fields_are_shown(
    qtbot, add_component_dialog
):
    # Click on the cylinder shape button
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    # Check that this has caused the relevant fields to become visible
    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.cylinderOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()

    # Check that the file input isn't visible as this is only available for the mesh
    assert not add_component_dialog.geometryFileBox.isVisible()
    # Check that the pixel grid options aren't visible as this is only available for certain NXclasses
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


def test_UI_GIVEN_nothing_WHEN_selecting_mesh_shape_THEN_relevant_fields_are_shown(
    qtbot, add_component_dialog
):
    # Click on the mesh shape button
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

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
    qtbot, add_component_dialog, shape_with_units
):
    # Click on the button of a shape type with units
    systematic_button_press(
        qtbot, add_component_dialog, get_shape_type_button(add_component_dialog, shape_with_units)
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
    get_component_combobox_index(add_component_dialog, pixels_class)
    # Change the pixel options to visible by selecting a cylinder/mesh shape and a NXclass with pixel fields
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(add_component_dialog, pixel_shape_name),
        add_component_dialog,
        add_component_dialog,
        get_component_combobox_index(add_component_dialog, pixels_class),
    )
    # Check that this has caused the pixel options to become visible
    assert add_component_dialog.pixelOptionsWidget.isVisible()


@pytest.mark.parametrize("any_component_type", COMPONENT_TYPES_SUBSET.keys())
def test_UI_GIVEN_any_nxclass_WHEN_adding_component_with_no_shape_THEN_pixel_options_go_from_visible_to_invisible(
    qtbot, add_component_dialog, any_component_type
):
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    # Change the pixel options to invisible
    make_pixel_options_disappear(
        qtbot, add_component_dialog, add_component_dialog, ALL_COMPONENT_TYPES[any_component_type]
    )
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


@pytest.mark.parametrize("no_pixels_class", NO_PIXEL_OPTIONS_SUBSET.keys())
@pytest.mark.parametrize("pixels_class", PIXEL_OPTIONS.keys())
@pytest.mark.parametrize("shape_name", SHAPE_TYPE_BUTTONS[1:])
def test_UI_GIVEN_class_without_pixel_fields_WHEN_selecting_nxclass_for_component_with_mesh_or_cylinder_shape_THEN_pixel_options_becomes_invisible(
    qtbot, add_component_dialog, no_pixels_class, pixels_class, shape_name
):
    # Make the pixel options become visible
    make_pixel_options_appear(
        qtbot,
        get_shape_type_button(add_component_dialog, shape_name),
        add_component_dialog,
        add_component_dialog,
        get_component_combobox_index(add_component_dialog, pixels_class),
    )
    assert add_component_dialog.pixelOptionsWidget.isVisible()

    # Change nxclass to one without pixel fields and check that the pixel options have become invisible again
    add_component_dialog.componentTypeComboBox.setCurrentIndex(
        NO_PIXEL_OPTIONS[no_pixels_class]
    )
    assert not add_component_dialog.pixelOptionsWidget.isVisible()


def test_UI_GIVEN_user_changes_shape_WHEN_adding_component_THEN_validity_is_reassessed(
    qtbot, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)
    mock_pixel_options.update_pixel_input_validity.assert_called_once()
    mock_pixel_options.reset_mock()

    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)
    mock_pixel_options.update_pixel_input_validity.assert_called_once()


def test_UI_GIVEN_cylinder_shape_WHEN_user_chooses_pixel_mapping_THEN_pixel_mapping_list_is_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, add_component_dialog
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
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
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, add_component_dialog
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
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Provide the same file as before
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the method for populating the pixel mapping was only called once even though a file was selected twice
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_called_once_with(
        VALID_CUBE_MESH_FILE_PATH
    )


def test_UI_GIVEN_pixel_options_are_not_visible_WHEN_giving_mesh_file_THEN_mapping_list_is_not_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_pixel_options_are_not_visible_WHEN_changing_cylinder_count_THEN_mapping_list_is_not_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    qtbot.keyClick(add_component_dialog.cylinderCountSpinBox, Qt.Key_Up)

    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_not_called()


def test_UI_GIVEN_invalid_file_WHEN_giving_mesh_file_THEN_mapping_list_is_not_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    enter_file_path(qtbot, add_component_dialog, VALID_CUBE_OFF_FILE, "OFF")

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_different_mesh_file_WHEN_user_selects_face_mapped_mesh_THEN_mapping_list_changes(
    qtbot, add_component_dialog, mock_pixel_options
):
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    # Provide a path and file for a cube mesh
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Provide a path and file for an octahedron mesh
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_OCTA_MESH_FILE_PATH,
        VALID_OCTA_OFF_FILE,
    )

    # Check that two different files being given means the method was called twice
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_has_calls(
        [call(VALID_CUBE_MESH_FILE_PATH), call(VALID_OCTA_MESH_FILE_PATH)]
    )


def test_UI_GIVEN_valid_name_WHEN_choosing_component_name_THEN_background_becomes_white(
    qtbot, add_component_dialog
):
    # Check that the background color of the ext field starts as red
    assert add_component_dialog.nameLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET

    # Mimic the user entering a name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Check that the background color of the test field has changed to white
    assert add_component_dialog.nameLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_window_closes(
    qtbot, add_component_dialog
):

    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.ok_button, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not add_component_dialog.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_mesh_shape_THEN_add_component_window_closes(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user entering valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.ok_button, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not add_component_dialog.isVisible()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_cylinder_shape_THEN_add_component_window_closes(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    # Mimic the user pressing the Add Component button
    qtbot.mouseClick(add_component_dialog.ok_button, Qt.LeftButton)

    # The window will close because the input is valid and the button is enabled
    assert not add_component_dialog.isVisible()


def test_UI_GIVEN_no_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # The Add Component button is disabled because no input was given
    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_valid_input_WHEN_adding_component_with_no_shape_THEN_add_component_button_is_enabled(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # The Add Component button is enabled because all the information required to create a no shape component is
    # there
    assert add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # No file name was given so we expect the file input box background to be red
    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_file_that_doesnt_exist_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user entering a bad file path
    enter_file_path(qtbot, add_component_dialog, NONEXISTENT_FILE_PATH, "OFF")

    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_red_background(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving the path for a file that exists but has the wrong extension
    enter_file_path(
        qtbot, add_component_dialog, WRONG_EXTENSION_FILE_PATH, "OFF"
    )

    assert add_component_dialog.fileLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_file_path_box_has_white_background(
    qtbot, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # The file input box should now have a white background
    assert add_component_dialog.fileLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_no_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):
    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user entering a unique name in the text field
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Although the component name is valid, no file path has been given so the button should be disabled
    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_nonexistent_file_path_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a nonexistent file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        NONEXISTENT_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_file_with_wrong_extension_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a path for a file that exists but has the wrong extension
    enter_file_path(
        qtbot,
        add_component_dialog,
        WRONG_EXTENSION_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user clearing the unit input box
    enter_units(qtbot, add_component_dialog, "")

    assert add_component_dialog.unitsLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_red_background(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert add_component_dialog.unitsLineEdit.styleSheet() == RED_LINE_EDIT_STYLE_SHEET


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_units_box_has_white_background(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the replacing the default value with "km"
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    assert (
        add_component_dialog.unitsLineEdit.styleSheet() == WHITE_LINE_EDIT_STYLE_SHEET
    )


def test_UI_GIVEN_valid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_enabled(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user giving valid units
    enter_units(qtbot, add_component_dialog, VALID_UNITS)

    assert add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_no_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user clearing the units box
    enter_units(qtbot, add_component_dialog, "")

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_mesh_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user giving a valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user entering a valid file name
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_invalid_units_WHEN_adding_component_with_cylinder_shape_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    # Mimic the user giving valid component name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Mimic the user giving invalid units input
    enter_units(qtbot, add_component_dialog, INVALID_UNITS)

    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_mesh_shape_selected_WHEN_choosing_shape_THEN_relevant_fields_are_visible(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()
    assert add_component_dialog.geometryFileBox.isVisible()

    assert not add_component_dialog.cylinderOptionsBox.isVisible()


def test_UI_GIVEN_cylinder_shape_selected_WHEN_choosing_shape_THEN_relevant_fields_are_visible(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    assert add_component_dialog.shapeOptionsBox.isVisible()
    assert add_component_dialog.unitsbox.isVisible()
    assert add_component_dialog.cylinderOptionsBox.isVisible()

    assert not add_component_dialog.geometryFileBox.isVisible()


@pytest.mark.parametrize("no_pixels_class", NO_PIXEL_OPTIONS_SUBSET.keys())
def test_UI_GIVEN_file_chosen_WHEN_pixel_mapping_options_not_visible_THEN_pixel_mapping_list_remains_empty(
    qtbot, add_component_dialog, no_pixels_class, mock_pixel_options
):

    # Mimic the user selecting a mesh shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.meshRadioButton)

    # Mimic the user selecting a component type that doesn't have pixel fields
    add_component_dialog.componentTypeComboBox.setCurrentIndex(
        NO_PIXEL_OPTIONS[no_pixels_class]
    )

    # Mimic the user giving a valid mesh file
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the pixel mapping list is still empty
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_invalid_off_file_WHEN_creating_pixel_mapping_THEN_pixel_mapping_widget_isnt_populated(
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    # Give an invalid file
    enter_file_path(
        qtbot, add_component_dialog, VALID_CUBE_MESH_FILE_PATH, "hfhuihfiuhf"
    )

    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_not_called()


def test_UI_GIVEN_cylinder_shape_selected_WHEN_adding_component_THEN_default_values_are_correct(
    qtbot, add_component_dialog
):

    # Mimic the user selecting a cylinder shape
    systematic_button_press(qtbot, add_component_dialog, add_component_dialog.CylinderRadioButton)

    assert add_component_dialog.cylinderOptionsBox.isVisible()
    assert add_component_dialog.cylinderHeightLineEdit.value() == 0.0
    assert add_component_dialog.cylinderRadiusLineEdit.value() == 0.0
    assert add_component_dialog.cylinderXLineEdit.value() == 0.0
    assert add_component_dialog.cylinderYLineEdit.value() == 0.0
    assert add_component_dialog.cylinderZLineEdit.value() == 1.0


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_is_shown(
    qtbot, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(1)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.edit_dialog.isEnabled()


def test_UI_GIVEN_array_field_selected_and_edit_button_pressed_THEN_edit_dialog_table_is_shown(
    qtbot, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(1)
    field.field_type_changed()

    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.table_view.isEnabled()


def test_UI_GIVEN_stream_field_selected_and_edit_button_pressed_THEN_edit_dialog_is_shown(
    qtbot, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(2)
    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.edit_dialog.isEnabled()


def test_UI_GIVEN_stream_field_selected_and_edit_button_pressed_THEN_edit_dialog_stream_widget_is_shown(
    qtbot, add_component_dialog
):
    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )
    field.field_type_combo.setCurrentIndex(2)
    field.field_type_changed()

    qtbot.addWidget(field)
    qtbot.mouseClick(field.edit_button, Qt.LeftButton)
    assert field.streams_widget.isEnabled()


def test_UI_GIVEN_user_provides_valid_pixel_configuration_WHEN_entering_pixel_data_THEN_add_component_button_is_enabled(
    qtbot, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking valid pixel info was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[False, False])

    # Enter a valid name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is enabled
    assert add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_user_provides_invalid_pixel_grid_WHEN_entering_pixel_data_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking an invalid Pixel Grid was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[True, False])

    # Enter a valid name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is disabled despite the valid name and file path
    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_user_provides_invalid_pixel_mapping_WHEN_entering_pixel_data_THEN_add_component_button_is_disabled(
    qtbot, add_component_dialog, mock_pixel_validator
):

    # Deceive the AddComponentDialog into thinking an invalid Pixel Mapping was given
    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )
    mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[False, True])

    # Enter a valid name
    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    # Enter a valid file path
    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    # Check that the add component button is disabled despite the valid name and file path
    assert not add_component_dialog.ok_button.isEnabled()


def test_UI_GIVEN_user_presses_cylinder_button_WHEN_mesh_pixel_mapping_list_has_been_generated_THEN_new_pixel_mapping_list_is_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    mock_pixel_options.reset_mock()

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, add_component_dialog
    )

    mock_pixel_options.reset_pixel_mapping_table.assert_called_once()
    mock_pixel_options.populate_pixel_mapping_list_with_cylinder_number.assert_called_once_with(
        1
    )


def test_UI_GIVEN_user_presses_mesh_button_WHEN_cylinder_pixel_mapping_list_has_been_generated_WHEN_new_pixel_mapping_list_is_generated(
    qtbot, add_component_dialog, mock_pixel_options
):

    make_pixel_options_appear(
        qtbot, add_component_dialog.CylinderRadioButton, add_component_dialog, add_component_dialog
    )

    mock_pixel_options.reset_mock()

    make_pixel_options_appear(
        qtbot, add_component_dialog.meshRadioButton, add_component_dialog, add_component_dialog
    )

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.reset_pixel_mapping_table.assert_called_once()
    mock_pixel_options.populate_pixel_mapping_list_with_mesh.assert_called_once_with(
        VALID_CUBE_MESH_FILE_PATH
    )


@pytest.mark.skip(reason="invalid type with mock component")
def test_UI_GIVEN_pixel_grid_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_is_stored_in_component(
    qtbot, add_component_dialog, mock_pixel_options, mock_component
):

    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        add_component_dialog,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    pixel_grid = PixelGrid()
    mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_grid)
    show_and_close_window(qtbot, add_component_dialog)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        COMPONENT_CLASS_PATH,
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_grid.assert_called_once_with(pixel_grid)
        mock_component.record_pixel_mapping.assert_not_called()


@pytest.mark.skip(reason="invalid type with mock component")
def test_UI_GIVEN_pixel_mapping_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_is_stored_in_component(
    qtbot, add_component_dialog, mock_pixel_options, mock_component
):

    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        add_component_dialog,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    pixel_mapping = PixelMapping(pixel_ids=[1])
    mock_pixel_options.generate_pixel_data = Mock(return_value=pixel_mapping)
    show_and_close_window(qtbot, add_component_dialog)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        COMPONENT_CLASS_PATH,
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_mapping.assert_called_once_with(pixel_mapping)
        mock_component.record_pixel_grid.assert_not_called()


@pytest.mark.skip(reason="invalid type with mock component")
def test_UI_GIVEN_no_pixel_data_is_entered_WHEN_adding_nxdetector_THEN_pixel_data_writing_methods_are_not_called(
    qtbot, add_component_dialog, mock_pixel_options, mock_component
):
    make_pixel_options_appear(
        qtbot,
        add_component_dialog.meshRadioButton,
        add_component_dialog,
        add_component_dialog,
        PIXEL_OPTIONS["NXdetector"],
    )

    enter_component_name(qtbot, add_component_dialog, add_component_dialog, UNIQUE_COMPONENT_NAME)

    enter_file_path(
        qtbot,
        add_component_dialog,
        VALID_CUBE_MESH_FILE_PATH,
        VALID_CUBE_OFF_FILE,
    )

    mock_pixel_options.generate_pixel_data = Mock(return_value=None)
    show_and_close_window(qtbot, add_component_dialog)

    # Call the on_ok method as if the user had pressed Add Component
    with patch(
        COMPONENT_CLASS_PATH,
        return_value=mock_component,
    ):
        add_component_dialog.on_ok()
        mock_component.record_pixel_mapping.assert_not_called()
        mock_component.record_pixel_grid.assert_not_called()


def test_UI_GIVEN_component_name_and_description_WHEN_editing_component_THEN_correct_values_are_loaded_into_UI(
    qtbot,
    model,
):
    component_model = ComponentTreeModel(model)

    name = "test"
    nx_class = "NXmonitor"
    desc = "description"

    component = Component(name)
    component.nx_class = nx_class
    component.description = desc

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                model=model,
                component_model=component_model,
                group_to_edit=component,
                nx_classes=NX_CLASS_DEFINITIONS,
                parent=None,
                scene_widget=None,
                initial_edit=False
            )

            qtbot.addWidget(dialog)

            assert dialog.nameLineEdit.text() == name
            assert dialog.descriptionPlainTextEdit.text() == desc
            assert dialog.componentTypeComboBox.currentText() == nx_class


def test_UI_GIVEN_component_with_no_shape_WHEN_editing_component_THEN_no_shape_radio_is_checked(
    qtbot,
):
    component, instrument, treeview_model = create_group_with_component(
        "test", "test_component_editing_no_shape"
    )

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                model=model,
                component_model=treeview_model,
                group_to_edit=component,
                nx_classes=NX_CLASS_DEFINITIONS,
                parent=None,
                scene_widget=None,
                initial_edit=False
            )
            qtbot.addWidget(dialog)

            assert dialog.noShapeRadioButton.isChecked()


def test_UI_GIVEN_component_with_cylinder_shape_WHEN_editing_component_THEN_cylinder_shape_radio_is_checked(
    qtbot,
    model,
):
    component_model = ComponentTreeModel(model)

    component_name = "test"
    component = Component(component_name)
    component.nx_class = "NXpinhole"

    component.set_cylinder_shape(QVector3D(1, 1, 1), height=3, radius=4)

    with patch("nexus_constructor.validators.PixelValidator") as mock_pixel_validator:
        mock_pixel_validator.unacceptable_pixel_states = Mock(return_value=[])
        with patch(
            "nexus_constructor.add_component_window.PixelOptions"
        ) as mock_pixel_options:
            mock_pixel_options.pixel_validator = mock_pixel_validator
            dialog = AddComponentDialog(
                model=model,
                component_model=component_model,
                group_to_edit=component,
                nx_classes=NX_CLASS_DEFINITIONS,
                parent=None,
                scene_widget=None,
                initial_edit=False
            )
            dialog.pixel_options = Mock(spec=PixelOptions)
            qtbot.addWidget(dialog)

            assert dialog.CylinderRadioButton.isChecked()
            assert dialog.cylinderOptionsBox.isEnabled()


def test_UI_GIVEN_component_with_scalar_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_value(
    qtbot,
):

    component, model, treeview_model = create_group_with_component(
        "chopper1", "test_component_editing_scalar_field"
    )

    field_name = "scalar"
    field_value = "test"
    component.set_field_value(field_name, field_value, dtype=ValueTypes.STRING)

    dialog = AddComponentDialog(
        model=model,
        component_model=treeview_model,
        group_to_edit=component,
        nx_classes=NX_CLASS_DEFINITIONS,
        parent=None,
        scene_widget=None,
        initial_edit=False
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    assert dialog.fieldsListWidget.model().hasIndex(0, 0)
    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "scalar dataset"

    assert widget.name == field_name
    assert widget.value.values == field_value


def create_group_with_component(component_name: str, file_name: str):
    """
    Convenience method, for when we don't really care about the component and just want one to be added to a file
    """
    model = Model()
    treeview_model = ComponentTreeModel(model)
    component = Component(component_name)
    component.nx_class = "NXdisk_chopper"
    return component, model, treeview_model


def test_UI_GIVEN_component_with_array_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_value(
    qtbot,
):
    component, model, treeview_model = create_group_with_component(
        "chopper1", "test_component_editing_array_field"
    )

    field_name = "array"
    field_value = np.array([1, 2, 3, 4, 5])
    component.set_field_value(field_name, field_value, ValueTypes.INT)
    units = "m"
    component[field_name].attributes.set_attribute_value(CommonAttrs.UNITS, units)
    dialog = AddComponentDialog(
        model=model,
        component_model=treeview_model,
        group_to_edit=component,
        nx_classes=NX_CLASS_DEFINITIONS,
        parent=None,
        scene_widget=None,
        initial_edit=False
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    assert dialog.fieldsListWidget.model().hasIndex(0, 0)
    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "array dataset"
    assert widget.name == field_name
    assert np.array_equal(widget.value.values, field_value)
    assert widget.units_line_edit.text() == units


def test_UI_GIVEN_component_with_link_field_WHEN_editing_component_THEN_field_appears_in_fields_list_with_correct_target(
    qtbot,
):
    component, model, treeview_model = create_group_with_component(
        "chopper1", "test_component_editing_link_field"
    )

    entry = Entry()
    link_name = "link1"
    link = Link(parent_node=entry, name=link_name, source=entry.name)

    component[link_name] = link

    dialog = AddComponentDialog(
        model=model,
        component_model=treeview_model,
        group_to_edit=component,
        nx_classes=NX_CLASS_DEFINITIONS,
        parent=None,
        scene_widget=None,
        initial_edit=False
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "link"
    assert widget.value.name == link_name
    assert widget.value.source == entry.name


def test_UI_GIVEN_component_with_multiple_fields_WHEN_editing_component_THEN_all_fields_appear_in_fields_list_with_correct_values(
    qtbot,
):
    component, model, treeview_model = create_group_with_component(
        "chopper1", "test_component_editing_multiple_fields"
    )

    field_name1 = "array"
    field_value1 = np.array([1, 2, 3, 4, 5])
    component.set_field_value(field_name1, field_value1, ValueTypes.INT)

    field_name2 = "scalar"
    field_value2 = 1
    component.set_field_value(field_name2, field_value2, ValueTypes.INT)

    dialog = AddComponentDialog(
        model=model,
        component_model=treeview_model,
        group_to_edit=component,
        nx_classes=NX_CLASS_DEFINITIONS,
        parent=None,
        scene_widget=None,
        initial_edit=False
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))
    assert widget.field_type_combo.currentText().lower() == "array dataset"
    assert widget.name == field_name1
    assert np.array_equal(widget.value.values, field_value1)

    widget2 = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(1))
    assert widget2.field_type_combo.currentText().lower() == "scalar dataset"
    assert widget2.name == field_name2
    assert widget2.value.values == str(field_value2)


def test_UI_GIVEN_group_with_basic_f142_field_WHEN_editing_component_THEN_topic_and_source_are_correct(
    qtbot,
):
    component, model, treeview_model = create_group_with_component(
        "chopper1", "test_component_editing_f142_stream_field"
    )

    field_name = "stream1"
    stream_group = Group(field_name)

    topic = "topic1"
    pvname = "source1"
    pvtype = "double"

    stream = F142Stream(
        parent_node=stream_group, topic=topic, source=pvname, type=pvtype
    )

    stream_group.children.append(stream)

    dialog = AddComponentDialog(
        model=model,
        component_model=treeview_model,
        group_to_edit=stream_group,
        nx_classes=NX_CLASS_DEFINITIONS,
        parent=None,
        scene_widget=None,
        initial_edit=False
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    widget = dialog.fieldsListWidget.itemWidget(dialog.fieldsListWidget.item(0))

    stream = widget.value
    assert stream.topic == topic
    assert stream.source == pvname
    assert stream.type == pvtype

    assert widget.streams_widget.topic_line_edit.text() == topic
    assert widget.streams_widget.schema_combo.currentText() == "f142"
    assert widget.streams_widget.source_line_edit.text() == pvname
    assert widget.streams_widget.type_combo.currentText() == pvtype


def test_UI_GIVEN_component_with_off_shape_WHEN_editing_component_THEN_mesh_shape_radio_is_checked(
    qtbot,
    model,
):
    component_model = ComponentTreeModel(model)

    component_name = "test"
    entry = Entry()
    component = Component(parent_node=entry, name=component_name)
    entry.children.append(component)
    component.nx_class = "NXpinhole"

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

    dialog = AddComponentDialog(None,
                                model=model,
                                component_model=component_model,
                                group_to_edit=component,
                                nx_classes=NX_CLASS_DEFINITIONS,
                                initial_edit=False,
                                scene_widget=None,
                                )
    dialog.pixel_options = Mock(spec=PixelOptions)

    qtbot.addWidget(dialog)

    assert dialog.meshRadioButton.isChecked()
    assert dialog.fileLineEdit.isEnabled()
    assert dialog.fileBrowseButton.isEnabled()


def test_UI_GIVEN_component_with_off_shape_WHEN_editing_component_THEN_mesh_data_is_in_line_edits(
    qtbot,
    model,
):
    component_model = ComponentTreeModel(model)

    component_name = "test"
    units = "m"
    filepath = os.path.join(os.path.pardir, "cube.off")

    entry = Entry()
    component = Component(parent_node=entry, name=component_name)
    entry.children.append(component)
    component.nx_class = "NXpinhole"
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

    dialog = AddComponentDialog(None,
        model=model,
        component_model=component_model,
        group_to_edit=component,
        nx_classes=NX_CLASS_DEFINITIONS,
                                initial_edit=False,
                                scene_widget=None,
    )
    dialog.pixel_options = Mock(spec=PixelOptions)
    qtbot.addWidget(dialog)

    assert dialog.meshRadioButton.isChecked()
    assert dialog.fileLineEdit.isEnabled()
    assert dialog.unitsLineEdit.isEnabled()
    assert dialog.unitsLineEdit.text() == units

    assert dialog.fileBrowseButton.isEnabled()

    assert dialog.fileLineEdit.isEnabled()
    assert dialog.fileLineEdit.text() == filepath


def test_UI_GIVEN_field_widget_with_string_type_THEN_value_property_is_correct(
    qtbot, add_component_dialog
):

    qtbot.mouseClick(add_component_dialog.addFieldPushButton, Qt.LeftButton)
    field = add_component_dialog.fieldsListWidget.itemWidget(
        add_component_dialog.fieldsListWidget.item(0)
    )

    field.field_type_combo.setCurrentText(FieldType.scalar_dataset.value)
    field.field_type_combo.currentTextChanged.emit(field.field_type_combo.currentText())

    field.value_type_combo.currentTextChanged.emit(field.value_type_combo.currentText)

    field_name = "testfield"
    field_value = "testvalue"

    field.field_name_edit.setText(field_name)
    field.value_line_edit.setText(field_value)
    field.value_type_combo.setCurrentText(ValueTypes.STRING)

    assert field.dtype == ValueTypes.STRING

    assert field.name == field_name
    assert field.value.values == field_value


def test_UI_GIVEN_field_widget_with_stream_type_THEN_stream_dialog_shown(
    qtbot, add_component_dialog
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
    qtbot, add_component_dialog
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

    assert field.name == field_name
    assert field.value.source == field_target


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_f142_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog
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
    qtbot, add_component_dialog
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


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_ADar_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog
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

    streams_widget._schema_type_changed("ADAr")

    assert streams_widget.topic_label.isEnabled()
    assert streams_widget.topic_line_edit.isEnabled()

    assert streams_widget.source_label.isVisible()
    assert streams_widget.source_line_edit.isVisible()
    assert streams_widget.array_size_label.isVisible()
    assert streams_widget.array_size_table.isVisible()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_ns10_THEN_stream_dialog_shown_with_correct_options(
    qtbot, add_component_dialog
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


@pytest.mark.parametrize("test_input", ["tdct", "senv"])
def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_THEN_stream_dialog_shown_with_correct_options(
    qtbot, test_input, add_component_dialog
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
    qtbot, add_component_dialog
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
    qtbot, add_component_dialog
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
    qtbot, add_component_dialog
):
    add_component_dialog.componentTypeComboBox.setCurrentText("NXaperture")
    current_nx_class = add_component_dialog.componentTypeComboBox.currentText()
    assert current_nx_class in add_component_dialog.webEngineView.url().toString()


def test_UI_GIVEN_change_of_component_type_THEN_webbrowser_url_is_updated_and_contains_component_class(
    qtbot, add_component_dialog
):
    # Setting a valid nexus class.
    add_component_dialog.componentTypeComboBox.setCurrentText("NXsample")

    current_nx_class = add_component_dialog.componentTypeComboBox.currentText()

    new_nx_class = add_component_dialog.componentTypeComboBox.itemText(3)
    add_component_dialog.componentTypeComboBox.setCurrentIndex(3)

    assert new_nx_class in add_component_dialog.webEngineView.url().toString()
    assert current_nx_class not in add_component_dialog.webEngineView.url().toString()


def test_UI_GIVEN_field_widget_with_stream_type_and_schema_set_to_f142_THEN_stream_dialog_shown_with_array_size_option_and_correct_value_in_nexus_file(
    qtbot, add_component_dialog
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

    stream = streams_widget.get_stream_module(None)

    assert stream.array_size == array_size


def test_UI_GIVEN_component_with_pixel_data_WHEN_editing_a_component_THEN_pixel_options_become_visible(
    qtbot, edit_component_dialog, mock_pixel_options
):
    show_and_close_window(qtbot, add_component_dialog)
    mock_pixel_options.fill_existing_entries.assert_called_once()


def test_UI_GIVEN_pixel_grid_WHEN_editing_mesh_component_with_grid_THEN_new_pixel_grid_is_written(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    prev_pixel_grid_size = 5
    new_pixel_grid_size = 3

    # Create a component with a pixel grid
    component_name = "ComponentWithGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        False,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
        assert component_to_edit.get_field_value(field).shape == (
            new_pixel_grid_size,
            new_pixel_grid_size,
        )

    assert isinstance(component_to_edit.shape[0], expected_geometry)


def test_UI_GIVEN_pixel_grid_WHEN_editing_cylinder_component_with_grid_THEN_new_pixel_grid_is_written(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    prev_pixel_grid_size = 5
    new_pixel_grid_size = 3

    # Create a component with a pixel grid
    component_name = "ComponentWithGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        True,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
        assert component_to_edit.get_field_value(field).shape == (
            new_pixel_grid_size,
            new_pixel_grid_size,
        )

    assert isinstance(component_to_edit.shape[0], expected_geometry)


def test_UI_GIVEN_pixel_mapping_WHEN_editing_cylinder_component_with_mapping_THEN_new_pixel_mapping_is_written(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    prev_detector_numbers = [5]
    new_detector_numbers = [6]

    # Create a component with a pixel mapping
    component_name = "ComponentWithMapping"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        True,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
    assert component_to_edit.get_field_value("detector_number") == new_detector_numbers
    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_pixel_grid_WHEN_editing_mesh_component_with_pixel_mapping_THEN_grid_replaces_mapping(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with a pixel mapping
    component_name = "MappingToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        False,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
        assert component_to_edit.get_field_value(field).shape == (grid_size, grid_size)

    shape, pixel_offsets = component_to_edit.shape

    with pytest.raises(AttributeError):
        shape.detector_faces

    assert pixel_offsets is not None
    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_pixel_grid_WHEN_editing_cylinder_component_with_pixel_mapping_THEN_grid_replaces_mapping(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with a pixel mapping
    component_name = "MappingToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        True,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
        assert component_to_edit.get_field_value(field).shape == (grid_size, grid_size)

    shape, pixel_offsets = component_to_edit.shape

    assert pixel_offsets is not None
    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_no_pixels_WHEN_editing_cylinder_component_with_pixel_mapping_THEN_mapping_is_erased(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with a pixel mapping
    component_name = "MappingToNoPixels"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog,
        component_name,
        True,
        mock_pixel_options,
        qtbot,
        add_component_dialog,
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
    with pytest.raises(AttributeError):
        component_to_edit.get_field_value("detector_number")

    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_pixel_grid_WHEN_editing_mesh_component_with_no_pixel_data_THEN_pixel_grid_is_created(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with no pixel data
    component_name = "NoPixelsToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog, component_name, False, mock_pixel_options, qtbot, add_component_dialog
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
        assert component_to_edit.get_field_value(field).shape == (grid_size, grid_size)

    assert isinstance(component_to_edit.shape[0], expected_geometry)


def test_UI_GIVEN_pixel_grid_WHEN_editing_cylinder_component_with_no_pixel_data_THEN_pixel_grid_is_created(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with no pixel data
    component_name = "NoPixelsToGrid"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog, component_name, True, mock_pixel_options, qtbot, add_component_dialog
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
        assert component_to_edit.get_field_value(field).shape == (grid_size, grid_size)

    assert isinstance(component_to_edit.shape[0], expected_geometry)


def test_UI_GIVEN_pixel_mapping_WHEN_editing_cylinder_component_with_no_pixel_data_THEN_pixel_mapping_is_created(
    qtbot, add_component_dialog, mock_pixel_options, parent_mock
):
    # Create a component with no pixel data
    component_name = "NoPixelsToMapping"
    expected_geometry = enter_and_create_component_with_pixel_data(
        add_component_dialog, component_name, True, mock_pixel_options, qtbot, add_component_dialog
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
    assert component_to_edit.get_field_value("detector_number") == detector_number

    assert isinstance(shape, expected_geometry)


def test_UI_GIVEN_previous_transformations_WHEN_editing_component_THEN_transformation_changed_signal_is_emitted(
    edit_component_dialog,
):

    transformation_mock = Mock()
    edit_component_dialog.signals.transformation_changed = transformation_mock
    edit_component_dialog.on_ok()
    transformation_mock.emit.assert_called_once()


def test_UI_GIVEN_creating_component_WHEN_pressing_ok_THEN_transformation_changed_signal_isnt_emitted(
    add_component_dialog, qtbot
):

    transformation_mock = Mock()
    add_component_dialog.signals.transformation_changed = transformation_mock

    enter_component_name(qtbot, add_component_dialog, add_component_dialog, "component name")

    add_component_dialog.on_ok()

    transformation_mock.emit.assert_not_called()


def test_UI_GIVEN_component_is_changed_WHEN_editing_component_THEN_delete_component_is_called(
    parent_mock, edit_component_dialog, component_with_cylindrical_geometry
):
    edit_component_dialog.on_ok()
    parent_mock.sceneWidget.delete_component.assert_called_once_with(
        component_with_cylindrical_geometry.name
    )
