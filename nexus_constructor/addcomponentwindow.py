from PySide2.QtCore import QUrl
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QFileDialog, QDialogButtonBox, QToolTip
from nexus_constructor.qml_models.geometry_models import (
    CylinderModel,
    OFFModel,
    NoShapeModel,
)
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from ui.addcomponent import Ui_AddComponentDialog
from nexus_constructor.file_dialog_options import FILE_DIALOG_NATIVE
from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.validators import UnitValidator

import os

GEOMETRY_FILE_TYPES = "OFF Files (*.off, *.OFF);; STL Files (*.stl, *.STL)"
component_types_in_entry_group = ["NXdetector", "NXsample"]


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, entry_group, components_list: InstrumentModel):
        super(AddComponentDialog, self).__init__()
        self.units_validator = UnitValidator()
        self.entry_group = entry_group
        self.components_list = components_list
        self.geometry_model = None
        self.intvalidator = QIntValidator()
        self.component_types = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

    def setupUi(self, AddComponentDialog):
        super().setupUi(AddComponentDialog)

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

        self.componentTypeComboBox.currentIndexChanged.connect(
            self.on_component_type_change
        )

        # Set default geometry type to mesh and show the related mesh fields such as geometry file etc.
        self.noGeometryRadioButton.setChecked(True)
        self.show_no_geometry_fields()

        self.unitsLineEdit.setValidator(self.units_validator)
        self.unitsLineEdit.validator().validationSuccess.connect(self.tick_check_box)
        self.unitsLineEdit.validator().validationFailed.connect(self.untick_check_box)

        self.cylinderXLineEdit.setValidator(self.intvalidator)
        self.cylinderYLineEdit.setValidator(self.intvalidator)
        self.cylinderZLineEdit.setValidator(self.intvalidator)
        self.cylinderRadiusLineEdit.setValidator(self.intvalidator)
        self.cylinderHeightLineEdit.setValidator(self.intvalidator)

        self.componentTypeComboBox.addItems(list(self.component_types.keys()))

    def on_component_type_change(self):
        self.webEngineView.setUrl(
            QUrl(
                f"http://download.nexusformat.org/sphinx/classes/base_classes/{self.componentTypeComboBox.currentText()}.html"
            )
        )

    def tick_check_box(self):
        self.ticklabel.setText("✅")
        self.ticklabel.setToolTip("Unit valid")

    def untick_check_box(self):
        self.ticklabel.setText("❌")
        self.ticklabel.setToolTip("Unit not valid")

    def mesh_file_picker(self):
        options = QFileDialog.Options()
        options |= FILE_DIALOG_NATIVE
        fileName, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption="QFileDialog.getOpenFileName()",
            directory="",
            filter=f"{GEOMETRY_FILE_TYPES};;All Files (*)",
            options=options,
        )
        if fileName:
            self.fileLineEdit.setText(fileName)
            self.geometry_file_name = fileName

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
            geometry_model.cylinder.height = self.cylinderHeightLineEdit.text()
            geometry_model.cylinder.radius = self.cylinderRadiusLineEdit.text()
            geometry_model.cylinder.axis_direction.setX(self.cylinderXLineEdit.text())
            geometry_model.cylinder.axis_direction.setY(self.cylinderYLineEdit.text())
            geometry_model.cylinder.axis_direction.setZ(self.cylinderZLineEdit.text())
        if self.meshRadioButton.isChecked():
            geometry_model = OFFModel()
            geometry_model.set_units(self.unitsLineEdit.text())
            geometry_model.set_file(self.geometry_file_name)
        else:
            geometry_model = NoShapeModel()
        return geometry_model

    def on_ok(self):
        component_type = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text().replace(" ", "_")
        self.components_list.add_component(
            component_type=component_type,
            description=self.descriptionPlainTextEdit.text(),
            name=component_name,
            geometry_model=self.generate_geometry_model(),
        )

        instrument_group = self.entry_group["instrument"]

        if component_type in component_types_in_entry_group:
            # If the component should be put in entry rather than instrument
            instrument_group = self.entry_group

        component_group = instrument_group.create_group(component_name)
        component_group.attrs["NX_class"] = component_type

        # TODO: sort out transforms and pixel data

        # TODO: nexus stuff goes here

        print("adding component")
