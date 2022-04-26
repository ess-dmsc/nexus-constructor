import logging
from collections import OrderedDict
from copy import deepcopy
from functools import partial
from typing import List

from PySide2.QtCore import Qt, QUrl, Signal
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QWidget, QMessageBox

from nexus_constructor.common_attrs import SHAPE_GROUP_NAME, CommonAttrs
from nexus_constructor.component_tree_model import NexusTreeModel
from nexus_constructor.component_type import (
    CHOPPER_CLASS_NAME,
    COMPONENT_TYPES,
    PIXEL_COMPONENT_TYPES,
    SLIT_CLASS_NAME,
)
from nexus_constructor.field_utils import get_fields_with_update_functions
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import ChopperChecker
from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    DiskChopperGeometryCreator,
)
from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.geometry.pixel_data import PixelData, PixelGrid, PixelMapping
from nexus_constructor.geometry.slit.slit_geometry import SlitGeometry
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import (
    BoxGeometry,
    CylindricalGeometry,
    NoShapeGeometry,
    OFFGeometryNexus,
    OFFGeometryNoNexus,
)
from nexus_constructor.model.group import Group, GroupContainer
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset, Link
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.ui_utils import (
    file_dialog,
    show_warning_dialog,
    validate_line_edit,
)
from nexus_constructor.unit_utils import METRES
from nexus_constructor.validators import (
    GEOMETRY_FILE_TYPES,
    SKIP_VALIDATION,
    GeometryFileValidator,
    OkValidator,
    UnitValidator,
)
from ui.add_component import Ui_AddComponentDialog


def _set_chopper_geometry(component: Component, fields_list_widget: QListWidget):
    """
    Attempts to set a chopper geometry in the component by checking if the component fields describe a valid chopper.
    :param component: The component to be given a shape.
    :param fields_list_widget: The fields list widget that contains the user input.
    """
    chopper_validator = ChopperChecker(fields_list_widget)

    if chopper_validator.validate_chopper():
        chopper_details = chopper_validator.chopper_details
        chopper_creator = DiskChopperGeometryCreator(chopper_details)
        component[SHAPE_GROUP_NAME] = chopper_creator.create_disk_chopper_geometry()
    else:
        logging.warning("Validation failed. Unable to create disk chopper mesh.")


def _set_slit_geometry(component: Component):
    slit_geometry = SlitGeometry()
    component[SHAPE_GROUP_NAME] = slit_geometry.create_slit_geometry()


class AddComponentDialog(Ui_AddComponentDialog):
    nx_class_changed = Signal("QVariant")

    def __init__(
        self,
        parent: QWidget,
        model: Model,
        component_model: NexusTreeModel,
        group_to_edit: Group,
        scene_widget: QWidget,
        initial_edit: bool,
        nx_classes=None,
    ):
        self._scene_widget = scene_widget
        self._group_container = GroupContainer(group_to_edit)
        self._group_parent = group_to_edit.parent_node
        self.group_to_edit = group_to_edit  # To be removed
        super().__init__(parent, self._group_container)
        super().setupUi()
        if nx_classes is None:
            nx_classes = {}
        self.signals = model.signals
        self.model = model
        self.component_model = component_model
        self.nx_component_classes = OrderedDict(sorted(nx_classes.items()))

        self.cad_file_name = None
        self.possible_fields: List[str] = []
        self.initial_edit = initial_edit
        self.valid_file_given = False
        self.pixel_options: PixelOptions = None
        self.setupUi()
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        if self.initial_edit:
            self.ok_button.setText("Add group")
            self.cancel_button.setVisible(True)
            self.componentTypeComboBox.currentIndexChanged.connect(self._handle_class_change)
            self.cancel_button.clicked.connect(self._cancel_new_group)
            self.rejected.connect(self._rejected)

    def _rejected(self):
        if self.initial_edit:
            self._group_parent.children.remove(self._group_container.group)

    def _confirm_cancel(self) -> bool:
        quit_msg = "Do you want to close the group editor?"
        reply = QMessageBox.question(
            self,
            "Really quit?",
            quit_msg,
            QMessageBox.Close | QMessageBox.Ignore,
            QMessageBox.Close,
        )
        if reply == QMessageBox.Close:
            return True
        return False

    def _cancel_new_group(self):
        if self._confirm_cancel():
            self.close()

    def _handle_class_change(self):
        c_nx_class = self.componentTypeComboBox.currentText()
        c_attributes = self._group_container.group.attributes
        c_name = self._group_container.group.name
        c_children = self._group_container.group.children
        group_constructor = None
        if isinstance(self._group_container.group, Component) and c_nx_class not in COMPONENT_TYPES:
            group_constructor = Group
        elif not isinstance(self._group_container.group, Component) and c_nx_class in COMPONENT_TYPES:
            group_constructor = Component
        if group_constructor:
            self._group_parent.children.remove(self._group_container.group)
            self._group_container.group = group_constructor(name=c_name, parent_node=self._group_parent)
            self._group_container.group.attributes = c_attributes
            self._group_container.group.children = c_children
            self._group_container.group.nx_class = c_nx_class
            self._group_parent.children.append(self._group_container.group)


    def setupUi(self, pixel_options: PixelOptions = PixelOptions()):
        """Sets up push buttons and validators for the add component window."""

        # Connect the button calls with functions
        self.ok_button.clicked.connect(self.on_ok)

        # Disable by default as component name will be missing at the very least.
        self.ok_button.setEnabled(False)

        # Set default URL to nexus base classes in web view
        self.webEngineView.setUrl(
            QUrl(
                "http://download.nexusformat.org/doc/html/classes/base_classes/index.html"
            )
        )

        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.boxRadioButton.clicked.connect(self.show_box_fields)
        self.CylinderRadioButton.clicked.connect(self.show_cylinder_fields)
        self.noShapeRadioButton.clicked.connect(self.show_no_geometry_fields)
        self.fileBrowseButton.clicked.connect(self.mesh_file_picker)

        self.fileLineEdit.setValidator(GeometryFileValidator(GEOMETRY_FILE_TYPES))
        self.fileLineEdit.validator().is_valid.connect(
            partial(validate_line_edit, self.fileLineEdit)
        )
        self.fileLineEdit.textChanged.connect(self.populate_pixel_mapping_if_necessary)

        self.componentTypeComboBox.currentIndexChanged.connect(self.on_nx_class_changed)

        # Set default geometry type and show the related fields.
        self.noShapeRadioButton.setChecked(True)
        self.show_no_geometry_fields()

        validate_line_edit(self.fileLineEdit, False)

        self.unitsLineEdit.setValidator(UnitValidator(expected_dimensionality=METRES))
        self.unitsLineEdit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.unitsLineEdit,
                tooltip_on_reject="Units not valid",
                tooltip_on_accept="Units Valid",
            )
        )

        self.componentTypeComboBox.currentIndexChanged.connect(
            self.change_pixel_options_visibility
        )

        # Set whatever the default nx_class is so the fields autocompleter can use the possible fields in the nx_class
        self.on_nx_class_changed()

        self.fieldsListWidget.itemClicked.connect(self.select_field)

        self.pixel_options = pixel_options
        if self.pixel_options:
            self.pixel_options.setupUi(self.pixelOptionsWidget)
        self.pixelOptionsWidget.ui = self.pixel_options

        self.ok_validator = OkValidator(
            self.noShapeRadioButton, self.meshRadioButton, self.pixel_options.validator)

        c_group = self._group_container.group

        if not self.initial_edit:
            self.setWindowTitle(f"Edit group: {c_group.name}")
            self._fill_existing_entries()
            if self.get_pixel_visibility_condition() and self.pixel_options:
                self.pixel_options.fill_existing_entries(c_group.group)
        else:
            self.ok_validator.set_nx_class_valid(False)

        self.componentTypeComboBox.validator().is_valid.connect(self.ok_validator.set_nx_class_valid)
        self.componentTypeComboBox.validator().validate(self.componentTypeComboBox.currentText(), 0)

        self.ok_validator.is_valid.connect(self.ok_button.setEnabled)

        self.nameLineEdit.validator().is_valid.connect(self.ok_validator.set_name_valid)

        [
            button.clicked.connect(self.ok_validator.validate_ok)
            for button in [
                self.meshRadioButton,
                self.CylinderRadioButton,
                self.noShapeRadioButton,
                self.boxRadioButton,
            ]
        ]

        self.unitsLineEdit.validator().is_valid.connect(
            self.ok_validator.set_units_valid
        )
        self.fileLineEdit.validator().is_valid.connect(self.ok_validator.set_file_valid)
        self.fileLineEdit.validator().is_valid.connect(self.set_file_valid)

        # Validate the default values set by the UI
        self.unitsLineEdit.validator().validate(self.unitsLineEdit.text(), 0)
        self.nameLineEdit.validator().validate(self.nameLineEdit.text(), 0)
        if not c_group:
            self.fileLineEdit.validator().validate(self.fileLineEdit.text(), 0)
        else:
            text = (
                SKIP_VALIDATION
                if c_group.has_pixel_shape()
                and not self.fileLineEdit.text()
                else self.fileLineEdit.text()
            )
            self.fileLineEdit.validator().validate(text, 0)
        self.addFieldPushButton.clicked.connect(self.add_field)
        self.removeFieldPushButton.clicked.connect(self.remove_field)

        # Connect the pixel mapping press signal the populate pixel mapping method
        if self.pixel_options:
            self.pixel_options.pixel_mapping_button_pressed.connect(
                self.populate_pixel_mapping_if_necessary
            )

        self.cylinderCountSpinBox.valueChanged.connect(
            self.populate_pixel_mapping_if_necessary
        )

        self.meshRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.CylinderRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.noShapeRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.boxRadioButton.clicked.connect(self.set_pixel_related_changes)

        self.change_pixel_options_visibility()
        self.setAttribute(Qt.WA_DeleteOnClose)

    def set_pixel_related_changes(self):
        """
        Manages the pixel-related changes that are induced by changing the shape type. This entails changing the
        visibility of the pixel options widget, clearing the previous pixel mapping table widget(if necessary),
        generating a new pixel mapping widget table (if necessary), and reassessing the validity of the pixel input.
        """
        self.change_pixel_options_visibility()

        if not self.noShapeRadioButton.isChecked():
            self.clear_previous_mapping_table()
            self.populate_pixel_mapping_if_necessary()

        self.update_pixel_input_validity()

    def clear_previous_mapping_table(self):
        """
        Wipes the previous table of pixel mapping table widgets. Required if the file has changed, or if the shape type has
        changed.
        """
        if self.pixel_options:
            self.pixel_options.reset_pixel_mapping_table()

    def _fill_existing_entries(self):
        """
        Fill in component details in the UI if editing a component
        """
        self.nameLineEdit.setText(self.group_to_edit.name)
        self.descriptionPlainTextEdit.setText(self.group_to_edit.description)
        self.componentTypeComboBox.setCurrentText(self.group_to_edit.nx_class)
        if isinstance(self.group_to_edit, Component):
            self.__fill_existing_shape_info()
        self.__fill_existing_fields()

    def __fill_existing_fields(self):
        items_and_update_methods = get_fields_and_update_functions_for_component(
            self.group_to_edit
        )
        for field, update_method in items_and_update_methods:
            if update_method is not None:
                new_ui_field = self.create_new_ui_field(field)
                update_method(field, new_ui_field)
                if not isinstance(field, Link):
                    try:
                        new_ui_field.units = field.attributes.get_attribute_value(
                            CommonAttrs.UNITS
                        )
                    except AttributeError:
                        new_ui_field.units = ""

    def __fill_existing_shape_info(self):
        component_shape, _ = self.group_to_edit.shape
        if not component_shape or isinstance(component_shape, NoShapeGeometry):
            self.noShapeRadioButton.setChecked(True)
            self.noShapeRadioButton.clicked.emit()
        else:
            if isinstance(component_shape, OFFGeometryNexus):
                self.cad_file_name = component_shape.file_path
                self.meshRadioButton.setChecked(True)
                self.meshRadioButton.clicked.emit()
                if component_shape.file_path:
                    self.fileLineEdit.setText(component_shape.file_path)
            elif isinstance(component_shape, CylindricalGeometry):
                self.CylinderRadioButton.clicked.emit()
                self.CylinderRadioButton.setChecked(True)
                self.cylinderHeightLineEdit.setValue(component_shape.height)
                self.cylinderRadiusLineEdit.setValue(component_shape.radius)
                self.cylinderXLineEdit.setValue(component_shape.axis_direction.x())
                self.cylinderYLineEdit.setValue(component_shape.axis_direction.y())
                self.cylinderZLineEdit.setValue(component_shape.axis_direction.z())
                self.unitsLineEdit.setText(component_shape.units)
            elif isinstance(component_shape, BoxGeometry):
                self.boxRadioButton.clicked.emit()
                self.boxRadioButton.setChecked(True)
                self.boxLengthLineEdit.setValue(component_shape.size[0])
                self.boxWidthLineEdit.setValue(component_shape.size[1])
                self.boxHeightLineEdit.setValue(component_shape.size[2])
                self.unitsLineEdit.setText(component_shape.units)

    def create_new_ui_field(self, field):
        new_ui_field = self.add_field()
        if isinstance(field, Dataset):
            new_ui_field.name = field.name
        return new_ui_field

    def add_field(self) -> FieldWidget:
        item = QListWidgetItem()
        field = FieldWidget(
            self.group_to_edit, self.possible_fields, self.fieldsListWidget
        )
        field.something_clicked.connect(partial(self.select_field, item))
        self.nx_class_changed.connect(field.field_name_edit.update_possible_fields)
        item.setSizeHint(field.sizeHint())

        self.fieldsListWidget.addItem(item)
        self.fieldsListWidget.setItemWidget(item, field)
        return field

    def select_field(self, widget):
        self.fieldsListWidget.setItemSelected(widget, True)

    def remove_field(self):
        for item in self.fieldsListWidget.selectedItems():
            self.fieldsListWidget.takeItem(self.fieldsListWidget.row(item))

    def on_nx_class_changed(self):
        c_nx_class = self.componentTypeComboBox.currentText()
        if not c_nx_class or c_nx_class not in self.nx_component_classes:
            return
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{c_nx_class}.html"
            )
        )

        self.possible_fields = self.nx_component_classes[c_nx_class]
        try:
            possible_field_names, _ = zip(*self.possible_fields)
            self.nx_class_changed.emit(possible_field_names)
        except ValueError:
            self.nx_class_changed.emit([])

    def mesh_file_picker(self):
        """
        Opens the mesh file picker. Sets the file name line edit to the file path.
        :return: None
        """
        filename = file_dialog(False, "Open Mesh", GEOMETRY_FILE_TYPES)
        self.cad_file_name = filename
        self.fileLineEdit.setText(filename)

    def show_cylinder_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(True)
        self.boxOptionsBox.setVisible(False)

    def show_box_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(False)
        self.boxOptionsBox.setVisible(True)

    def show_no_geometry_fields(self):

        self.shapeOptionsBox.setVisible(False)
        if self.nameLineEdit.text():
            self.ok_button.setEnabled(True)

    def show_mesh_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)
        self.boxOptionsBox.setVisible(False)

    def generate_geometry_model(
        self, component: Component, pixel_data: PixelData = None
    ):
        """
        Generates a geometry model depending on the type of geometry selected and the current values
        of the line edits that apply to the particular geometry type.
        :return: The generated model.
        """
        if self.CylinderRadioButton.isChecked():
            geometry = component.set_cylinder_shape(
                QVector3D(
                    self.cylinderXLineEdit.value(),
                    self.cylinderYLineEdit.value(),
                    self.cylinderZLineEdit.value(),
                ),
                self.cylinderHeightLineEdit.value(),
                self.cylinderRadiusLineEdit.value(),
                self.unitsLineEdit.text(),
                pixel_data=pixel_data,
            )
            if not geometry:
                show_warning_dialog(
                    "3D vector is zero length in cylinder geometry.", ""
                )
        elif self.boxRadioButton.isChecked():
            component.set_box_shape(
                self.boxLengthLineEdit.value(),
                self.boxWidthLineEdit.value(),
                self.boxHeightLineEdit.value(),
                self.unitsLineEdit.text(),
            )
        elif self.meshRadioButton.isChecked() and self.cad_file_name:
            mesh_geometry = OFFGeometryNoNexus()
            geometry_model = load_geometry(
                self.cad_file_name, self.unitsLineEdit.text(), mesh_geometry
            )

            # Units have already been used during loading the file, but we store them and file name
            # so we can repopulate their fields in the edit component window
            geometry_model.units = self.unitsLineEdit.text()
            geometry_model.file_path = self.cad_file_name

            component.set_off_shape(
                geometry_model,
                units=self.unitsLineEdit.text(),
                filename=self.fileLineEdit.text(),
                pixel_data=pixel_data,
            )
        elif (
            self.noShapeRadioButton.isChecked()
            and component.nx_class == CHOPPER_CLASS_NAME
        ):
            _set_chopper_geometry(component, self.fieldsListWidget)
        elif (
            self.noShapeRadioButton.isChecked()
            and component.nx_class == SLIT_CLASS_NAME
        ):
            _set_slit_geometry(component)

    def get_pixel_visibility_condition(self) -> bool:
        """
        Determines if it is necessary to make the pixel options visible.
        :return: A bool indicating if the current shape and component type allow for pixel-related input.
        """
        return (
            self.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES
            and not self.noShapeRadioButton.isChecked()
        )

    def on_ok(self):
        """
        Retrieves information from the interface in order to create a component. By this point the input should already
        be valid as the validators control whether or not the Add Component button is enabled.
        """
        _, index = self.component_model.current_nxs_obj
        self.model.signals.group_edited.emit(index, False)
        if self.pixel_options:
            pixel_data = (
                self.pixel_options.generate_pixel_data()
            )
        else:
            pixel_data = None

        component = self.finalise_group(pixel_data)

        if self.initial_edit and isinstance(component, Component):
            self.signals.component_added.emit(component)

        self.signals.transformation_changed.emit()
        self.model.signals.group_edited.emit(index, True)
        self.hide()

    def finalise_group(
        self,
        pixel_data: PixelData,
    ):
        """
        Edits an existing component.
        :param pixel_data: The component PixelData. Can be None.
        :return: The geometry object.
        """
        c_group = self._group_container.group

        if isinstance(c_group, Component):
            # remove the previous object from the qt3d view
            self._scene_widget.delete_component(c_group.name)
            self.component_model.components.append(c_group)
            self.generate_geometry_model(c_group, pixel_data)
            self.write_pixel_data_to_component(
                c_group, pixel_data
            )
        add_fields_to_component(
            c_group, self.fieldsListWidget, self.component_model
        )
        return c_group

    def write_pixel_data_to_component(
        self, component: Component, pixel_data: PixelData
    ):
        """
        Writes the detector number/pixel grid data to a component.
        :param component: The component to modify.
        :param nx_class: The NXclass of the component.
        :param pixel_data: The pixel data.
        """
        component.clear_pixel_data()

        if pixel_data is None or component.nx_class not in PIXEL_COMPONENT_TYPES:
            return

        if isinstance(pixel_data, PixelMapping):
            component.record_pixel_mapping(pixel_data)
        if isinstance(pixel_data, PixelGrid) and self.get_pixel_visibility_condition():
            component.record_pixel_grid(pixel_data)

    def change_pixel_options_visibility(self):
        """
        Changes the visibility of the pixel options depending on if the current component/shape type has pixel fields.
        """
        self.pixelOptionsWidget.setVisible(self.get_pixel_visibility_condition())

    def set_file_valid(self, validity):
        """
        Records the current status of the geometry file validity. This is used to determine if a list of pixel mapping
        widgets can be generated.
        :param validity: A bool indicating whether the mesh file was opened successfully.
        """
        self.valid_file_given = validity

    def populate_pixel_mapping_if_necessary(self):
        """
        Tells the pixel options widget to populate the pixel mapping widget provided certain conditions are met. Checks
        that the pixel options are visible then performs further checks depending on if the mesh or cylinder button
        has been selected. The RuntimeError occurs when editing a component and switching from a Pixel Grid/No Shape
        to a PixelMapping. It says that the Pixel Options widget and Mesh/Cylinder buttons have been deleted even though
        they ought to be "brand new" when the Edit Component Window opens. A try-except block appears to be the only way
        to handle it for now.
        """
        try:
            if not self.pixelOptionsWidget.isVisible():
                return

            if self.meshRadioButton.isChecked():
                self.create_pixel_mapping_list_for_mesh()

            if self.CylinderRadioButton.isChecked() and self.pixel_options:
                self.pixel_options.populate_pixel_mapping_list_with_cylinder_number(
                    self.cylinderCountSpinBox.value()
                )
        except RuntimeError:
            pass

    def create_pixel_mapping_list_for_mesh(self):
        """
        Instructs the PixelOptions to create a list of Pixel Mapping widgets using a mesh file if the user has given a
        valid file and has not selected the same file twice in a row.
        """
        if (
            self.cad_file_name is not None
            and self.valid_file_given
            and (
                self.pixel_options.get_current_mapping_filename() != self.cad_file_name
            )
        ):
            self.pixel_options.populate_pixel_mapping_list_with_mesh(self.cad_file_name)

    def update_pixel_input_validity(self):
        """
        Instruct the PixelOptions widget to carry out another check for input validity.
        """
        if self.pixel_options:
            self.pixel_options.update_pixel_input_validity()


def get_fields_and_update_functions_for_component(component: Component):
    return get_fields_with_update_functions(component)


def add_fields_to_component(
    component: Group, fields_widget: QListWidget, component_model: NexusTreeModel = None
):
    """
    Adds fields from a list widget to a component.
    :param component: Component to add the field to.
    :param fields_widget: The field list widget to extract field information such the name and value of each field.
    """
    for i in range(fields_widget.count()):
        widget = fields_widget.itemWidget(fields_widget.item(i))
        try:
            if not isinstance(widget.value, (Link, Dataset)):
                stream_module = deepcopy(widget.value)
                stream_module.parent_node = component
                component.children.append(stream_module)
            else:
                component[widget.name] = widget.value
        except ValueError as error:
            show_warning_dialog(
                f"Warning: field {widget.name} not added",
                title="Field invalid",
                additional_info=str(error),
                parent=fields_widget.parent().parent(),
            )
    if component_model and component_model.current_nxs_obj[1]:
        row = component_model.rowCount(component_model.current_nxs_obj[1])
        component_model.createIndex(row, 0, component_model.current_nxs_obj[1])
