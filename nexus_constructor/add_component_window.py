from collections import OrderedDict
from copy import deepcopy
from functools import partial
from os import path
from typing import Callable, List

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QKeyEvent, QVector3D
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox, QWidget

from nexus_constructor.common_attrs import NX_CLASSES_WITH_PLACEHOLDERS, CommonAttrs
from nexus_constructor.component_tree_model import NexusTreeModel
from nexus_constructor.component_type import (
    COMPONENT_TYPES,
    PIXEL_COMPONENT_TYPES,
    STREAM_MODULE_GROUPS,
)
from nexus_constructor.field_utils import (
    add_required_component_fields,
    get_fields_with_update_functions,
)
from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.geometry.pixel_data import PixelData, PixelGrid, PixelMapping
from nexus_constructor.instrument_view.instrument_view import SPECIAL_SHAPE_CASES
from nexus_constructor.model import Group, GroupContainer
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import (
    BoxGeometry,
    CylindricalGeometry,
    NoShapeGeometry,
    OFFGeometryNexus,
    OFFGeometryNoNexus,
)
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset, Link, FileWriter
from nexus_constructor.pixel_options import PixelOptions
from nexus_constructor.ui_utils import (
    file_dialog,
    show_warning_dialog,
    validate_line_edit,
)
from nexus_constructor.unit_utils import METRES
from nexus_constructor.validators import (
    GEOMETRY_FILE_TYPES,
    SKIP_VALIDATION,
    GeometryFileValidator,
    OkValidator,
    UnitValidator,
)
from ui.add_component import Ui_AddComponentDialog


class AddComponentDialog(Ui_AddComponentDialog):
    nx_class_changed = Signal("QVariant")
    suggest_group_name_from_parent_fields = Signal("QVariant")

    def __init__(
        self,
        parent: QWidget,
        model: Model,
        component_model: NexusTreeModel,
        group_to_edit: Group,
        scene_widget: QWidget,
        initial_edit: bool,
        nx_classes=None,
        tree_view_updater: Callable = None,
    ):
        self._tree_view_updater = tree_view_updater
        self._scene_widget = scene_widget
        self._group_to_edit_backup: Group = deepcopy(group_to_edit)
        self._group_container = GroupContainer(group_to_edit)
        self._group_parent = group_to_edit.parent_node
        file_dir = path.dirname(__file__)
        self.local_url_root = path.join(
            file_dir,
            "..",
            "nx-class-documentation",
            "html",
            "classes",
            "base_classes",
        )
        super().__init__(parent, self._group_container)
        super().setupUi()
        if nx_classes is None:
            nx_classes = {}
        self.signals = model.signals
        self.model = model
        self.component_model = component_model
        self.nx_component_classes = OrderedDict(sorted(nx_classes.items()))

        self.cad_file_name = None
        self.possible_fields: List[str] = []
        self.initial_edit = initial_edit
        self.valid_file_given = False
        self.pixel_options: PixelOptions = None
        self.setupUi()
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        if self.initial_edit:
            self.ok_button.setText("Add group")
            self.cancel_button.setVisible(True)
            self.componentTypeComboBox.currentIndexChanged.connect(
                self._handle_class_change
            )
            self.cancel_button.clicked.connect(self._cancel_new_group)
            self.rejected.connect(self._rejected)
        else:
            self.cancel_button.setVisible(True)
            self.cancel_button.clicked.connect(self._cancel_edit_group)

    def _rejected(self):
        if self.initial_edit:
            self._group_parent.children.remove(self._group_container.group)

    def _confirm_cancel(self) -> bool:
        quit_msg = "Do you want to close the group editor?"
        reply = QMessageBox.question(
            self,
            "Really quit?",
            quit_msg,
            QMessageBox.Close | QMessageBox.Ignore,
            QMessageBox.Close,
        )
        if reply == QMessageBox.Close:
            return True
        return False

    def _cancel_new_group(self):
        if self._confirm_cancel():
            group, _ = self.component_model.current_nxs_obj
            if isinstance(group, Group):
                self._refresh_tree(group)
            else:
                self._refresh_tree(self._group_to_edit_backup)
            self.close()

    def _cancel_edit_group(self):
        if self._confirm_cancel():
            if self._group_parent:
                self._group_parent.children.remove(self._group_container.group)
                self._group_parent[self._group_to_edit_backup.name] = (
                    self._group_to_edit_backup
                )
            else:
                self.model.entry = self._group_to_edit_backup  # type: ignore
                self.component_model.tree_root = self.model.entry
            self._refresh_tree(self._group_to_edit_backup)
            self.close()

    def _refresh_tree(self, group: Group):
        if self._tree_view_updater:
            self._tree_view_updater(group)

    def _handle_class_change(self):
        c_nx_class = self.componentTypeComboBox.currentText()
        c_attributes = self._group_container.group.attributes
        c_name = self._group_container.group.name
        c_children = self._group_container.group.children
        group_constructor = None
        if (
            isinstance(self._group_container.group, Component)
            and c_nx_class not in COMPONENT_TYPES
        ):
            group_constructor = Group
        elif (
            not isinstance(self._group_container.group, Component)
            and c_nx_class in COMPONENT_TYPES
        ):
            group_constructor = Component
        if group_constructor:
            self._group_parent.children.remove(self._group_container.group)
            self._group_container.group = group_constructor(
                name=c_name, parent_node=self._group_parent
            )
            self._group_container.group.attributes = c_attributes
            self._group_container.group.children = c_children
            self._group_container.group.nx_class = c_nx_class
            self._group_parent.children.append(self._group_container.group)

    def setupUi(self, pixel_options: PixelOptions = PixelOptions()):
        """Sets up push buttons and validators for the add component window."""

        # Connect the button calls with functions
        self.ok_button.clicked.connect(self.on_ok)

        # Disable by default as component name will be missing at the very least.
        self.ok_button.setEnabled(False)
        self.placeholder_checkbox.stateChanged.connect(self._disable_fields_and_buttons)
        self.meshRadioButton.clicked.connect(self.show_mesh_fields)
        self.boxRadioButton.clicked.connect(self.show_box_fields)
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

        validate_line_edit(self.fileLineEdit, False)

        self.unitsLineEdit.setValidator(UnitValidator(expected_dimensionality=METRES))
        self.unitsLineEdit.validator().is_valid.connect(
            partial(
                validate_line_edit,
                self.unitsLineEdit,
                tooltip_on_reject="Units not valid",
                tooltip_on_accept="Units Valid",
            )
        )

        self.componentTypeComboBox.currentIndexChanged.connect(
            self.change_pixel_options_visibility
        )

        # Set whatever the default nx_class is so the fields autocompleter can use the possible fields in the nx_class
        self.nx_class_changed.connect(self.set_shape_button_visibility)
        self.on_nx_class_changed()

        self.fieldsListWidget.itemClicked.connect(self.select_field)

        self.pixel_options = pixel_options
        if self.pixel_options:
            self.pixel_options.setupUi(self.pixelOptionsWidget)
        self.pixelOptionsWidget.ui = self.pixel_options

        self.ok_validator = OkValidator(
            self.noShapeRadioButton,
            self.meshRadioButton,
            self.pixel_options.validator,
            self.fieldsListWidget,
        )
        self.nx_class_changed.connect(self.__add_required_fields)
        self.suggest_group_name_from_parent_fields.connect(
            self.nameLineEdit.update_possible_fields
        )

        c_group = self._group_container.group

        if not self.initial_edit:
            self.setWindowTitle(f"Edit group: {c_group.name}")
            self.placeholder_checkbox.setChecked(c_group.group_placeholder)

            self._fill_existing_entries()
            if (
                self.get_pixel_visibility_condition()
                and self.pixel_options
                and isinstance(c_group, Component)
            ):
                self.pixel_options.fill_existing_entries(c_group)
            if c_group.nx_class in NX_CLASSES_WITH_PLACEHOLDERS:
                self.placeholder_checkbox.setVisible(True)
        else:
            self.ok_validator.set_nx_class_valid(False)

        self.componentTypeComboBox.validator().is_valid.connect(
            self.ok_validator.set_nx_class_valid
        )
        self.componentTypeComboBox.validator().validate(
            self.componentTypeComboBox.currentText(), 0
        )

        self.ok_validator.is_valid.connect(self.ok_button.setEnabled)

        self.nameLineEdit.validator().is_valid.connect(self.ok_validator.set_name_valid)

        [
            button.clicked.connect(self.ok_validator.validate_ok)
            for button in [
                self.meshRadioButton,
                self.CylinderRadioButton,
                self.noShapeRadioButton,
                self.boxRadioButton,
            ]
        ]

        self.unitsLineEdit.validator().is_valid.connect(
            self.ok_validator.set_units_valid
        )
        self.fileLineEdit.validator().is_valid.connect(self.ok_validator.set_file_valid)
        self.fileLineEdit.validator().is_valid.connect(self.set_file_valid)

        self.fieldsListWidget.currentTextChanged.connect(
            self.ok_validator.validate_field_widget_list
        )

        # Validate the default values set by the UI
        self.unitsLineEdit.validator().validate(self.unitsLineEdit.text(), 0)
        self.nameLineEdit.validator().validate(self.nameLineEdit.text(), 0)
        if not c_group:
            self.fileLineEdit.validator().validate(self.fileLineEdit.text(), 0)
        else:
            text = (
                SKIP_VALIDATION
                if c_group.has_pixel_shape() and not self.fileLineEdit.text()
                else self.fileLineEdit.text()
            )
            self.fileLineEdit.validator().validate(text, 0)
        self.addFieldPushButton.clicked.connect(self.add_field)
        self.removeFieldPushButton.clicked.connect(self.remove_field)

        # Connect the pixel mapping press signal the populate pixel mapping method
        if self.pixel_options:
            self.pixel_options.pixel_mapping_button_pressed.connect(
                self.populate_pixel_mapping_if_necessary
            )

        self.cylinderCountSpinBox.valueChanged.connect(
            self.populate_pixel_mapping_if_necessary
        )

        self.meshRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.CylinderRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.noShapeRadioButton.clicked.connect(self.set_pixel_related_changes)
        self.boxRadioButton.clicked.connect(self.set_pixel_related_changes)

        self.change_pixel_options_visibility()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ok_validator.validate_field_widget_list()

        self._set_html_docs_and_possible_fields(self._group_to_edit_backup.nx_class)

    def set_pixel_related_changes(self):
        """
        Manages the pixel-related changes that are induced by changing the shape type. This entails changing the
        visibility of the pixel options widget, clearing the previous pixel mapping table widget(if necessary),
        generating a new pixel mapping widget table (if necessary), and reassessing the validity of the pixel input.
        """
        self.change_pixel_options_visibility()

        if not self.noShapeRadioButton.isChecked():
            self.clear_previous_mapping_table()
            self.populate_pixel_mapping_if_necessary()

        self.update_pixel_input_validity()

    def clear_previous_mapping_table(self):
        """
        Wipes the previous table of pixel mapping table widgets. Required if the file has changed, or if the shape type has
        changed.
        """
        if self.pixel_options:
            self.pixel_options.reset_pixel_mapping_table()

    def _fill_existing_entries(self):
        """
        Fill in component details in the UI if editing a component
        """
        c_group = self._group_container.group
        if isinstance(c_group, Component):
            self.__fill_existing_shape_info()
        self.__fill_existing_fields()

    def __add_required_fields(self):
        c_group = self._group_container.group
        items_and_update_methods: List = []
        add_required_component_fields(c_group, items_and_update_methods)
        if items_and_update_methods:
            self.__populate_ui_fields(items_and_update_methods)
        self.ok_validator.validate_field_widget_list()

    def __fill_existing_fields(self):
        c_group = self._group_container.group
        items_and_update_methods = get_fields_and_update_functions_for_component(
            c_group
        )
        self.__populate_ui_fields(items_and_update_methods)

    def __populate_ui_fields(self, items_and_update_methods):
        for field, update_method in items_and_update_methods:
            if update_method is not None:
                new_ui_field = self.create_new_ui_field(field)
                update_method(field, new_ui_field)
                if not isinstance(field, Link):
                    try:
                        new_ui_field.units = field.attributes.get_attribute_value(
                            CommonAttrs.UNITS
                        )
                    except AttributeError:
                        new_ui_field.units = ""

    def __fill_existing_shape_info(self):
        if not isinstance(self._group_container.group, Component):
            return
        component_shape, _ = self._group_container.group.shape
        if not component_shape or isinstance(component_shape, NoShapeGeometry):
            self.noShapeRadioButton.setChecked(True)
            self.noShapeRadioButton.clicked.emit()
        else:
            if (
                isinstance(component_shape, OFFGeometryNexus)
                and component_shape.file_path
            ):
                self.cad_file_name = component_shape.file_path
                self.meshRadioButton.setChecked(True)
                self.meshRadioButton.clicked.emit()
                self.unitsLineEdit.setText(component_shape.units)
                if component_shape.file_path:
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
            elif isinstance(component_shape, BoxGeometry):
                self.boxRadioButton.clicked.emit()
                self.boxRadioButton.setChecked(True)
                self.boxLengthLineEdit.setValue(component_shape.size[0])
                self.boxWidthLineEdit.setValue(component_shape.size[1])
                self.boxHeightLineEdit.setValue(component_shape.size[2])
                self.unitsLineEdit.setText(component_shape.units)

    def create_new_ui_field(self, field):
        new_ui_field = self.add_field()
        if isinstance(field, Dataset):
            new_ui_field.name = field.name
        return new_ui_field

    def add_field(self) -> FieldWidget:
        item = QListWidgetItem()
        field = FieldWidget(
            self._group_container.group,
            self.possible_fields,
            self.fieldsListWidget,
        )
        item.setData(Qt.UserRole, field)
        field.something_clicked.connect(partial(self.select_field, item))
        self.nx_class_changed.connect(field.field_name_edit.update_possible_fields)
        item.setSizeHint(field.sizeHint())

        self.fieldsListWidget.addItem(item)
        self.fieldsListWidget.setItemWidget(item, field)
        if self.ok_validator:
            self.ok_validator.validate_field_widget_list()
        return field

    def select_field(self, widget):
        widget.setSelected(True)

    def remove_field(self):
        for item in self.fieldsListWidget.selectedItems():
            data = item.data(Qt.UserRole)
            if data.streams_widget:
                self._group_container.group.add_stream_module(
                    data.streams_widget._old_schema
                )
            self.fieldsListWidget.takeItem(self.fieldsListWidget.row(item))
        if self.ok_validator:
            self.ok_validator.validate_field_widget_list()

    def on_nx_class_changed(self):
        c_nx_class = self.componentTypeComboBox.currentText()
        self.placeholder_checkbox.setVisible(c_nx_class in NX_CLASSES_WITH_PLACEHOLDERS)
        if c_nx_class not in NX_CLASSES_WITH_PLACEHOLDERS:
            self.placeholder_checkbox.setChecked(False)
        if not c_nx_class or c_nx_class not in self.nx_component_classes:
            return
        self._set_html_docs_and_possible_fields(c_nx_class)

        self.possible_fields = self.nx_component_classes[c_nx_class]
        try:
            possible_field_names, _, _ = zip(*self.possible_fields)
            self.nx_class_changed.emit(possible_field_names)
        except ValueError:
            self.nx_class_changed.emit([])

    def _set_html_docs_and_possible_fields(self, c_nx_class):
        nx_class_docs_to_display = c_nx_class
        if c_nx_class in STREAM_MODULE_GROUPS or not c_nx_class:
            nx_class_docs_to_display = self._group_parent.nx_class
        if self._group_parent:
            possible_fields = self.nx_component_classes[self._group_parent.nx_class]
            possible_field_names, _, _ = zip(*possible_fields)
            possible_field_names = sorted(possible_field_names)
            self.suggest_group_name_from_parent_fields.emit(possible_field_names)
        else:
            self.suggest_group_name_from_parent_fields.emit([])
        class_html = path.join(
            self.local_url_root,
            f"{nx_class_docs_to_display}.html",
        )
        local_url_class = QUrl.fromLocalFile(class_html)
        self.webEngineView.setUrl(local_url_class)

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
        self.boxOptionsBox.setVisible(False)

    def show_box_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(False)
        self.cylinderOptionsBox.setVisible(False)
        self.boxOptionsBox.setVisible(True)

    def show_no_geometry_fields(self):
        self.shapeOptionsBox.setVisible(False)
        if self.nameLineEdit.text():
            self.ok_button.setEnabled(True)

    def show_mesh_fields(self):
        self.shapeOptionsBox.setVisible(True)
        self.geometryFileBox.setVisible(True)
        self.cylinderOptionsBox.setVisible(False)
        self.boxOptionsBox.setVisible(False)

    def _disable_fields_and_buttons(self, placeholder_state: bool):
        self.noShapeRadioButton.setEnabled(not placeholder_state)
        self.boxRadioButton.setEnabled(not placeholder_state)
        self.meshRadioButton.setEnabled(not placeholder_state)
        self.CylinderRadioButton.setEnabled(not placeholder_state)
        self.shapeOptionsBox.setEnabled(not placeholder_state)
        self.addFieldPushButton.setEnabled(not placeholder_state)
        self.removeFieldPushButton.setEnabled(not placeholder_state)

    def generate_geometry_model(
        self, component: Component, pixel_data: PixelData = None
    ):
        """
        Generates a geometry model depending on the type of geometry selected and the current values
        of the line edits that apply to the particular geometry type.
        :return: The generated model.
        """
        if self.CylinderRadioButton.isChecked():
            geometry = component.set_cylinder_shape(
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
            if not geometry:
                show_warning_dialog(
                    "3D vector is zero length in cylinder geometry.", ""
                )
        elif self.boxRadioButton.isChecked():
            component.set_box_shape(
                self.boxLengthLineEdit.value(),
                self.boxWidthLineEdit.value(),
                self.boxHeightLineEdit.value(),
                self.unitsLineEdit.text(),
                pixel_data=pixel_data,
            )
        elif self.meshRadioButton.isChecked() and self.cad_file_name:
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

    def get_pixel_visibility_condition(self) -> bool:
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
        _, index = self.component_model.current_nxs_obj
        self.model.signals.group_edited.emit(index, False)
        if self.pixel_options:
            pixel_data = self.pixel_options.generate_pixel_data()
        else:
            pixel_data = None

        component = self.finalise_group(pixel_data)
        if isinstance(component, Group):
            component.group_placeholder = self.placeholder_checkbox.isChecked()
        if isinstance(component, Component):
            self.signals.component_added.emit(component)
        if not self.initial_edit:
            self.signals.transformation_changed.emit()
        self.model.signals.group_edited.emit(index, True)
        self.hide()

    def keyPressEvent(self, arg__1: QKeyEvent) -> None:
        if arg__1.key() == Qt.Key_Escape:
            self._cancel_edit_group()
        else:
            super().keyPressEvent(arg__1)

    def finalise_group(
        self,
        pixel_data: PixelData,
    ):
        """
        Edits an existing component.
        :param pixel_data: The component PixelData. Can be None.
        :return: The geometry object.
        """
        c_group = self._group_container.group
        old_group_name = c_group.absolute_path
        self.nameLineEdit.set_new_group_name()
        group_children = []
        for child in c_group.children:
            if isinstance(child, Group):
                group_children.append(child)
        c_group.children = []
        for child in group_children:
            c_group[child.name] = child
        add_fields_to_component(c_group, self.fieldsListWidget, self.component_model)
        if isinstance(c_group, Component):
            # remove the previous object from the qt3d view
            self._scene_widget.delete_component(old_group_name)
            self.component_model.model.append_component(c_group)
            self.generate_geometry_model(c_group, pixel_data)
            self.write_pixel_data_to_component(c_group, pixel_data)

        return c_group

    def write_pixel_data_to_component(
        self, component: Component, pixel_data: PixelData
    ):
        """
        Writes the detector number/pixel grid data to a component.
        :param component: The component to modify.
        :param nx_class: The NXclass of the component.
        :param pixel_data: The pixel data.
        """
        component.clear_pixel_data()

        if pixel_data is None or component.nx_class not in PIXEL_COMPONENT_TYPES:
            return

        if isinstance(pixel_data, PixelMapping):
            component.record_pixel_mapping(pixel_data)
        if isinstance(pixel_data, PixelGrid) and self.get_pixel_visibility_condition():
            component.record_pixel_grid(pixel_data, self.unitsLineEdit.text())

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
        has been selected. The RuntimeError occurs when editing a component and switching from a Pixel Grid/No Shape
        to a PixelMapping. It says that the Pixel Options widget and Mesh/Cylinder buttons have been deleted even though
        they ought to be "brand new" when the Edit Component Window opens. A try-except block appears to be the only way
        to handle it for now.
        """
        try:
            if not self.pixelOptionsWidget.isVisible():
                return

            if self.meshRadioButton.isChecked():
                self.create_pixel_mapping_list_for_mesh()

            if self.CylinderRadioButton.isChecked() and self.pixel_options:
                self.pixel_options.populate_pixel_mapping_list_with_cylinder_number(
                    self.cylinderCountSpinBox.value()
                )
        except RuntimeError:
            pass

    def create_pixel_mapping_list_for_mesh(self):
        """
        Instructs the PixelOptions to create a list of Pixel Mapping widgets using a mesh file if the user has given a
        valid file and has not selected the same file twice in a row.
        """
        if (
            self.cad_file_name is not None
            and self.valid_file_given
            and (
                self.pixel_options.get_current_mapping_filename() != self.cad_file_name
            )
        ):
            self.pixel_options.populate_pixel_mapping_list_with_mesh(self.cad_file_name)

    def update_pixel_input_validity(self):
        """
        Instruct the PixelOptions widget to carry out another check for input validity.
        """
        if self.pixel_options:
            self.pixel_options.update_pixel_input_validity()

    def set_shape_button_visibility(self):
        nx_class = self.componentTypeComboBox.currentText()
        self.shapeTypeBox.setVisible(nx_class in COMPONENT_TYPES)
        if nx_class not in COMPONENT_TYPES:
            return
        is_not_special_case = nx_class not in SPECIAL_SHAPE_CASES.keys()
        self.noShapeRadioButton.setVisible(True)
        self.boxRadioButton.setVisible(is_not_special_case)
        self.meshRadioButton.setVisible(is_not_special_case)
        self.CylinderRadioButton.setVisible(is_not_special_case)


def get_fields_and_update_functions_for_component(component: Group):
    return get_fields_with_update_functions(component)


def add_fields_to_component(
    component: Group, fields_widget: QListWidget, component_model: NexusTreeModel = None
):
    """
    Adds fields from a list widget to a component.
    :param component: Component to add the field to.
    :param fields_widget: The field list widget to extract field information such the name and value of each field.
    """
    for i in range(fields_widget.count()):
        widget = fields_widget.itemWidget(fields_widget.item(i))
        try:
            if not isinstance(widget.value, (Link, Dataset, FileWriter)):
                stream_module = deepcopy(widget.value)
                stream_module.parent_node = component
                component.children.append(stream_module)
            else:
                component[widget.name] = widget.value
        except ValueError as error:
            show_warning_dialog(
                f"Warning: field {widget.name} not added",
                title="Field invalid",
                additional_info=str(error),
                parent=fields_widget.parent().parent(),
            )
    if component_model and component_model.current_nxs_obj[1]:
        row = component_model.rowCount(component_model.current_nxs_obj[1])
        component_model.createIndex(row, 0, component_model.current_nxs_obj[1])
