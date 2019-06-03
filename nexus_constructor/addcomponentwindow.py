from PySide2.QtCore import QUrl
from PySide2.QtWidgets import QFileDialog

from nexus_constructor.qml_models import geometry_models
from ui.addcomponent import Ui_AddComponentDialog

from nexus_constructor.file_dialog_options import FILE_DIALOG_NATIVE


GEOMETRY_FILE_TYPES = "OFF Files (*.off, *.OFF);; STL Files (*.stl, *.STL)"


class AddComponentDialog(Ui_AddComponentDialog):
    def __init__(self, entry_group, components_list):
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

    def on_close(self):
        print("closing window")

    def on_ok(self):
        print("adding component")
