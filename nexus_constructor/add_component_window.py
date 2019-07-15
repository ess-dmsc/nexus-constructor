import os
from enum import Enum
from functools import partial

from PySide2.QtCore import QUrl, Signal, QObject
from PySide2.QtGui import QIntValidator, QDoubleValidator
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QListWidgetItem
from nexusutils.readwriteoff import parse_off_file

from nexus_constructor.component import Component
from nexus_constructor.component_fields import FieldWidget, add_fields_to_component
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_type import (
    make_dictionary_of_class_definitions,
    PIXEL_COMPONENT_TYPES,
)
from nexus_constructor.geometry import OFFGeometry, OFFGeometryNoNexus, NoShapeGeometry
from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.instrument import Instrument
from nexus_constructor.pixel_data import CountDirection, Corner, PixelMapping, PixelGrid
from nexus_constructor.pixel_mapping_widget import PixelMappingWidget
from nexus_constructor.ui_utils import file_dialog, validate_line_edit
from nexus_constructor.ui_utils import generate_unique_name
from nexus_constructor.validators import (
    UnitValidator,
    NameValidator,
    GeometryFileValidator,
    GEOMETRY_FILE_TYPES,
    OkValidator,
)
from ui.add_component import Ui_AddComponentDialog


class GeometryType(Enum):
    NONE = 1
    CYLINDER = 2
    MESH = 3


class AddComponentDialog(Ui_AddComponentDialog, QObject):
    nx_class_changed = Signal("QVariant")

    def __init__(self, instrument: Instrument, component_model: ComponentTreeModel):
        super(AddComponentDialog, self).__init__()

        # Dictionaries that map user-input to known pixel grid options. Used when created the PixelGridModel.
        self.count_direction = {
            "Rows": CountDirection.ROW,
            "Columns": CountDirection.COLUMN,
        }
        self.initial_count_corner = {
            "Bottom left": Corner.BOTTOM_LEFT,
            "Bottom right": Corner.BOTTOM_RIGHT,
            "Top left": Corner.TOP_LEFT,
            "Top right": Corner.TOP_RIGHT,
        }

        self.instrument = instrument
        self.component_model = component_model

        self.geometry_model = None
        _, self.nx_component_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

        self.geometry_file_name = None
        self.pixel_mapping_widgets = []

        self.possible_fields = []

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

        self.ok_validator = OkValidator(
            self.noGeometryRadioButton, self.meshRadioButton
        )
        self.ok_validator.is_valid.connect(self.buttonBox.setEnabled)

        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.CylinderRadioButton.clicked.connect(self.show_cylinder_fields)
        self.noGeometryRadioButton.clicked.connect(self.show_no_geometry_fields)
        self.fileBrowseButton.clicked.connect(self.mesh_file_picker)

        [
            button.clicked.connect(self.ok_validator.validate_ok)
            for button in [
                self.meshRadioButton,
                self.CylinderRadioButton,
                self.noGeometryRadioButton,
            ]
        ]

        self.fileLineEdit.setValidator(GeometryFileValidator(GEOMETRY_FILE_TYPES))
        self.fileLineEdit.validator().is_valid.connect(
            partial(validate_line_edit, self.fileLineEdit)
        )
        self.fileLineEdit.validator().is_valid.connect(self.ok_validator.set_file_valid)

        self.componentTypeComboBox.currentIndexChanged.connect(self.on_nx_class_changed)

        # Set default geometry type and show the related fields.
        self.noGeometryRadioButton.setChecked(True)
        self.show_no_geometry_fields()

        name_validator = NameValidator(self.instrument.get_component_list())
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

        self.nameLineEdit.validator().is_valid.connect(self.ok_validator.set_name_valid)

        self.unitsLineEdit.setValidator(UnitValidator())
        self.unitsLineEdit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.unitsLineEdit,
                tooltip_on_reject="Units not valid",
                tooltip_on_accept="Units Valid",
            )
        )
        self.unitsLineEdit.validator().is_valid.connect(
            self.ok_validator.set_units_valid
        )

        self.componentTypeComboBox.addItems(list(self.nx_component_classes.keys()))

        # Validate the default values set by the UI
        self.unitsLineEdit.validator().validate(self.unitsLineEdit.text(), 0)
        self.nameLineEdit.validator().validate(self.nameLineEdit.text(), 0)
        self.addFieldPushButton.clicked.connect(self.add_field)
        self.removeFieldPushButton.clicked.connect(self.remove_field)

        # Set whatever the default nx_class is so the fields autocompleter can use the possible fields in the nx_class
        self.on_nx_class_changed()

        self.fieldsListWidget.itemClicked.connect(self.select_field)

        # Instruct the pixel grid box to appear or disappear depending on the pixel layout setting
        self.repeatableGridRadioButton.clicked.connect(
            lambda: self.show_pixel_grid_or_pixel_mapping(True)
        )
        self.faceMappedMeshRadioButton.clicked.connect(
            lambda: self.show_pixel_grid_or_pixel_mapping(False)
        )

        # Create a validator that only accepts ints that are 0 or greater
        zero_or_greater_int_validator = QIntValidator()
        zero_or_greater_int_validator.setBottom(0)
        # Set the validator of the row, column and first line input boxes in the pixel grid options
        self.rowLineEdit.setValidator(zero_or_greater_int_validator)
        self.columnsLineEdit.setValidator(zero_or_greater_int_validator)
        self.firstIDLineEdit.setValidator(zero_or_greater_int_validator)

        double_validator = QDoubleValidator()
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.rowHeightLineEdit.setValidator(double_validator)
        self.columnWidthLineEdit.setValidator(double_validator)

        self.pixelMappingLabel.setVisible(False)
        self.pixelMappingListWidget.setVisible(False)

    def add_field(self):
        item = QListWidgetItem()
        field = FieldWidget(self.possible_fields, self.fieldsListWidget)
        field.something_clicked.connect(partial(self.select_field, item))
        self.nx_class_changed.connect(field.field_name_edit.update_possible_fields)
        item.setSizeHint(field.sizeHint())

        self.fieldsListWidget.addItem(item)
        self.fieldsListWidget.setItemWidget(item, field)

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
        self.pixelLayoutBox.setVisible(
            self.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES
        )
        self.possible_fields = self.nx_component_classes[
            self.componentTypeComboBox.currentText()
        ]
        self.nx_class_changed.emit(self.possible_fields)

        # Change which pixel-related fields are visible because this depends on the class that has been selected.
        self.change_pixel_options_visibility()

    def show_pixel_grid_or_pixel_mapping(self, bool):
        """
        Switches between the pixel grid or pixel mapping boxes being visible. Populates the pixel mapping list if it is
        visible but empty.
        :param bool: Boolean indicating whether the pixel grid or pixel mapping box should be visible.
        """
        self.pixelGridBox.setVisible(bool)
        self.pixelMappingLabel.setVisible(not bool)
        self.pixelMappingListWidget.setVisible(not bool)

        self.populate_pixel_mapping_list_when_empty(not bool)

    def mesh_file_picker(self):
        """
        Opens the mesh file picker. Sets the file name line edit to the file path. Creates a pixel mapping list if the
        pixel mapping box is visible.
        :return: None
        """
        filename = file_dialog(False, "Open Mesh", GEOMETRY_FILE_TYPES)
        if filename != self.geometry_file_name:
            self.fileLineEdit.setText(filename)
            self.geometry_file_name = filename

        _, _, pixel_mapping_condition = self.pixel_options_conditions()

        if pixel_mapping_condition:
            self.populate_pixel_mapping_list()

    def pixel_options_conditions(self):
        """
        Determine which of the pixel-related fields need to be visible.
        :return: Booleans indicating whether the pixel layout, pixel data, pixel grid, and pixel mapping options need to
        be made visible.
        """

        pixel_layout_condition = (
            self.componentTypeComboBox.currentText().startswith("NXdetector")
            and self.meshRadioButton.isChecked()
        )
        pixel_grid_condition = (
            pixel_layout_condition and self.repeatableGridRadioButton.isChecked()
        )
        pixel_mapping_condition = (
            pixel_layout_condition and self.faceMappedMeshRadioButton.isChecked()
        )

        return (pixel_layout_condition, pixel_grid_condition, pixel_mapping_condition)

    def change_pixel_options_visibility(self):
        """
        Changes the visibility of the pixel-related fields and the box that contains them. First checks if any of the
        fields need to be shown then uses this to determine if the box is needed. After that the visibility of the box
        and individual fields is set.
        """
        pixel_layout_condition, pixel_grid_condition, pixel_mapping_condition = (
            self.pixel_options_conditions()
        )

        # Only make the pixel box appear based on the pixel layout and pixel data options being visible. The pixel grid
        # and mapping options already depend on pixel layout being visible.
        self.pixelOptionsBox.setVisible(pixel_layout_condition)

        # Set visibility for the components of the pixel options box
        self.pixelLayoutBox.setVisible(pixel_layout_condition)
        self.pixelGridBox.setVisible(pixel_grid_condition)
        self.pixelMappingLabel.setVisible(pixel_mapping_condition)
        self.pixelMappingListWidget.setVisible(pixel_mapping_condition)

        # Populate the pixel mapping list if it is visible but empty
        self.populate_pixel_mapping_list_when_empty(pixel_mapping_condition)

    def show_cylinder_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(True)
        self.change_pixel_options_visibility()

    def show_no_geometry_fields(self):
        self.geometryOptionsBox.setVisible(False)
        self.change_pixel_options_visibility()
        if self.nameLineEdit.text():
            self.buttonBox.setEnabled(True)

    def show_mesh_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)
        self.change_pixel_options_visibility()

    def generate_geometry_model(self, component: Component) -> OFFGeometry:
        """
        Generates a geometry model depending on the type of geometry selected and the current values
        of the lineedits that apply to the particular geometry type.
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
            )
        elif self.meshRadioButton.isChecked():
            mesh_geometry = OFFGeometryNoNexus()
            geometry_model = load_geometry(
                self.geometry_file_name, self.unitsLineEdit.text(), mesh_geometry
            )

            # Units have already been used during loading the file, but we store them and file name
            # so we can repopulate their fields in the edit component window
            geometry_model.units = self.unitsLineEdit.text()
            geometry_model.file_path = self.geometry_file_name

            component.set_off_shape(geometry_model)
        else:
            geometry_model = NoShapeGeometry()

        return geometry_model

    def generate_pixel_data(self):
        """
        Creates the appropriate PixelModel object depending on user selection then gives it the information that the
        user entered in the relevant fields.
        :return:
        """
        # Determine which type of PixelMapping object ought to be created.
        _, pixel_grid_condition, pixel_mapping_condition = (
            self.pixel_options_conditions()
        )

        if pixel_grid_condition:
            pixel_data = PixelGrid()
            pixel_data.rows = int(self.rowLineEdit.text())
            pixel_data.columns = int(self.columnsLineEdit.text())
            pixel_data.row_height = float(self.rowHeightLineEdit.text())
            pixel_data.column_width = float(self.columnWidthLineEdit.text())
            pixel_data.first_id = int(self.firstIDLineEdit.text())
            pixel_data.count_direction = self.count_direction[
                self.countFirstComboBox.currentText()
            ]

            pixel_data.initial_count_corner = self.initial_count_corner[
                self.startCountingComboBox.currentText()
            ]

        elif pixel_mapping_condition:
            pixel_data = PixelMapping(self.get_pixel_mapping_ids())

        else:
            return None

        return pixel_data

    def on_ok(self):
        nx_class = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()
        component = self.instrument.add_component(component_name, nx_class, description)
        geometry = self.generate_geometry_model(component)
        pixel_data = self.generate_pixel_data()
        add_fields_to_component(component, self.fieldsListWidget)
        self.component_model.add_component(component)
        self.instrument.nexus.component_added.emit(self.nameLineEdit.text(), geometry)

        #
        # self.nexus_wrapper.add_component(
        #     nx_class,
        #     component_name,
        #     description,
        #     self.generate_geometry_model(),
        #     self.generate_pixel_data(),
        # )

    def populate_pixel_mapping_list(self):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file.
        """
        # Don't do this if a file hasn't been selected yet.
        if not self.geometry_file_name:
            return

        n_faces = None

        with open(self.geometry_file_name) as temp_off_file:
            faces = parse_off_file(temp_off_file)[1]
            n_faces = len(faces)

        # Clear the list widget in case it contains information from a previous file.
        self.pixel_mapping_widgets = []
        self.pixelMappingListWidget.clear()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        for i in range(n_faces):
            pixel_mapping_widget = PixelMappingWidget(self.pixelMappingListWidget, i)

            list_item = QListWidgetItem()
            list_item.setSizeHint(pixel_mapping_widget.sizeHint())

            self.pixelMappingListWidget.addItem(list_item)
            self.pixelMappingListWidget.setItemWidget(list_item, pixel_mapping_widget)

            # Keep the PixelMappingWidget so that its ID can be retrieved easily when making a PixelMapping object.
            self.pixel_mapping_widgets.append(pixel_mapping_widget)

    def get_pixel_mapping_ids(self):
        """
        :return: A list of the IDs for the current PixelMappingWidgets.
        """
        return [
            pixel_mapping_widget.get_id()
            for pixel_mapping_widget in self.pixel_mapping_widgets
        ]

    def populate_pixel_mapping_list_when_empty(self, pixel_mapping_condition):
        """
        Populates the pixel mapping list only if it is visible and empty.
        :param pixel_mapping_condition: The condition for showing the pixel mapping list.
        """
        if pixel_mapping_condition and not self.pixel_mapping_widgets:
            self.populate_pixel_mapping_list()
