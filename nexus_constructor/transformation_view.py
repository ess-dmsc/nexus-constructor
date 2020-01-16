from nexus_constructor.transformation_types import TransformationType
from ui.transformation import Ui_Transformation
from ui.link import Ui_Link
from PySide2.QtWidgets import QGroupBox, QFrame, QWidget
from PySide2.QtGui import QVector3D
from nexus_constructor.transformations import Transformation
from nexus_constructor.instrument import Instrument
from nexus_constructor.component_tree_model import LinkTransformation
from nexus_constructor.component.component import Component


class EditTransformation(QGroupBox):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent)
        self.instrument = instrument
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self)
        self.transformation = transformation
        current_vector = self.transformation.vector
        self.transformation_frame.x_spinbox.setRange(-10000000, 10000000)
        self.transformation_frame.y_spinbox.setRange(-10000000, 10000000)
        self.transformation_frame.z_spinbox.setRange(-10000000, 10000000)
        self.transformation_frame.value_spinbox.setRange(-10000000, 10000000)
        self.transformation_frame.x_spinbox.setValue(current_vector.x())
        self.transformation_frame.y_spinbox.setValue(current_vector.y())
        self.transformation_frame.z_spinbox.setValue(current_vector.z())
        self.transformation_frame.name_line_edit.setText(self.transformation.name)
        self.transformation_frame.value_spinbox.setValue(self.transformation.value)
        self.disable()

    def disable(self):
        self.transformation_frame.x_spinbox.setEnabled(False)
        self.transformation_frame.y_spinbox.setEnabled(False)
        self.transformation_frame.z_spinbox.setEnabled(False)
        self.transformation_frame.value_spinbox.setEnabled(False)
        self.transformation_frame.name_line_edit.setEnabled(False)

    def enable(self):
        self.transformation_frame.x_spinbox.setEnabled(True)
        self.transformation_frame.y_spinbox.setEnabled(True)
        self.transformation_frame.z_spinbox.setEnabled(True)
        self.transformation_frame.value_spinbox.setEnabled(True)
        self.transformation_frame.name_line_edit.setEnabled(True)

    def saveChanges(self):
        self.transformation.name = self.transformation_frame.name_line_edit.text()
        self.transformation.vector = QVector3D(
            self.transformation_frame.x_spinbox.value(),
            self.transformation_frame.y_spinbox.value(),
            self.transformation_frame.z_spinbox.value(),
        )
        self.transformation.value = self.transformation_frame.value_spinbox.value()
        self.instrument.nexus.transformation_changed.emit()


class EditTranslation(EditTransformation):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent, transformation, instrument)
        self.transformation_frame.valueLabel.setText("Distance (m)")
        self.setTitle(TransformationType.TRANSLATION.value)


class EditRotation(EditTransformation):
    def __init__(
        self, parent: QWidget, transformation: Transformation, instrument: Instrument
    ):
        super().__init__(parent, transformation, instrument)
        self.transformation_frame.valueLabel.setText("Angle (°)")
        self.setTitle("Rotation")


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
        self.link_frame.TransformationsComboBox.blockSignals(True)

        self.link_frame.TransformationsComboBox.clear()
        self.link_frame.TransformationsComboBox.addItem("(None)", userData=None)
        self.link_frame.TransformationsComboBox.setCurrentIndex(0)
        components = self.instrument.get_component_list()
        for current_component in components:
            transformations = current_component.transforms
            self.link_frame.TransformationsComboBox.addItem(
                current_component.name, userData=current_component
            )
            last_index = self.link_frame.TransformationsComboBox.count() - 1
            if links_back_to_component(
                self.link.parent.parent_component, current_component
            ):
                self.link_frame.TransformationsComboBox.model().item(
                    last_index
                ).setEnabled(False)
            if len(transformations) == 0:
                self.link_frame.TransformationsComboBox.model().item(
                    last_index
                ).setEnabled(False)
            if (
                self.link.linked_component is not None
                and self.link.linked_component == current_component
            ):
                self.link_frame.TransformationsComboBox.setCurrentIndex(
                    self.link_frame.TransformationsComboBox.count() - 1
                )
        self.link_frame.TransformationsComboBox.currentIndexChanged.connect(
            self.set_new_index
        )
        self.link_frame.TransformationsComboBox.blockSignals(False)

    def set_new_index(self, new_index):
        if new_index == -1:
            return
        self.link.linked_component = (
            self.link_frame.TransformationsComboBox.currentData()
        )

    def enable(self):
        self.populate_combo_box()

    def saveChanges(self):
        self.instrument.nexus.transformation_changed.emit()
