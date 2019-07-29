import os
from enum import Enum
from functools import partial

from PySide2.QtCore import QUrl, Signal, QObject
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QListWidgetItem, QDoubleSpinBox, QSpinBox
from nexusutils.readwriteoff import parse_off_file

from nexus_constructor.component import Component
from nexus_constructor.component_fields import FieldWidget, add_fields_to_component
from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_type import (
    make_dictionary_of_class_definitions,
    PIXEL_COMPONENT_TYPES,
)
from nexus_constructor.geometry import CylindricalGeometry, OFFGeometryNexus
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

        # Dictionaries that map user-input to known pixel grid options. Used when created the PixelGridModel.
        self.count_direction = {
            "Rows": CountDirection.ROW,
            "Columns": CountDirection.COLUMN,
        }
        self.initial_count_corner = {
            "Bottom Left": Corner.BOTTOM_LEFT,
            "Bottom Right": Corner.BOTTOM_RIGHT,
            "Top Left": Corner.TOP_LEFT,
            "Top Right": Corner.TOP_RIGHT,
        }

        self.instrument = instrument
        self.component_model = component_model

        self.geometry_model = None
        _, self.nx_component_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

        self.cad_file_name = None
        self.pixel_mapping_widgets = []

        self.possible_fields = []
        self.component_to_edit = component_to_edit

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
            self.noShapeRadioButton,
            self.meshRadioButton,
            self.pixelOptionsBox,
            self.singlePixelRadioButton,
            self.entireShapeRadioButton,
        )
        self.ok_validator.is_valid.connect(self.buttonBox.setEnabled)

        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.CylinderRadioButton.clicked.connect(self.show_cylinder_fields)
        self.noShapeRadioButton.clicked.connect(self.show_no_geometry_fields)
        self.fileBrowseButton.clicked.connect(self.mesh_file_picker)

        self.meshRadioButton.clicked.connect(self.update_pixel_options)
        self.CylinderRadioButton.clicked.connect(self.update_pixel_options)
        self.noShapeRadioButton.clicked.connect(self.update_pixel_options)

        [
            button.clicked.connect(self.ok_validator.validate_ok)
            for button in [
                self.meshRadioButton,
                self.CylinderRadioButton,
                self.noShapeRadioButton,
            ]
        ]

        self.fileLineEdit.setValidator(GeometryFileValidator(GEOMETRY_FILE_TYPES))
        self.fileLineEdit.validator().is_valid.connect(
            partial(validate_line_edit, self.fileLineEdit)
        )
        self.fileLineEdit.validator().is_valid.connect(self.ok_validator.set_file_valid)

        self.componentTypeComboBox.currentIndexChanged.connect(self.on_nx_class_changed)
        self.componentTypeComboBox.currentIndexChanged.connect(
            self.update_pixel_options
        )

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
        self.singlePixelRadioButton.clicked.connect(
            lambda: self.show_pixel_grid_or_pixel_mapping(True)
        )
        self.entireShapeRadioButton.clicked.connect(
            lambda: self.show_pixel_grid_or_pixel_mapping(False)
        )

        # Make both the pixel grid and pixel mapping options invisible when the No Pixel button has been pressed
        self.noPixelsButton.clicked.connect(self.hide_pixel_grid_and_mapping)

        self.pixelMappingLabel.setVisible(False)
        self.pixelMappingListWidget.setVisible(False)

        self.countFirstComboBox.addItems(list(self.count_direction.keys()))

        self.rowCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.rowCountSpinBox, self.rowHeightSpinBox
            )
        )
        self.columnCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.columnCountSpinBox, self.columnWidthSpinBox
            )
        )

        if self.component_to_edit:
            self._fill_existing_entries()

    def disable_or_enable_size_field(
        self, count_spin_box: QSpinBox, size_spin_box: QDoubleSpinBox
    ):
        size_spin_box.setEnabled(count_spin_box.value() != 0)
        self.forbid_both_row_and_columns_being_zero()

    def forbid_both_row_and_columns_being_zero(self):

        RED_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #f6989d }"
        WHITE_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #FFFFFF }"

        if self.rowCountSpinBox.value() == 0 and self.columnCountSpinBox.value() == 0:
            self.rowCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.ok_validator.set_pixel_grid_valid(False)
        else:
            self.rowCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.ok_validator.set_pixel_grid_valid(True)

    def _fill_existing_entries(self):
        self.buttonBox.setText("Edit Component")
        self.nameLineEdit.setText(self.component_to_edit.name)
        self.descriptionPlainTextEdit.setText(self.component_to_edit.description)
        self.componentTypeComboBox.setCurrentText(self.component_to_edit.nx_class)
        component_shape = self.component_to_edit.get_shape()
        if not component_shape or isinstance(component_shape, OFFGeometryNoNexus):
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

        # TODO: fields

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
        self.update_pixel_options()

    def hide_pixel_grid_and_mapping(self):
        """
        Hides the pixel grid and pixel mapping options when the No Pixel button has been selected.
        """

        self.pixelGridBox.setVisible(False)
        self.pixelMappingLabel.setVisible(False)
        self.pixelMappingListWidget.setVisible(False)

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
        if filename != self.cad_file_name:
            self.fileLineEdit.setText(filename)
            self.cad_file_name = filename
        else:
            return

        _, _, pixel_mapping_condition = self.pixel_options_conditions()

        if pixel_mapping_condition:
            self.populate_pixel_mapping_list()

    def pixel_options_conditions(self):
        """
        Determine which of the pixel-related fields need to be visible.
        :return: Booleans indicating whether the pixel layout, pixel grid, and pixel mapping options need to
        be made visible.
        """

        pixel_options_condition = self.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES and (
            self.meshRadioButton.isChecked() or self.CylinderRadioButton.isChecked()
        )
        pixel_grid_condition = (
            pixel_options_condition and self.singlePixelRadioButton.isChecked()
        )
        pixel_mapping_condition = (
            pixel_options_condition and self.entireShapeRadioButton.isChecked()
        )

        return pixel_options_condition, pixel_grid_condition, pixel_mapping_condition

    def update_pixel_options(self):

        pixel_options_condition, pixel_grid_condition, pixel_mapping_condition = (
            self.pixel_options_conditions()
        )
        self.change_pixel_options_visibility(
            pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
        )

    def change_pixel_options_visibility(
        self, pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
    ):
        """
        Changes the visibility of the pixel-related fields and the box that contains them. First checks if any of the
        fields need to be shown then uses this to determine if the box is needed. After that the visibility of the box
        and individual fields is set.
        """

        # Only make the pixel box appear based on the pixel layout and pixel data options being visible. The pixel grid
        # and mapping options already depend on pixel layout being visible.
        self.pixelOptionsBox.setVisible(pixel_options_condition)

        # Set visibility for the components of the pixel options box
        self.pixelLayoutBox.setVisible(pixel_options_condition)
        self.pixelGridBox.setVisible(pixel_grid_condition)
        self.pixelMappingLabel.setVisible(pixel_mapping_condition)
        self.pixelMappingListWidget.setVisible(pixel_mapping_condition)

        # Populate the pixel mapping list if it is visible but empty
        self.populate_pixel_mapping_list_when_empty(pixel_mapping_condition)

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
            )
        else:
            geometry_model = NoShapeGeometry()
            component.remove_shape()

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
            pixel_data.rows = self.rowCountSpinBox.value()
            pixel_data.columns = self.columnCountSpinBox.value()
            pixel_data.row_height = self.rowHeightSpinBox.value()
            pixel_data.column_width = self.columnWidthLineEdit.value()
            pixel_data.first_id = self.firstIDSpinBox.value()
            pixel_data.count_direction = self.count_direction[
                self.countFirstComboBox.currentText()
            ]

            pixel_data.initial_count_corner = self.initial_count_corner[
                self.startCountingComboBox.currentText()
            ]

            return pixel_data

        elif pixel_mapping_condition:
            return PixelMapping(self.get_pixel_mapping_ids())

        else:
            return None

    def on_ok(self):
        nx_class = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()

        if self.component_to_edit:
            self.component_to_edit.name = component_name
            self.component_to_edit.nx_class = nx_class
            self.component_to_edit.description = description
            # remove the previous shape from the qt3d view
            if self.component_to_edit.get_shape() and self.parent():
                self.parent().sceneWidget.delete_component(self.component_to_edit.name)
            geometry = self.generate_geometry_model(self.component_to_edit)
        else:
            component = self.instrument.create_component(
                component_name, nx_class, description
            )
            geometry = self.generate_geometry_model(component)
            add_fields_to_component(component, self.fieldsListWidget)
            self.component_model.add_component(component)

        self.instrument.nexus.component_added.emit(self.nameLineEdit.text(), geometry)

    def invalid_file_given(self):
        """
        Checks if the current mesh file is valid. If it is invalid and pixel mapping has been chosen, then a pixel
        mapping list won't be generated.
        :return: A bool indicating whether or not the file line edit has a red background.
        """
        return (
            self.fileLineEdit.styleSheet() == "QLineEdit { background-color: #f6989d }"
        )

    def check_pixel_mapping(self):

        nonempty_ids = [widget.get_id() != "" for widget in self.pixel_mapping_widgets]
        self.ok_validator.set_pixel_mapping_valid(any(nonempty_ids))

    def populate_pixel_mapping_list(self):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file.
        """
        # Don't do this if a file hasn't been selected yet or if the file given is invalid
        if not self.cad_file_name or self.invalid_file_given():
            return

        n_faces = None

        with open(self.cad_file_name) as temp_off_file:
            faces = parse_off_file(temp_off_file)[1]
            n_faces = len(faces)

        # Clear the list widget in case it contains information from a previous file.
        self.pixel_mapping_widgets = []
        self.pixelMappingListWidget.clear()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        for i in range(n_faces):
            pixel_mapping_widget = PixelMappingWidget(self.pixelMappingListWidget, i)
            pixel_mapping_widget.pixelIDLineEdit.textChanged.connect(
                self.check_pixel_mapping
            )

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
