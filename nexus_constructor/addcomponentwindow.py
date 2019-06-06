from PySide2.QtCore import QUrl, Signal
from PySide2.QtWidgets import QDialogButtonBox
from nexus_constructor.qml_models.geometry_models import (
    CylinderModel,
    OFFModel,
    NoShapeModel,
)
from PySide2.QtGui import QValidator
from ui.addcomponent import Ui_AddComponentDialog
from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.validators import UnitValidator, NameValidator
from nexus_constructor.nexus_wrapper import NexusWrapper
from nexus_constructor.utils import file_dialog
import os
from functools import partial

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


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, nexus_wrapper: NexusWrapper):
        super(AddComponentDialog, self).__init__()
        self.nexus_wrapper = nexus_wrapper
        self.geometry_model = None
        self.component_types = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

    def setupUi(self, parent_dialog):
        super().setupUi(parent_dialog)

        # Connect the button calls with functions
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.on_ok)

        # Grey out OK button by default to prevent users from adding components with invalid fields
        # TODO: enable this when all fields are valid
        # self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        # Set default URL to nexus base classes in web view
        self.webEngineView.setUrl(
            QUrl(
                "http://download.nexusformat.org/doc/html/classes/base_classes/index.html"
            )
        )

        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.CylinderRadioButton.clicked.connect(self.show_cylinder_fields)
        self.noGeometryRadioButton.clicked.connect(self.show_no_geometry_fields)
        self.fileBrowseButton.clicked.connect(self.mesh_file_picker)

        self.fileLineEdit.setValidator(FileValidator(GEOMETRY_FILE_TYPES))
        self.fileLineEdit.validator().isValid.connect(partial(self.validate_line_edit, self.fileLineEdit))

        self.componentTypeComboBox.currentIndexChanged.connect(
            self.on_component_type_change
        )

        # Set default geometry type to mesh and show the related mesh fields such as geometry file etc.
        self.noGeometryRadioButton.setChecked(True)
        self.show_no_geometry_fields()

        name_validator = NameValidator()
        name_validator.list_model = self.nexus_wrapper.get_component_list()
        self.nameLineEdit.setValidator(name_validator)
        self.nameLineEdit.validator().isValid.connect(partial(self.validate_line_edit, self.nameLineEdit))

        self.unitsLineEdit.setValidator(UnitValidator())
        self.unitsLineEdit.validator().isValid.connect(self.validate_units)

        self.componentTypeComboBox.addItems(list(self.component_types.keys()))

    def validate_line_edit(self, line_edit, is_valid: bool):
        colour = "#FFFFFF" if is_valid else "#f6989d"
        line_edit.setStyleSheet(f"QLineEdit {{ background-color: {colour} }}")

    def on_component_type_change(self):
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{self.componentTypeComboBox.currentText()}.html"
            )
        )

    def validate_units(self, is_valid):
        self.ticklabel.setText("✅" if is_valid else "❌")
        self.ticklabel.setToolTip("Unit valid" if is_valid else "Unit not valid")

    def mesh_file_picker(self):
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
