import h5py
from PySide2.QtGui import QVector3D
from nexus_constructor.instrument import Instrument
from nexus_constructor.nexus.nexus_wrapper import NexusWrapper
from nexus_constructor.transformation_view import EditRotation, EditTranslation
from nexus_constructor.validators import FieldType
import numpy as np
from pytestqt.qtbot import QtBot  # noqa: F401
from tests.helpers import file  # noqa: F401


def test_UI_GIVEN_scalar_vector_WHEN_creating_translation_view_THEN_ui_is_filled_correctly(
    qtbot
):
    wrapper = NexusWrapper()
    instrument = Instrument(wrapper, {})

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
    qtbot
):
    wrapper = NexusWrapper()
    instrument = Instrument(wrapper, {})

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
    qtbot, file  # noqa:F811
):
    wrapper = NexusWrapper()
    instrument = Instrument(wrapper, {})

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
    qtbot, file  # noqa:F811
):
    wrapper = NexusWrapper(filename="test")
    instrument = Instrument(wrapper, {})

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
    qtbot
):
    wrapper = NexusWrapper(filename="asdfgsdfh")
    instrument = Instrument(wrapper, {})

    component = instrument.create_component("test", "NXaperture", "")

    x = 0
    y = 0
    z = 0
    path = "/entry"

    transform = component.add_rotation(QVector3D(x, y, z), 0, name="test")
    link = wrapper.instrument["asdfgh"] = h5py.SoftLink(path)

    transform.dataset = link

    view = EditRotation(parent=None, transformation=transform, instrument=instrument)
    qtbot.addWidget(view)

    assert view.transformation_frame.x_spinbox.value() == x
    assert view.transformation_frame.y_spinbox.value() == y
    assert view.transformation_frame.z_spinbox.value() == z
    assert view.transformation_frame.value_spinbox.value() == 0.0
    assert view.transformation_frame.magnitude_widget.field_type == FieldType.link
    assert view.transformation_frame.magnitude_widget.value.path == path
