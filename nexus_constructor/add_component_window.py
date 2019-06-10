from enum import Enum

from PySide2.QtCore import QUrl, Signal, QObject
from PySide2.QtWidgets import QDialogButtonBox
from nexus_constructor.qml_models.geometry_models import (
    CylinderModel,
    OFFModel,
    NoShapeModel,
)
from PySide2.QtGui import QValidator
from ui.add_component import Ui_AddComponentDialog
from nexus_constructor.component_type import (
    make_dictionary_of_class_definitions,
    PIXEL_COMPONENT_TYPES,
)
from nexus_constructor.validators import UnitValidator, NameValidator
from nexus_constructor.nexus_wrapper import NexusWrapper
from nexus_constructor.utils import file_dialog, validate_line_edit
import os
from functools import partial

# TODO: stop enter closing the dialog
GEOMETRY_FILE_TYPES = {"OFF Files": ["off", "OFF"], "STL Files": ["stl", "STL"]}


class FileValidator(QValidator):
    """
    Validator to ensure file exists and is the correct file type.
    """

    def __init__(self, file_types):
        """

        :param file_types:
        """
        super().__init__()
        self.file_types = file_types

    def validate(self, input: str, pos: int):
        if not input:
            self.isValid.emit(False)
            return QValidator.Intermediate
        if not os.path.isfile(input):
            self.isValid.emit(False)
            return QValidator.Intermediate
        for suffixes in GEOMETRY_FILE_TYPES.values():
            for suff in suffixes:
                if input.endswith(f".{suff}"):
                    self.isValid.emit(True)
                    return QValidator.Acceptable
        self.isValid.emit(False)
        return QValidator.Invalid

    isValid = Signal(bool)


class GeometryType(Enum):
    NONE = 1
    CYLINDER = 2
    MESH = 3


class OkValidator(QObject):
    """
    Validator to enable the OK button. Several criteria have to be met before this can occur depending on the geometry type.
    """

    def __init__(self, no_geometry_button, mesh_button):
        super().__init__()
        self.name_is_valid = False
        self.file_is_valid = False
        self.units_are_valid = False
        self.no_geometry_button = no_geometry_button
        self.mesh_button = mesh_button

    def set_name_valid(self, is_valid):
        self.name_is_valid = is_valid
        print("Name: {}".format(self.name_is_valid))
        self.validate_ok()

    def set_file_valid(self, is_valid):
        self.file_is_valid = is_valid
        print("File: {}".format(self.file_is_valid))
        self.validate_ok()

    def set_units_valid(self, is_valid):
        self.units_are_valid = is_valid
        print("Units: {}".format(self.units_are_valid))
        self.validate_ok()

    def validate_ok(self):
        """
        Validates the fields in order to dictate whether the OK button should be disabled or enabled.
        :return: None, but emits the isValid signal.
        """
        unacceptable = [
            not self.name_is_valid,
            not self.no_geometry_button.isChecked() and not self.units_are_valid,
            self.mesh_button.isChecked() and not self.file_is_valid,
        ]

        print("Is valid {}".format(unacceptable))
        self.isValid.emit(not any(unacceptable))

    # Signal to indicate that the fields are valid or invalid. False: invalid.
    isValid = Signal(bool)


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, nexus_wrapper: NexusWrapper):
        super(AddComponentDialog, self).__init__()
        self.nexus_wrapper = nexus_wrapper
        self.geometry_model = None
        self.component_types = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

    def setupUi(self, parent_dialog):
        """ Sets up push buttons and validators for the add component window. """
        super().setupUi(parent_dialog)

        # Connect the button calls with functions
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok)

        # Disable by default as component name will be missing at the very least.
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        # Set default URL to nexus base classes in web view
        self.webEngineView.setUrl(
            QUrl(
                "http://download.nexusformat.org/doc/html/classes/base_classes/index.html"
            )
        )

        self.ok_validator = OkValidator(
            self.noGeometryRadioButton, self.meshRadioButton
        )
        self.ok_validator.isValid.connect(
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled
        )

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

        self.fileLineEdit.setValidator(FileValidator(GEOMETRY_FILE_TYPES))
        self.fileLineEdit.validator().isValid.connect(
            partial(validate_line_edit, self.fileLineEdit)
        )
        self.fileLineEdit.validator().isValid.connect(self.ok_validator.set_file_valid)

        self.componentTypeComboBox.currentIndexChanged.connect(
            self.on_component_type_change
        )

        # Set default geometry type and show the related fields.
        self.noGeometryRadioButton.setChecked(True)
        self.show_no_geometry_fields()

        name_validator = NameValidator()
        name_validator.list_model = self.nexus_wrapper.get_component_list()
        self.nameLineEdit.setValidator(name_validator)
        self.nameLineEdit.validator().isValid.connect(
            partial(validate_line_edit, self.nameLineEdit)
        )

        validate_line_edit(self.nameLineEdit, False)
        validate_line_edit(self.fileLineEdit, False)

        self.nameLineEdit.validator().isValid.connect(self.ok_validator.set_name_valid)

        self.unitsLineEdit.setValidator(UnitValidator())
        self.unitsLineEdit.validator().isValid.connect(
            partial(
                validate_line_edit,
                self.unitsLineEdit,
                tooltip_on_reject="Units not valid",
                tooltip_on_accept="Units Valid",
            )
        )
        self.unitsLineEdit.validator().isValid.connect(
            self.ok_validator.set_units_valid
        )

        self.componentTypeComboBox.addItems(list(self.component_types.keys()))

    def on_component_type_change(self):
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{self.componentTypeComboBox.currentText()}.html"
            )
        )
        self.pixelOptionsBox.setVisible(
            self.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES
        )

    def mesh_file_picker(self):
        """
        Opens the mesh file picker. Sets the file name line edit to the file path.
        :return: None
        """
        filename = file_dialog(False, "Open Mesh", GEOMETRY_FILE_TYPES)
        if filename:
            self.fileLineEdit.setText(filename)
            self.geometry_file_name = filename

    def show_cylinder_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(True)

    def show_no_geometry_fields(self):
        self.geometryOptionsBox.setVisible(False)
        if self.nameLineEdit.text():
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def show_mesh_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)

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
        component_type = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()
        self.nexus_wrapper.add_component(
            component_type, component_name, description, self.generate_geometry_model()
        )
