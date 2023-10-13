from typing import TYPE_CHECKING

from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QFrame, QGroupBox, QWidget

from nexus_constructor.common_attrs import CommonAttrs, TransformationType
from nexus_constructor.component_tree_model import LinkTransformation
from nexus_constructor.field_utils import find_field_type
from nexus_constructor.model.component import Component
from nexus_constructor.model.model import Model
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.unit_utils import METRES, RADIANS
from ui.link import Ui_Link
from ui.transformation import UiTransformation

if TYPE_CHECKING:
    from nexus_constructor.model.value_type import ValueType  # noqa: F401


class EditTransformation(QGroupBox):
    transformation_parent = None

    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent)
        self.model = model
        self.transformation_frame = UiTransformation(self)
        self.transformation = transformation
        self.transformation_parent = transformation.parent_component
        current_vector = self.transformation.vector
        self._fill_in_existing_fields(current_vector)
        self._fill_in_existing_fields(self.transformation.offset_vector)
        self.transformation_frame.depends_on_text_box.setEnabled(False)
        self.disable()
        self._init_connections()

    def _init_connections(self):
        self.transformation_frame.name_line_edit.textChanged.connect(
            self.save_transformation_name
        )

        for box in self.transformation_frame.spinboxes:
            box.textChanged.connect(self.save_transformation_vector)

        for box in self.transformation_frame.offset_spinboxes:
            box.textChanged.connect(self.save_offset)

        self.transformation_frame.magnitude_widget.value_line_edit.textChanged.connect(
            self.save_magnitude
        )
        self.transformation_frame.magnitude_widget.units_line_edit.textChanged.connect(
            self.save_magnitude
        )
        if self.model:
            self.model.signals.transformation_changed.connect(self.update_depends_on_ui)

    def _fill_in_existing_fields(self, current_vector):
        self.transformation_frame.name_line_edit.setText(self.transformation.name)
        self.transformation_frame.x_spinbox.setValue(current_vector.x())
        self.transformation_frame.y_spinbox.setValue(current_vector.y())
        self.transformation_frame.z_spinbox.setValue(current_vector.z())
        update_function = find_field_type(self.transformation.values)
        if update_function is not None:
            update_function(
                self.transformation.values, self.transformation_frame.magnitude_widget
            )
        self.transformation_frame.magnitude_widget.units = self.transformation.units
        offset = self.transformation.attributes.get_attribute_value(CommonAttrs.OFFSET)
        if offset is not None:
            self.transformation_frame.x_spinbox_offset.setValue(offset[0])
            self.transformation_frame.y_spinbox_offset.setValue(offset[1])
            self.transformation_frame.z_spinbox_offset.setValue(offset[2])
        self.update_depends_on_ui()

    def disable(self):
        for ui_element in self.transformation_frame.spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(False)

    def enable(self):
        # Don't enable the 3D value spinbox if the magnitude is scalar
        if self.transformation_frame.magnitude_widget.field_type_is_scalar():
            spinboxes = self.transformation_frame.spinboxes
        else:
            spinboxes = self.transformation_frame.spinboxes

        for ui_element in spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(True)

    def update_depends_on_ui(self):
        if self.transformation.depends_on:
            self.transformation_frame.depends_on_text_box.setText(
                self.transformation.depends_on.absolute_path
            )
        else:
            self.transformation_frame.depends_on_text_box.setText(".")

    def save_magnitude(self):
        self.transformation.values = self.transformation_frame.magnitude_widget.value
        self.transformation.units = self.transformation_frame.magnitude_widget.units
        self.model.signals.transformation_changed.emit()

    def save_transformation_vector(self):
        self.transformation.vector = QVector3D(
            *[spinbox.value() for spinbox in self.transformation_frame.spinboxes]
        )
        self.model.signals.transformation_changed.emit()

    def save_transformation_name(self):
        if self.transformation_frame.name_line_edit.text() != self.transformation.name:
            self.transformation.name = self.transformation_frame.name_line_edit.text()
            self.model.signals.transformation_changed.emit()

    def save_offset(self):
        self.transformation.offset_vector = QVector3D(
            *[spinbox.value() for spinbox in self.transformation_frame.offset_spinboxes]
        )
        self.model.signals.transformation_changed.emit()

    def save_all_changes(self):
        self.save_transformation_name()
        self.save_transformation_vector()
        self.save_offset()
        self.save_magnitude()


class EditTranslation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent, transformation, model)
        self.transformation_frame.magnitude_widget.unit_validator.expected_dimensionality = (
            METRES
        )
        transformation_text(self, TransformationType.TRANSLATION)


class EditRotation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent, transformation, model)
        self.transformation_frame.magnitude_widget.unit_validator.expected_dimensionality = (
            RADIANS
        )
        transformation_text(self, TransformationType.ROTATION)


def transformation_text(self, transformation_type):
    self.transformation_frame.vector_label.setText("Vector")
    self.transformation_frame.value_label.setText("Magnitude")
    self.transformation_frame.offset_label.setText("Offset")
    self.setTitle(transformation_type)


def links_back_to_component(reference: Component, comparison: Component):
    if reference == comparison:
        return True
    if not comparison.transforms.has_link:
        return False
    if comparison.transforms.link.linked_component is None:
        return False
    return links_back_to_component(
        reference, comparison.transforms.link.linked_component
    )


class EditTransformationLink(QFrame):
    def __init__(self, parent: QWidget, link: LinkTransformation, model: Model):
        super().__init__(parent)
        self.link = link
        self.signals = model.signals
        self.model = model
        self.link_frame = Ui_Link()
        self.link_frame.setupUi(self)
        self.populate_combo_box()
        self.link_frame.go_to_link.clicked.connect(self.go_to_component)

    def populate_combo_box(self):
        self.link_frame.transformations_combo_box.blockSignals(True)

        self.link_frame.transformations_combo_box.clear()
        self.link_frame.transformations_combo_box.addItem("(None)", userData=None)
        self.link_frame.transformations_combo_box.setCurrentIndex(0)
        components = self.model.get_components()
        for current_component in components:
            transformations = current_component.transforms
            self.link_frame.transformations_combo_box.addItem(
                current_component.name, userData=current_component
            )
            last_index = self.link_frame.transformations_combo_box.count() - 1
            if links_back_to_component(
                self.link.parent.parent_component, current_component
            ):
                self.link_frame.transformations_combo_box.model().item(
                    last_index
                ).setEnabled(False)
            if len(transformations) == 0:
                self.link_frame.transformations_combo_box.model().item(
                    last_index
                ).setEnabled(False)
            if (
                self.link.linked_component is not None
                and self.link.linked_component == current_component
            ):
                new_index = self.link_frame.transformations_combo_box.count() - 1
                self.link_frame.transformations_combo_box.setCurrentIndex(new_index)
                self.link_frame.setLinkEvent(new_index)
        self.link_frame.transformations_combo_box.currentIndexChanged.connect(
            self.set_new_index
        )
        self.link_frame.transformations_combo_box.blockSignals(False)

    def set_new_index(self, new_index):
        if new_index == -1:
            return
        self.link.linked_component = (
            self.link_frame.transformations_combo_box.currentData()
        )

    def enable(self):
        self.populate_combo_box()

    def save_all_changes(self):
        self.signals.transformation_changed.emit()

    def go_to_component(self):
        tree_view = self.parent().parent().parent()
        tree_view.setCurrentIndex(
            tree_view.model().index_from_component(self.link.linked_component)
        )
