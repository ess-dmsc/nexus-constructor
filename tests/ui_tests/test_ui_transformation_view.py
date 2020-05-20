import h5py
from PySide2.QtGui import QVector3D
from mock import Mock

from nexus_constructor.model.entry import Instrument
from nexus_constructor.transformation_view import EditRotation, EditTranslation
from nexus_constructor.validators import FieldType
import numpy as np
from pytestqt.qtbot import QtBot  # noqa: F401
import pytest

pytest.skip("Disabled whilst working on model change", allow_module_level=True)


def test_UI_GIVEN_scalar_vector_WHEN_creating_translation_view_THEN_ui_is_filled_correctly(
    qtbot, nexus_wrapper
):

    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 0
    z = 0
    transform = component.add_translation(QVector3D(x, y, z), name="test")

    view = EditTranslation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.value_spinbox.value() == 1
    assert view.transformation_frame.magnitude_widget.value[()] == 1
    assert (
        view.transformation_frame.magnitude_widget.field_type
        == FieldType.scalar_dataset
    )


def test_UI_GIVEN_scalar_angle_WHEN_creating_rotation_view_THEN_ui_is_filled_correctly(
    qtbot, nexus_wrapper
):

    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.value_spinbox.value() == angle
    assert view.transformation_frame.magnitude_widget.value[()] == angle
    assert (
        view.transformation_frame.magnitude_widget.field_type
        == FieldType.scalar_dataset
    )


def test_UI_GIVEN_array_dataset_as_magnitude_WHEN_creating_translation_THEN_ui_is_filled_correctly(
    qtbot, file, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    array = np.array([1, 2, 3, 4])

    x = 1
    y = 0
    z = 0
    transform = component.add_translation(QVector3D(x, y, z), name="test")

    transform.dataset = file.create_dataset("test", data=array)

    view = EditTranslation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert np.allclose(view.transformation.dataset[...], array)
    assert (
        view.transformation_frame.magnitude_widget.field_type == FieldType.array_dataset
    )


def test_UI_GIVEN_stream_group_as_angle_WHEN_creating_rotation_THEN_ui_is_filled_correctly(
    qtbot, file, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 0
    y = 0
    z = 0

    transform = component.add_rotation(QVector3D(x, y, z), 0, name="test")

    stream_group = file.create_group("stream_group")
    stream_group.attrs["NX_class"] = "NCstream"
    topic = "test_topic"
    writer_module = "ev42"
    source = "source1"
    stream_group.create_dataset("topic", dtype=h5py.special_dtype(vlen=str), data=topic)
    stream_group.create_dataset("writer_module", data=writer_module)
    stream_group.create_dataset("source", data=source)

    transform.dataset = stream_group

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.value_spinbox.value() == 0.0
    assert (
        view.transformation_frame.magnitude_widget.field_type == FieldType.kafka_stream
    )
    assert view.transformation_frame.magnitude_widget.value["topic"][()] == topic
    assert (
        view.transformation_frame.magnitude_widget.value["writer_module"][()]
        == writer_module
    )
    assert view.transformation_frame.magnitude_widget.value["source"][()] == source


def test_UI_GIVEN_link_as_rotation_magnitude_WHEN_creating_rotation_view_THEN_ui_is_filled_correctly(
    qtbot, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 0
    y = 0
    z = 0
    path = "/entry"

    transform = component.add_rotation(QVector3D(x, y, z), 0, name="test")
    link = nexus_wrapper.instrument["asdfgh"] = h5py.SoftLink(path)

    transform.dataset = link

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.value_spinbox.value() == 0.0
    assert view.transformation_frame.magnitude_widget.field_type == FieldType.link
    assert view.transformation_frame.magnitude_widget.value.path == path


def test_UI_GIVEN_vector_updated_WHEN_saving_view_changes_THEN_model_is_updated(
    qtbot, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    new_x = 4
    new_y = 5
    new_z = 6

    view.transformation_frame.x_spinbox.setValue(new_x)
    view.transformation_frame.y_spinbox.setValue(new_y)
    view.transformation_frame.z_spinbox.setValue(new_z)

    view.saveChanges()

    assert transform.vector == QVector3D(new_x, new_y, new_z)


def test_UI_GIVEN_view_gains_focus_WHEN_transformation_view_exists_THEN_spinboxes_are_enabled(
    qtbot, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    view.enable()

    assert view.transformation_frame.x_spinbox.isEnabled()
    assert view.transformation_frame.y_spinbox.isEnabled()
    assert view.transformation_frame.z_spinbox.isEnabled()
    assert view.transformation_frame.name_line_edit.isEnabled()


def test_UI_GIVEN_view_loses_focus_WHEN_transformation_view_exists_THEN_spinboxes_are_disabled(
    qtbot, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    view.disable()

    assert not view.transformation_frame.x_spinbox.isEnabled()
    assert not view.transformation_frame.y_spinbox.isEnabled()
    assert not view.transformation_frame.z_spinbox.isEnabled()
    assert not view.transformation_frame.name_line_edit.isEnabled()


def test_UI_GIVEN_new_values_are_provided_WHEN_save_changes_is_called_THEN_transformation_changed_signal_is_called_to_update_3d_view(
    qtbot, nexus_wrapper
):
    instrument = Instrument(nexus_wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 1
    y = 2
    z = 3
    angle = 90

    transform = component.add_rotation(angle=angle, axis=QVector3D(x, y, z))

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    instrument.nexus.transformation_changed = Mock()
    qtbot.addWidget(view)

    new_x = 4

    view.transformation_frame.x_spinbox.setValue(new_x)
    view.saveChanges()
    instrument.nexus.transformation_changed.emit.assert_called_once()
    assert transform.vector == QVector3D(new_x, y, z)
