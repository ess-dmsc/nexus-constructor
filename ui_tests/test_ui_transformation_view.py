from typing import Any

import numpy as np
import pytest
from PySide6.QtGui import QVector3D
from pytestqt.qtbot import QtBot  # noqa: F401

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.field_attrs import _get_human_readable_type
from nexus_constructor.model.component import Component
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import Dataset, F142Stream, Link
from nexus_constructor.transformation_view import EditRotation, EditTranslation
from nexus_constructor.validators import FieldType
from nexus_constructor.ui_utils import qvector3d_to_numpy_array


@pytest.fixture
def component():
    return Component("Component", [])


def create_corresponding_value_dataset(value: Any):
    name = ""
    type = _get_human_readable_type(value)

    if np.isscalar(value):
        value = str(value)

    return Dataset(
        parent_node=None,
        name=name,
        type=type,
        values=value,
    )


def test_UI_GIVEN_scalar_vector_WHEN_creating_translation_view_THEN_ui_is_filled_correctly(
    qtbot, model, component
):
    x = 0
    y = 0
    z = 0
    value = 0.0
    transform = component.add_translation(QVector3D(x, y, z), name="transform")
    transform.values = create_corresponding_value_dataset(value)

    view = EditTranslation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.magnitude_widget.value_line_edit.text() == str(
        value
    )
    assert (
        view.transformation_frame.magnitude_widget.field_type
        == FieldType.scalar_dataset
    )


def test_UI_GIVEN_scalar_angle_WHEN_creating_rotation_view_THEN_ui_is_filled_correctly(
    qtbot, model, component
):
    x = 0
    y = 0
    z = 0
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))
    transform.values = create_corresponding_value_dataset(angle)

    view = EditRotation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.magnitude_widget.value_line_edit.text() == str(
        angle
    )
    assert (
        view.transformation_frame.magnitude_widget.field_type
        == FieldType.scalar_dataset
    )


def test_UI_GIVEN_a_translation_with_zero_offset_WHEN_setting_the_offset_to_nonzero_THEN_ui_is_filled_correctly(
    qtbot, component, model
):
    transform = component.add_translation(QVector3D(0, 0, 1), name="test")
    transform.values = create_corresponding_value_dataset(123)
    view = EditTranslation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    view.transformation_frame.offset_spinboxes[0].setValue(9)
    view.save_offset()
    assert all(transform.attributes.get_attribute_value(CommonAttrs.OFFSET) == qvector3d_to_numpy_array(QVector3D(9, 0, 0)))
    assert view.transformation_frame.offset_spinboxes[0].value() == 9


def test_UI_GIVEN_a_translation_with_nonzero_offset_WHEN_setting_the_offset_to_zero_THEN_ui_is_filled_correctly(
    qtbot, component, model
):
    transform = component.add_translation(QVector3D(0, 0, 1), name="test")
    transform.values = create_corresponding_value_dataset(123)
    view = EditTranslation(parent=None, transformation=transform, model=model)
    view.transformation_frame.offset_spinboxes[0].setValue(10)
    qtbot.addWidget(view)
    view.save_offset()

    view.transformation_frame.offset_spinboxes[0].setValue(0)
    view.save_offset()

    assert view.transformation_frame.offset_spinboxes[0].value() == 0


def test_UI_GIVEN_array_dataset_as_magnitude_WHEN_creating_translation_THEN_ui_is_filled_correctly(
    qtbot, component, model
):
    array = np.array([1, 2, 3, 4])

    x = 0
    y = 0
    z = 0
    transform = component.add_translation(QVector3D(x, y, z), name="test")
    transform.values = create_corresponding_value_dataset(array)

    view = EditTranslation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert np.allclose(
        view.transformation_frame.magnitude_widget.table_view.model.array, array
    )
    assert (
        view.transformation_frame.magnitude_widget.field_type == FieldType.array_dataset
    )


def test_UI_GIVEN_stream_group_as_angle_WHEN_creating_rotation_THEN_ui_is_filled_correctly(
    qtbot,
):
    component = Component(
        name="test",
    )

    x = 0
    y = 0
    z = 0

    transform = component.add_rotation(QVector3D(x, y, z), 0, name="test")

    topic = "test_topic"
    source = "source1"
    type = "double"
    stream = F142Stream(parent_node=transform, topic=topic, source=source, type=type)

    transform.values = stream

    view = EditRotation(parent=None, transformation=transform, model=None)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert (
        view.transformation_frame.magnitude_widget.field_type == FieldType.kafka_stream
    )
    assert view.transformation_frame.magnitude_widget.value.topic == topic
    assert view.transformation_frame.magnitude_widget.value.type == type
    assert view.transformation_frame.magnitude_widget.value.writer_module == "f142"
    assert view.transformation_frame.magnitude_widget.value.source == source


def test_UI_GIVEN_link_as_rotation_magnitude_WHEN_creating_rotation_view_THEN_ui_is_filled_correctly(
    qtbot,
):
    model = Model()
    component = Component(name="test")

    x = 0
    y = 0
    z = 0
    path = "/entry"

    transform = component.add_rotation(QVector3D(x, y, z), 0, name="test")
    transform.values = Link(parent_node=None, name="test", source=path)

    view = EditRotation(transformation=transform, model=model, parent=None)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.magnitude_widget.field_type == FieldType.link
    assert view.transformation_frame.magnitude_widget.value.source == path


def test_UI_GIVEN_vector_updated_WHEN_saving_view_changes_THEN_model_is_updated(
    qtbot, component, model
):
    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))
    transform.values = create_corresponding_value_dataset(angle)
    view = EditRotation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    new_x = 4
    new_y = 5
    new_z = 6

    view.transformation_frame.x_spinbox.setValue(new_x)
    view.transformation_frame.y_spinbox.setValue(new_y)
    view.transformation_frame.z_spinbox.setValue(new_z)

    view.save_all_changes()

    assert transform.vector == QVector3D(new_x, new_y, new_z)


def test_UI_GIVEN_view_gains_focus_WHEN_transformation_view_exists_THEN_spinboxes_are_enabled(
    qtbot, component, model
):
    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))
    transform.values = create_corresponding_value_dataset(angle)
    view = EditRotation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    view.enable()

    assert view.transformation_frame.x_spinbox.isEnabled()
    assert view.transformation_frame.y_spinbox.isEnabled()
    assert view.transformation_frame.z_spinbox.isEnabled()
    assert view.transformation_frame.name_line_edit.isEnabled()


def test_UI_GIVEN_view_loses_focus_WHEN_transformation_view_exists_THEN_spinboxes_are_disabled(
    qtbot, component, model
):
    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))
    transform.values = create_corresponding_value_dataset(angle)
    view = EditRotation(parent=None, transformation=transform, model=model)
    qtbot.addWidget(view)

    view.disable()

    assert not view.transformation_frame.x_spinbox.isEnabled()
    assert not view.transformation_frame.y_spinbox.isEnabled()
    assert not view.transformation_frame.z_spinbox.isEnabled()
    assert not view.transformation_frame.name_line_edit.isEnabled()
