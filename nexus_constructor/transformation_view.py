from typing import TYPE_CHECKING

from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QFrame, QGroupBox, QWidget

from nexus_constructor.common_attrs import TransformationType
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
    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent)
        self.model = model
        self.transformation_frame = UiTransformation(self)
        self.transformation = transformation
        current_vector = self.transformation.vector
        self._fill_in_existing_fields(current_vector)
        self.transformation_frame.magnitude_widget.enable_3d_value_spinbox.connect(
            self._change_3d_value_spinbox_visibility
        )
        self.disable()
        self._init_connections()

    def _init_connections(self):
        self.transformation_frame.name_line_edit.textChanged.connect(
            self.save_transformation_name
        )

        for box in self.transformation_frame.spinboxes[:-1]:
            box.textChanged.connect(self.save_transformation_vector)

        self.transformation_frame.magnitude_widget.value_line_edit.textChanged.connect(
            self.save_magnitude
        )
        self.transformation_frame.magnitude_widget.units_line_edit.textChanged.connect(
            self.save_magnitude
        )

    def _change_3d_value_spinbox_visibility(self, show: bool):
        self.transformation_frame.value_spinbox.setEnabled(show)

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
        self.transformation_frame.value_spinbox.setValue(self.transformation.ui_value)

    def disable(self):
        for ui_element in self.transformation_frame.spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(False)

    def enable(self):
        # Don't enable the 3D value spinbox if the magnitude is scalar
        if self.transformation_frame.magnitude_widget.field_type_is_scalar():
            spinboxes = self.transformation_frame.spinboxes[:-1]
        else:
            spinboxes = self.transformation_frame.spinboxes

        for ui_element in spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(True)

    def save_magnitude(self):

        self.check_field_type()

        self.transformation.ui_value = self.transformation_frame.value_spinbox.value()
        self.transformation.values = self.transformation_frame.magnitude_widget.value
        self.transformation.units = self.transformation_frame.magnitude_widget.units
        self.model.signals.transformation_changed.emit()

    def check_field_type(self):
        if self.transformation_frame.magnitude_widget.field_type_is_scalar():
            try:
                value_3d_view: "ValueType" = (
                    self.transformation_frame.magnitude_widget.value.values
                )
                self.transformation_frame.value_spinbox.setValue(float(value_3d_view))
            except ValueError:
                pass

    def save_transformation_vector(self):
        self.transformation.vector = QVector3D(
            *[spinbox.value() for spinbox in self.transformation_frame.spinboxes[:-1]]
        )
        self.model.signals.transformation_changed.emit()

    def save_transformation_name(self):
        if self.transformation_frame.name_line_edit.text() != self.transformation.name:
            self.transformation.name = self.transformation_frame.name_line_edit.text()
            self.model.signals.transformation_changed.emit()

    def save_all_changes(self):
        self.save_transformation_name()
        self.save_transformation_vector()
        self.save_magnitude()


class EditTranslation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent, transformation, model)
        self.transformation_frame.magnitude_widget.unit_validator.expected_dimensionality = (
            METRES
        )
        self.transformation_frame.vector_label.setText("Direction")
        self.transformation_frame.value_label.setText("Distance (m)")
        self.setTitle(TransformationType.TRANSLATION)


class EditRotation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation, model: Model):
        super().__init__(parent, transformation, model)
        self.transformation_frame.magnitude_widget.unit_validator.expected_dimensionality = (
            RADIANS
        )
        self.transformation_frame.vector_label.setText("Rotation Axis")
        self.transformation_frame.value_label.setText("Angle (°)")
        self.setTitle(TransformationType.ROTATION)


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
        self.instrument = model.entry.instrument
        self.link_frame = Ui_Link()
        self.link_frame.setupUi(self)
        self.populate_combo_box()

    def populate_combo_box(self):
        self.link_frame.transformations_combo_box.blockSignals(True)

        self.link_frame.transformations_combo_box.clear()
        self.link_frame.transformations_combo_box.addItem("(None)", userData=None)
        self.link_frame.transformations_combo_box.setCurrentIndex(0)
        components = self.instrument.component_list
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
                self.link_frame.transformations_combo_box.setCurrentIndex(
                    self.link_frame.transformations_combo_box.count() - 1
                )
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
