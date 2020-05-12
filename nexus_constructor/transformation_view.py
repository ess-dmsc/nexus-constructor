from nexus_constructor.field_utils import find_field_type
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Instrument
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.unit_utils import METRES, RADIANS
from ui.transformation import Ui_Transformation
from ui.link import Ui_Link
from PySide2.QtWidgets import QGroupBox, QFrame, QWidget, QLabel
from PySide2.QtGui import QVector3D
from nexus_constructor.transformations import Transformation, NXLogTransformation
from nexus_constructor.component_tree_model import LinkTransformation


class EditTransformation(QGroupBox):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent)
        self.instrument = instrument
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self, instrument)
        self.transformation = transformation
        current_vector = self.transformation.vector
        self._fill_in_existing_fields(current_vector)
        self.disable()

    def _fill_in_existing_fields(self, current_vector):
        self.transformation_frame.name_line_edit.setText(self.transformation.name)
        self.transformation_frame.x_spinbox.setValue(current_vector.x())
        self.transformation_frame.y_spinbox.setValue(current_vector.y())
        self.transformation_frame.z_spinbox.setValue(current_vector.z())
        update_function = find_field_type(self.transformation.dataset)
        if update_function is not None:
            update_function(
                self.transformation.dataset, self.transformation_frame.magnitude_widget
            )
        if isinstance(self.transformation, NXLogTransformation):
            self.transformation_frame.main_layout.addWidget(
                QLabel(
                    "Transformation is an NXlog - currently these are not editable. "
                )
            )
            self.transformation_frame.magnitude_widget.setVisible(False)
        self.transformation_frame.magnitude_widget.units = self.transformation.units
        self.transformation_frame.value_spinbox.setValue(self.transformation.ui_value)

    def disable(self):
        for ui_element in self.transformation_frame.spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(False)

    def enable(self):
        for ui_element in self.transformation_frame.spinboxes + [
            self.transformation_frame.name_line_edit,
            self.transformation_frame.magnitude_widget,
        ]:
            ui_element.setEnabled(True)

    def saveChanges(self):
        self.transformation.ui_value = self.transformation_frame.value_spinbox.value()
        self.transformation.dataset = self.transformation_frame.magnitude_widget.value
        if self.transformation_frame.name_line_edit.text() != self.transformation.name:
            self.transformation.name = self.transformation_frame.name_line_edit.text()
        self.transformation.vector = QVector3D(
            *[spinbox.value() for spinbox in self.transformation_frame.spinboxes[:-1]]
        )
        self.transformation.units = self.transformation_frame.magnitude_widget.units
        self.instrument.nexus.transformation_changed.emit()


class EditTranslation(EditTransformation):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent, transformation, instrument)
        self.transformation_frame.magnitude_widget.unit_validator.expected_dimensionality = (
            METRES
        )
        self.transformation_frame.vector_label.setText("Direction")
        self.transformation_frame.value_label.setText("Distance (m)")
        self.setTitle(TransformationType.TRANSLATION)


class EditRotation(EditTransformation):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent, transformation, instrument)
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
    def __init__(
        self, parent: QWidget, link: LinkTransformation, instrument: Instrument
    ):
        super().__init__(parent)
        self.link = link
        self.instrument = instrument
        self.link_frame = Ui_Link()
        self.link_frame.setupUi(self)
        self.populate_combo_box()

    def populate_combo_box(self):
        self.link_frame.transformations_combo_box.blockSignals(True)

        self.link_frame.transformations_combo_box.clear()
        self.link_frame.transformations_combo_box.addItem("(None)", userData=None)
        self.link_frame.transformations_combo_box.setCurrentIndex(0)
        components = self.instrument.get_component_list()
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

    def saveChanges(self):
        self.instrument.nexus.transformation_changed.emit()
