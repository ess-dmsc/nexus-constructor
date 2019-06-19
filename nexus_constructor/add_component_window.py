from enum import Enum

from PySide2.QtCore import QUrl
from PySide2.QtGui import QIntValidator, QDoubleValidator

from nexus_constructor.qml_models.geometry_models import (
    CylinderModel,
    OFFModel,
    NoShapeModel,
)
from ui.add_component import Ui_AddComponentDialog
from nexus_constructor.component_type import (
    make_dictionary_of_class_definitions,
    PIXEL_COMPONENT_TYPES,
)
from nexus_constructor.validators import (
    UnitValidator,
    NameValidator,
    GeometryFileValidator,
    GEOMETRY_FILE_TYPES,
    OkValidator,
    NullableIntValidator,
)
from nexus_constructor.nexus_wrapper import NexusWrapper
from nexus_constructor.utils import file_dialog, validate_line_edit
import os
from functools import partial


class GeometryType(Enum):
    NONE = 1
    CYLINDER = 2
    MESH = 3


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, nexus_wrapper: NexusWrapper):
        super(AddComponentDialog, self).__init__()
        self.nexus_wrapper = nexus_wrapper
        self.geometry_model = None
        self.nx_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

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

        name_validator = NameValidator()
        name_validator.list_model = self.nexus_wrapper.get_component_list()
        self.nameLineEdit.setValidator(name_validator)
        self.nameLineEdit.validator().is_valid.connect(
            partial(validate_line_edit, self.nameLineEdit)
        )

        validate_line_edit(self.nameLineEdit, False)
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

        self.componentTypeComboBox.addItems(list(self.nx_classes.keys()))

        # Validate the default value set by the UI
        self.unitsLineEdit.validator().validate(self.unitsLineEdit.text(), 0)

        self.detectorIdLineEdit.setValidator(NullableIntValidator())

        # Instruct the pixel grid box to appear or disappear depending on the pixel layout setting
        self.repeatableGridRadioButton.clicked.connect(
            lambda: self.pixelGridBox.setVisible(True)
        )
        self.faceMappedMeshRadioButton.clicked.connect(
            lambda: self.pixelGridBox.setVisible(False)
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

    def on_nx_class_changed(self):
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{self.componentTypeComboBox.currentText()}.html"
            )
        )
        self.pixelLayoutBox.setVisible(
            self.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES
        )

        self.change_pixel_options_visibility()

    def mesh_file_picker(self):
        """
        Opens the mesh file picker. Sets the file name line edit to the file path.
        :return: None
        """
        filename = file_dialog(False, "Open Mesh", GEOMETRY_FILE_TYPES)
        if filename:
            self.fileLineEdit.setText(filename)
            self.geometry_file_name = filename

    def change_pixel_options_visibility(self):
        """
        Changes the visibility of the pixel-related fields and the box that contains them. First checks if any of the
        fields need to be shown then uses this to determine if the box is needed. After that the visibility of the box
        and then the fields is set.
        """
        pixel_layout_condition = (
            self.componentTypeComboBox.currentText() == "NXdetector"
            and self.meshRadioButton.isChecked()
        )
        pixel_data_condition = (
            not self.noGeometryRadioButton.isChecked()
            and self.componentTypeComboBox.currentText() == "NXmonitor"
        )
        pixel_grid_condition = (
            pixel_layout_condition and self.repeatableGridRadioButton.isChecked()
        )

        """
        Only make the pixel box appear based on layout fields and data fields because the grid and mapping options
        already depend on pixel layout being visible.
        """
        self.pixelOptionsBox.setVisible(pixel_layout_condition or pixel_data_condition)

        # Set visibility for the components of the pixel options box
        self.pixelLayoutBox.setVisible(pixel_layout_condition)
        self.pixelDataBox.setVisible(pixel_data_condition)
        self.pixelGridBox.setVisible(pixel_grid_condition)

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

    def generate_geometry_model(self):
        """
        Generates a geometry model depending on the type of geometry selected and the current values of the lineedits that apply to the particular geometry type.
        :return: The generated model.
        """
        if self.CylinderRadioButton.isChecked():
            geometry_model = CylinderModel()
            geometry_model.set_unit(self.unitsLineEdit.text())
            geometry_model.cylinder.height = self.cylinderHeightLineEdit.value()
            geometry_model.cylinder.radius = self.cylinderRadiusLineEdit.value()
            geometry_model.cylinder.axis_direction.setX(self.cylinderXLineEdit.value())
            geometry_model.cylinder.axis_direction.setY(self.cylinderYLineEdit.value())
            geometry_model.cylinder.axis_direction.setZ(self.cylinderZLineEdit.value())
        if self.meshRadioButton.isChecked():
            geometry_model = OFFModel()
            geometry_model.set_units(self.unitsLineEdit.text())
            geometry_model.set_file(self.geometry_file_name)
        else:
            geometry_model = NoShapeModel()
        return geometry_model

    def on_ok(self):
        nx_class = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()
        self.nexus_wrapper.add_component(
            nx_class, component_name, description, self.generate_geometry_model()
        )
