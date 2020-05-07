import pytest

pytest.skip("Disabled whilst working on model change", allow_module_level=True)
import numpy as np
from nexus_constructor.component.chopper_shape import ChopperShape
from nexus_constructor.component.component_shape import ComponentShape
from nexus_constructor.component.pixel_shape import PixelShape
from nexus_constructor.component.component_factory import create_component
from nexus_constructor.model.geometry import (
    OFFGeometryNoNexus,
    OFFGeometryNexus,
)
from nexus_constructor.model.geometry import NoShapeGeometry

"""
Tests here document the conditions under which the factory creates components of different types
"""


def add_dataset(group, name, data, attributes=None):
    if isinstance(data, str):
        dataset = group.create_dataset(
            name, data=np.array(data).astype("|S" + str(len(data)))
        )
    else:
        dataset = group.create_dataset(name, data=data)

    if attributes:
        for key in attributes:
            if isinstance(attributes[key], str):
                dataset.attrs.create(
                    key,
                    np.array(attributes[key]).astype("|S" + str(len(attributes[key]))),
                )
            else:
                dataset.attrs.create(key, np.array(attributes[key]))
    return dataset


def test_GIVEN_an_NXdisk_chopper_group_WHEN_calling_create_component_THEN_component_has_a_ChopperShape(
    nexus_wrapper,
):
    chopper_group = nexus_wrapper.create_nx_group(
        "chopper", "NXdisk_chopper", nexus_wrapper.instrument
    )
    new_component = create_component(nexus_wrapper, chopper_group)
    assert isinstance(new_component._shape, ChopperShape)
    assert isinstance(
        new_component.shape[0], NoShapeGeometry
    ), "Expect chopper component to return NoShapeGeometry as it has insufficient details to create a mesh of the disk shape"


def test_GIVEN_an_NXdisk_chopper_group_WHEN_calling_create_component_THEN_component_returns_OFFGeometry_of_chopper(
    nexus_wrapper,
):
    chopper_group = nexus_wrapper.create_nx_group(
        "chopper", "NXdisk_chopper", nexus_wrapper.instrument
    )
    add_dataset(
        chopper_group,
        "slit_edges",
        np.array(
            [
                83.71,
                94.7,
                140.49,
                155.79,
                193.26,
                212.56,
                242.32,
                265.33,
                287.91,
                314.37,
                330.3,
                360.0,
            ]
        )
        + 15.0,
        attributes={"units": "deg"},
    )
    add_dataset(chopper_group, "slits", 6)
    add_dataset(chopper_group, "slit_height", 130.0, attributes={"units": "mm"})
    add_dataset(chopper_group, "radius", 300.0, attributes={"units": "mm"})
    new_component = create_component(nexus_wrapper, chopper_group)
    assert isinstance(new_component._shape, ChopperShape)
    assert isinstance(new_component.shape[0], OFFGeometryNoNexus)
    assert (
        len(new_component.shape[0].vertices) > 8
    ), "Expect chopper geometry with many vertices, not just a placeholder cube with 8 vertices"


def test_GIVEN_an_nx_group_with_no_shape_WHEN_calling_create_component_THEN_component_has_a_ComponentShape(
    nexus_wrapper,
):
    monitor_group = nexus_wrapper.create_nx_group(
        "monitor", "NXmonitor", nexus_wrapper.instrument
    )
    new_component = create_component(nexus_wrapper, monitor_group)
    assert isinstance(new_component._shape, ComponentShape)


def test_GIVEN_an_nx_group_with_shape_WHEN_calling_create_component_THEN_component_returns_OFFGeometry(
    nexus_wrapper,
):
    monitor_group = nexus_wrapper.create_nx_group(
        "monitor", "NXmonitor", nexus_wrapper.instrument
    )
    new_component = create_component(nexus_wrapper, monitor_group)

    shape_group = nexus_wrapper.create_nx_group(
        "shape", "NXoff_geometry", new_component.group
    )
    vertices_dataset = nexus_wrapper.set_field_value(
        shape_group,
        "vertices",
        np.array([[0, 2, -2], [-1, -1, 1], [1, -1, 1]]),
        dtype=np.float,
    )
    nexus_wrapper.set_field_value(
        shape_group, "winding_order", np.array([0, 1, 2]), dtype=np.int32
    )
    nexus_wrapper.set_field_value(shape_group, "faces", np.array([0]), dtype=np.int32)
    nexus_wrapper.set_attribute_value(vertices_dataset, "units", "m")

    assert isinstance(new_component.shape[0], OFFGeometryNexus)


def test_GIVEN_an_NXdetector_group_with_detector_shape_WHEN_calling_create_component_THEN_component_has_a_ComponentShape(
    nexus_wrapper,
):
    detector_group = nexus_wrapper.create_nx_group(
        "detector", "NXdetector", nexus_wrapper.instrument
    )
    nexus_wrapper.create_nx_group("detector_shape", "NXoff_geometry", detector_group)
    new_component = create_component(nexus_wrapper, detector_group)
    assert isinstance(new_component._shape, ComponentShape)


def test_GIVEN_an_NXdetector_group_with_pixel_shape_WHEN_calling_create_component_THEN_component_has_a_PixelShape(
    nexus_wrapper,
):
    detector_group = nexus_wrapper.create_nx_group(
        "detector", "NXdetector", nexus_wrapper.instrument
    )
    nexus_wrapper.create_nx_group("pixel_shape", "NXoff_geometry", detector_group)
    new_component = create_component(nexus_wrapper, detector_group)
    assert isinstance(new_component._shape, PixelShape)
