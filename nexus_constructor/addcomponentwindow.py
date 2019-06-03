from PySide2.QtCore import QUrl
from PySide2.QtWidgets import QFileDialog

from nexus_constructor.qml_models import geometry_models
from nexus_constructor.qml_models.geometry_models import (
    CylinderModel,
    OFFModel,
    NoShapeModel,
)
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from ui.addcomponent import Ui_AddComponentDialog

from nexus_constructor.file_dialog_options import FILE_DIALOG_NATIVE


GEOMETRY_FILE_TYPES = "OFF Files (*.off, *.OFF);; STL Files (*.stl, *.STL)"


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, entry_group, components_list: InstrumentModel):
        super(AddComponentDialog, self).__init__()
        self.entry_group = entry_group
        self.components_list = components_list
        self.geometry_model = None

    def setupUi(self, AddComponentDialog):
        super().setupUi(AddComponentDialog)
        self.buttonBox.rejected.connect(self.on_close)
        self.buttonBox.accepted.connect(self.on_ok)
        self.webView.setUrl(
            QUrl(
                "http://download.nexusformat.org/doc/html/classes/base_classes/index.html"
            )
        )
        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.CylinderRadioButton.clicked.connect(self.show_cylinder_fields)
        self.noGeometryRadioButton.clicked.connect(self.show_no_geometry_fields)
        self.fileBrowseButton.clicked.connect(self.mesh_file_picker)

        self.meshRadioButton.setChecked(True)
        self.show_mesh_fields()

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
            with open(fileName) as geometry_file:
                self.load_geometry_from_file_object(geometry_file)

    def load_geometry_from_file_object(self, file_object):
        self.geometry_model = geometry_models.OFFModel()
        pass

    def show_cylinder_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(True)

    def show_no_geometry_fields(self):
        self.geometryOptionsBox.setVisible(False)

    def show_mesh_fields(self):
        self.geometryOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)

    def generate_geometry_model(self):
        if self.CylinderRadioButton.isChecked():
            geometry_model = CylinderModel()
            geometry_model.cylinder.height = self.cylinderHeightLineEdit.text()
            geometry_model.cylinder.radius = self.cylinderRadiusLineEdit.text()
            geometry_model.cylinder.axis_direction.setX(self.cylinderXLineEdit.text())
            geometry_model.cylinder.axis_direction.setY(self.cylinderYLineEdit.text())
            geometry_model.cylinder.axis_direction.setZ(self.cylinderZLineEdit.text())
        if self.meshRadioButton.isChecked():
            geometry_model = OFFModel()
            # TODO: set geometry up
        else:
            geometry_model = NoShapeModel()
        return geometry_model

    def on_close(self):
        print("closing window")

    def on_ok(self):
        self.components_list.add_component(
            component_type=self.componentTypeComboBox.currentText(),
            description=self.descriptionPlainTextEdit.toPlainText(),
            name=self.nameLineEdit.text().replace(" ", "_"),
            geometry_model=self.generate_geometry_model(),
        )
        # TODO: sort out transforms and pixel data

        # TODO: nexus stuff goes here

        print("adding component")
