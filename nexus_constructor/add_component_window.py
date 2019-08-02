import os
from enum import Enum
from functools import partial

from PySide2.QtCore import QUrl, Signal, QObject
from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QListWidgetItem

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
from nexus_constructor.pixel_options import PixelOptions
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

        self.instrument = instrument
        self.component_model = component_model

        self.geometry_model = None
        _, self.nx_component_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

        self.cad_file_name = None

        self.possible_fields = []
        self.component_to_edit = component_to_edit

        self.pixel_options = PixelOptions(self)

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

        self.meshRadioButton.clicked.connect(self.pixel_options.update)
        self.CylinderRadioButton.clicked.connect(self.pixel_options.update)
        self.noShapeRadioButton.clicked.connect(self.pixel_options.update)

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
            self.pixel_options.update
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

        if self.component_to_edit:
            self._fill_existing_entries()

        self.pixel_options.setup_ui()

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
        self.pixel_options.update()

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

    def on_ok(self):
        nx_class = self.componentTypeComboBox.currentText()
        component_name = self.nameLineEdit.text()
        description = self.descriptionPlainTextEdit.text()
        pixel_data = self.pixel_options.generate_pixel_data()

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
                component_name, nx_class, description, pixel_data
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
