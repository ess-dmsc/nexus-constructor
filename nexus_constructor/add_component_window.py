from collections import OrderedDict
from enum import Enum

import h5py
from PySide2.QtGui import QVector3D
from PySide2.QtCore import QUrl, Signal, QObject
from PySide2.QtWidgets import QListWidgetItem

from nexus_constructor.component.component_factory import create_component
from nexus_constructor.geometry import (
    OFFGeometry,
    OFFGeometryNoNexus,
    NoShapeGeometry,
    CylindricalGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.component_fields import FieldWidget, add_fields_to_component
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    UserDefinedChopperChecker,
)
from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    DiskChopperGeometryCreator,
)
from nexus_constructor.stream_advanced_options import (
    NEXUS_INDICES_INDEX_EVERY_MB,
    NEXUS_INDICES_INDEX_EVERY_KB,
    STORE_LATEST_INTO,
    NEXUS_BUFFER_PACKET_MAX_KB,
    NEXUS_BUFFER_SIZE_KB,
    NEXUS_BUFFER_SIZE_MB,
    NEXUS_CHUNK_CHUNK_KB,
    NEXUS_CHUNK_CHUNK_MB,
    ADC_PULSE_DEBUG,
)
from ui.add_component import Ui_AddComponentDialog
from nexus_constructor.component.component_type import (
    make_dictionary_of_class_definitions,
    PIXEL_COMPONENT_TYPES,
    CHOPPER_CLASS_NAME,
)
from nexus_constructor.validators import (
    UnitValidator,
    NameValidator,
    GeometryFileValidator,
    GEOMETRY_FILE_TYPES,
    OkValidator,
    FieldType,
)
from nexus_constructor.instrument import Instrument
from nexus_constructor.ui_utils import file_dialog, validate_line_edit
from nexus_constructor.component_tree_model import ComponentTreeModel
import os
from functools import partial
from nexus_constructor.ui_utils import generate_unique_name
from nexus_constructor.component.component import Component
from nexus_constructor.geometry.geometry_loader import load_geometry

from nexus_constructor.pixel_data import PixelData, PixelMapping, PixelGrid
from nexus_constructor.pixel_options import PixelOptions
import numpy as np


class GeometryType(Enum):
    NONE = 1
    CYLINDER = 2
    MESH = 3


class AddComponentDialog(Ui_AddComponentDialog, QObject):
    nx_class_changed = Signal("QVariant")

    def __init__(
        self,
        instrument: Instrument,
        component_model: ComponentTreeModel,
        component_to_edit: Component = None,
        parent=None,
    ):
        super(AddComponentDialog, self).__init__()
        if parent:
            self.setParent(parent)
        self.instrument = instrument
        self.component_model = component_model
        self.geometry_model = None
        _, self.nx_component_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )
        self.nx_component_classes = OrderedDict(
            sorted(self.nx_component_classes.items())
        )

        self.cad_file_name = None
        self.possible_fields = []
        self.component_to_edit = component_to_edit
        self.valid_file_given = False
        self.pixel_options = None

    def setupUi(self, parent_dialog):
        """ Sets up push buttons and validators for the add component window. """
        super().setupUi(parent_dialog)

        # Connect the button calls with functions
        self.buttonBox.clicked.connect(self.on_ok)

        # Disable by default as component name will be missing at the very least.
        self.buttonBox.setEnabled(False)

        # Set default URL to nexus base classes in web view
        self.webEngineView.setUrl(
            QUrl(
                "http://download.nexusformat.org/doc/html/classes/base_classes/index.html"
            )
        )

        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
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

        component_list = self.instrument.get_component_list()

        if self.component_to_edit:
            for item in component_list:
                if item.name == self.component_to_edit.name:
                    component_list.remove(item)

        name_validator = NameValidator(component_list)
        self.nameLineEdit.setValidator(name_validator)
        self.nameLineEdit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.nameLineEdit,
                tooltip_on_accept="Component name is valid.",
                tooltip_on_reject=f"Component name is not valid. Suggestion: ",
                suggestion_callable=self.generate_name_suggestion,
            )
        )

        validate_line_edit(self.fileLineEdit, False)

        self.unitsLineEdit.setValidator(UnitValidator())
        self.unitsLineEdit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.unitsLineEdit,
                tooltip_on_reject="Units not valid",
                tooltip_on_accept="Units Valid",
            )
        )

        self.componentTypeComboBox.addItems(list(self.nx_component_classes.keys()))
        self.componentTypeComboBox.currentIndexChanged.connect(
            self.change_pixel_options_visibility
        )

        # Set whatever the default nx_class is so the fields autocompleter can use the possible fields in the nx_class
        self.on_nx_class_changed()

        self.fieldsListWidget.itemClicked.connect(self.select_field)

        self.pixel_options = PixelOptions()
        self.pixel_options.setupUi(self.pixelOptionsWidget)
        self.pixelOptionsWidget.ui = self.pixel_options

        if self.component_to_edit:
            self._fill_existing_entries()
            self.pixel_options.fill_existing_entries()

        self.ok_validator = OkValidator(
            self.noShapeRadioButton,
            self.meshRadioButton,
            self.pixel_options.get_validator(),
        )
        self.ok_validator.is_valid.connect(self.buttonBox.setEnabled)

        self.nameLineEdit.validator().is_valid.connect(self.ok_validator.set_name_valid)

        [
            button.clicked.connect(self.ok_validator.validate_ok)
            for button in [
                self.meshRadioButton,
                self.CylinderRadioButton,
                self.noShapeRadioButton,
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
        self.addFieldPushButton.clicked.connect(self.add_field)
        self.removeFieldPushButton.clicked.connect(self.remove_field)

        # Connect the pixel mapping press signal the populate pixel mapping method
        self.pixel_options.pixel_mapping_button_pressed.connect(
            self.populate_pixel_mapping_if_necessary
        )

        self.cylinderCountSpinBox.valueChanged.connect(
            self.populate_pixel_mapping_if_necessary
        )

        self.meshRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.CylinderRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.noShapeRadioButton.clicked.connect(self.set_pixel_related_changes)

    def set_pixel_related_changes(self):
        """
        Manages the pixel-related changes that are induced by changing the shape type. This entails changing the
        visibility of the pixel options widget, clearing the previous pixel mapping widget list (if necessary),
        generating a new pixel mapping widget list (if necessary), and reassessing the validity of the pixel input.
        """
        self.change_pixel_options_visibility()

        if not self.noShapeRadioButton.isChecked():
            self.clear_previous_mapping_list()
            self.populate_pixel_mapping_if_necessary()

        self.update_pixel_input_validity()

    def clear_previous_mapping_list(self):
        """
        Wipes the previous list of pixel mapping widgets. Required if the file has changed, or if the shape type has
        changed.
        """
        self.pixel_options.reset_pixel_mapping_list()

    def _fill_existing_entries(self):
        self.buttonBox.setText("Edit Component")
        self.nameLineEdit.setText(self.component_to_edit.name)
        self.descriptionPlainTextEdit.setText(self.component_to_edit.description)
        self.componentTypeComboBox.setCurrentText(self.component_to_edit.nx_class)
        component_shape, _ = self.component_to_edit.shape
        if not component_shape or isinstance(component_shape, NoShapeGeometry):
            self.noShapeRadioButton.setChecked(True)
            self.noShapeRadioButton.clicked.emit()
        else:
            if isinstance(component_shape, OFFGeometryNexus):
                self.meshRadioButton.setChecked(True)
                self.meshRadioButton.clicked.emit()
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
        fields = self.component_to_edit.get_fields()
        if fields:
            for field in fields:
                new_ui_field = self.add_field()
                new_ui_field.name = field.name.split("/")[-1]
                if isinstance(field, h5py.Dataset):
                    dtype = field.dtype
                    value = field.value
                    new_ui_field.dtype = dtype
                    if np.isscalar(value):
                        self._update_existing_scalar_field(field, new_ui_field)
                    else:
                        self._update_existing_array_field(new_ui_field, value)
                elif isinstance(field, h5py.Group):
                    if isinstance(
                        field.parent.get(field.name, getlink=True), h5py.SoftLink
                    ):
                        self._update_existing_link_field(field, new_ui_field)
                    elif (
                        "NX_class" in field.attrs.keys()
                        and field.attrs["NX_class"] == "NCstream"
                    ):
                        self._update_existing_stream_info(field, new_ui_field)

    def _update_existing_link_field(self, field, new_ui_field):
        new_ui_field.field_type = FieldType.link.value
        new_ui_field.value = field.parent.get(field.name, getlink=True).path

    def _update_existing_array_field(self, new_ui_field, value):
        new_ui_field.field_type = FieldType.array_dataset.value
        new_ui_field.value = value

    def _update_existing_scalar_field(self, field, new_ui_field):
        new_ui_field.field_type = FieldType.scalar_dataset.value
        if field.dtype == h5py.special_dtype(vlen=str):
            new_ui_field.value = field.value
        else:
            new_ui_field.value = field.value[()]

    def _update_existing_stream_info(self, field, new_ui_field):
        new_ui_field.field_type = FieldType.kafka_stream.value
        schema = field["writer_module"][()]
        new_ui_field.streams_widget.schema_combo.setCurrentText(str(schema))
        new_ui_field.streams_widget.topic_line_edit.setText(str(field["topic"][()]))
        if schema != "ev42":
            new_ui_field.streams_widget.source_line_edit.setText(
                str(field["source"][()])
            )
        if schema == "f142":
            self.__fill_in_existing_f142_fields(field, new_ui_field)

        if schema == "ev42":
            self.__fill_in_existing_ev42_fields(field, new_ui_field)

    def __fill_in_existing_ev42_fields(self, field, new_ui_field):
        advanced_options = False
        for item in field.keys():
            if item in [
                ADC_PULSE_DEBUG,
                NEXUS_INDICES_INDEX_EVERY_MB,
                NEXUS_INDICES_INDEX_EVERY_KB,
                NEXUS_CHUNK_CHUNK_MB,
                NEXUS_CHUNK_CHUNK_KB,
                NEXUS_BUFFER_SIZE_MB,
                NEXUS_BUFFER_SIZE_KB,
                NEXUS_BUFFER_PACKET_MAX_KB,
            ]:
                advanced_options = True

        if advanced_options:
            new_ui_field.streams_widget.ev42_advanced_group_box.setEnabled(True)
            new_ui_field.streams_widget.set_advanced_options_state()

        if ADC_PULSE_DEBUG in field.keys():
            new_ui_field.streams_widget.ev42_adc_pulse_debug_checkbox.setChecked(
                bool(field[ADC_PULSE_DEBUG][()])
            )
        if NEXUS_INDICES_INDEX_EVERY_MB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_indices_index_every_mb_spinbox.setValue(
                field[NEXUS_INDICES_INDEX_EVERY_MB][()]
            )
        if NEXUS_INDICES_INDEX_EVERY_KB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_indices_index_every_kb_spinbox.setValue(
                field[NEXUS_INDICES_INDEX_EVERY_KB][()]
            )
        if NEXUS_CHUNK_CHUNK_MB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_chunk_chunk_mb_spinbox.setValue(
                field[NEXUS_CHUNK_CHUNK_MB][()]
            )
        if NEXUS_CHUNK_CHUNK_KB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_chunk_chunk_kb_spinbox.setValue(
                field[NEXUS_CHUNK_CHUNK_KB][()]
            )
        if NEXUS_BUFFER_SIZE_MB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_buffer_size_mb_spinbox.setValue(
                field[NEXUS_BUFFER_SIZE_MB][()]
            )
        if NEXUS_BUFFER_SIZE_KB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_buffer_size_kb_spinbox.setValue(
                field[NEXUS_BUFFER_SIZE_KB][()]
            )
        if NEXUS_BUFFER_PACKET_MAX_KB in field.keys():
            new_ui_field.streams_widget.ev42_nexus_buffer_packet_max_kb_spinbox.setValue(
                field[NEXUS_BUFFER_PACKET_MAX_KB][()]
            )

    def __fill_in_existing_f142_fields(self, field, new_ui_field):
        new_ui_field.streams_widget.type_combo.setCurrentText(field["type"][()])
        if "array_size" in field.keys():
            new_ui_field.streams_widget.array_radio.setChecked(True)
            new_ui_field.streams_widget.scalar_radio.setChecked(False)
            new_ui_field.streams_widget.array_size_spinbox.setValue(
                field["array_size"][()]
            )
        else:
            new_ui_field.streams_widget.array_radio.setChecked(False)
            new_ui_field.streams_widget.scalar_radio.setChecked(True)
        if (
            NEXUS_INDICES_INDEX_EVERY_KB in field.keys()
            or NEXUS_INDICES_INDEX_EVERY_MB in field.keys()
            or STORE_LATEST_INTO in field.keys()
        ):
            new_ui_field.streams_widget.f142_advanced_group_box.setEnabled(True)
            new_ui_field.streams_widget.set_advanced_options_state()
        if NEXUS_INDICES_INDEX_EVERY_MB in field.keys():
            new_ui_field.streams_widget.f142_nexus_indices_index_every_mb_spinbox.setValue(
                field[NEXUS_INDICES_INDEX_EVERY_MB][()]
            )
        if NEXUS_INDICES_INDEX_EVERY_KB in field.keys():
            new_ui_field.streams_widget.f142_nexus_indices_index_every_kb_spinbox.setValue(
                field[NEXUS_INDICES_INDEX_EVERY_KB][()]
            )
        if STORE_LATEST_INTO in field.keys():
            new_ui_field.streams_widget.f142_nexus_store_latest_into_spinbox.setValue(
                field[STORE_LATEST_INTO][()]
            )

    def add_field(self) -> FieldWidget:
        item = QListWidgetItem()
        field = FieldWidget(
            self.possible_fields, self.fieldsListWidget, self.instrument
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

    def generate_name_suggestion(self):
        """
        Generates a component name suggestion for use in the tooltip when a component is invalid.
        :return: The component name suggestion, based on the current nx_class.
        """
        return generate_unique_name(
            self.componentTypeComboBox.currentText().lstrip("NX"),
            self.instrument.get_component_list(),
        )

    def on_nx_class_changed(self):
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{self.componentTypeComboBox.currentText()}.html"
            )
        )
        self.possible_fields = self.nx_component_classes[
            self.componentTypeComboBox.currentText()
        ]
        self.nx_class_changed.emit(self.possible_fields)

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

    def show_no_geometry_fields(self):

        self.shapeOptionsBox.setVisible(False)
        if self.nameLineEdit.text():
            self.buttonBox.setEnabled(True)

    def show_mesh_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)

    def generate_geometry_model(
        self, component: Component, pixel_data: PixelData = None
    ) -> OFFGeometry:
        """
        Generates a geometry model depending on the type of geometry selected and the current values
        of the line edits that apply to the particular geometry type.
        :return: The generated model.
        """
        if self.CylinderRadioButton.isChecked():

            geometry_model = component.set_cylinder_shape(
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
        elif self.meshRadioButton.isChecked():
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
        else:
            chopper_checker = UserDefinedChopperChecker(self.fieldsListWidget)
            if (
                component.nx_class == CHOPPER_CLASS_NAME
                and chopper_checker.validate_chopper()
            ):
                geometry_model = DiskChopperGeometryCreator(
                    chopper_checker.chopper_details
                ).create_disk_chopper_geometry()
            else:
                geometry_model = NoShapeGeometry()
                component.remove_shape()

        return geometry_model

    def get_pixel_visibility_condition(self):
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
        nx_class = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()

        pixel_data = self.pixel_options.generate_pixel_data()

        if self.component_to_edit:
            shape, positions = self.edit_existing_component(
                component_name, description, nx_class, pixel_data
            )
        else:
            shape, positions = self.create_new_component(
                component_name, description, nx_class, pixel_data
            )

        self.instrument.nexus.component_added.emit(
            self.nameLineEdit.text(), shape, positions
        )

    def create_new_component(
        self,
        component_name: str,
        description: str,
        nx_class: str,
        pixel_data: PixelData,
    ):
        """
        Creates a new component.
        :param component_name: The name of the component.
        :param description: The component description.
        :param nx_class: The component class.
        :param pixel_data: The PixelData for the component. Will be None if it was not given of if the component type
            doesn't have pixel-related fields.
        :return: The geometry object.
        """
        component = self.instrument.create_component(
            component_name, nx_class, description
        )
        self.generate_geometry_model(component, pixel_data)

        # In the future this should check if the class is NXdetector or NXdetector_module
        if nx_class == "NXdetector":
            if isinstance(pixel_data, PixelMapping):
                component.record_detector_number(pixel_data)
            if isinstance(pixel_data, PixelGrid):
                component.record_pixel_grid(pixel_data)

        add_fields_to_component(component, self.fieldsListWidget)
        self.component_model.add_component(component)

        component_with_geometry = create_component(
            self.instrument.nexus, component.group
        )
        return component_with_geometry.shape

    def edit_existing_component(
        self,
        component_name: str,
        description: str,
        nx_class: str,
        pixel_data: PixelData,
    ):
        """
        Edits an existing component.
        :param component_name: The component name.
        :param description: The component description.
        :param nx_class: The component class.
        :param pixel_data: The component PixelData. Can be None.
        :return: The geometry object.
        """
        self.component_to_edit.name = component_name
        self.component_to_edit.nx_class = nx_class
        self.component_to_edit.description = description
        # remove the previous shape from the qt3d view
        if not isinstance(self.component_to_edit.shape[0], NoShapeGeometry):
            self.instrument.remove_component(self.component_to_edit)

        add_fields_to_component(self.component_to_edit, self.fieldsListWidget)
        self.generate_geometry_model(self.component_to_edit, pixel_data)
        component_with_geometry = create_component(
            self.instrument.nexus, self.component_to_edit.group
        )
        return component_with_geometry.shape

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
        has been selected.
        """

        if not self.pixelOptionsWidget.isVisible():
            return

        if self.meshRadioButton.isChecked():
            self.create_pixel_mapping_list_for_mesh()

        if self.CylinderRadioButton.isChecked():
            self.pixel_options.populate_pixel_mapping_list_with_cylinder_number(
                self.cylinderCountSpinBox.value()
            )

    def create_pixel_mapping_list_for_mesh(self):
        """
        Instructs the PixelOptions to create a list of Pixel Mapping widgets using a mesh file if the user has given a
        valid file and has not selected the same file twice in a row.
        """
        if (
            self.cad_file_name is not None
            and self.valid_file_given
            and self.pixel_options.get_current_mapping_filename() != self.cad_file_name
        ):
            self.pixel_options.populate_pixel_mapping_list_with_mesh(self.cad_file_name)

    def update_pixel_input_validity(self):
        """
        :return:
        """
        self.pixel_options.update_pixel_input_validity()
