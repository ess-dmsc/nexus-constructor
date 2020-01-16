from mock import patch
from numpy import array_equal, array
from pytest import approx, raises
import pytest
from PySide2.QtGui import QVector3D

from nexus_constructor.pixel_data import PixelMapping
from .helpers import add_component_to_file
from nexus_constructor.geometry.cylindrical_geometry import (
    calculate_vertices,
    CylindricalGeometry,
)
from nexus_constructor.ui_utils import numpy_array_to_qvector3d


@pytest.fixture
def nx_cylindrical_geometry(nexus_wrapper):
    return nexus_wrapper.create_nx_group(
        "test_geometry", "NXcylindrical_geometry", nexus_wrapper.entry
    )


def test_cylinder_has_property_values_it_was_created_with(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper)
    height = 3
    radius = 4
    units = "cubits"
    cylinder = component.set_cylinder_shape(
        axis_direction=QVector3D(1, 0, 0), height=height, radius=radius, units=units
    )

    assert cylinder.radius == approx(radius)
    assert cylinder.height == approx(height)
    assert cylinder.units == units
    assert cylinder.geometry_str == "Cylinder"


def test_cylinder_units_returns_str_if_bytes_in_file(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper)
    units_bytes = b"cubits"
    cylinder = component.set_cylinder_shape(
        axis_direction=QVector3D(1, 0, 0), height=3, radius=4, units=units_bytes
    )
    units_str = units_bytes.decode("utf-8")

    assert cylinder.units == units_str


def test_axis_direction_must_be_non_zero(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper)
    height = 3
    radius = 4
    with raises(ValueError):
        component.set_cylinder_shape(
            axis_direction=QVector3D(0, 0, 0), height=height, radius=radius, units="m"
        )


def test_creating_cylinder_from_file_with_multiple_cylinders_in_single_group_ignores_all_but_the_first_cylinder(
    nexus_wrapper
):
    height_cyl_1 = 4.2
    radius_cyl_1 = 4.2
    height_cyl_2 = 3.5
    radius_cyl_2 = 3.5
    cylinders_group = nexus_wrapper.create_nx_group(
        "cylinders", "NXcylindrical_geometry", nexus_wrapper.nexus_file
    )
    vertices = [
        [-0.5 * height_cyl_1, 0, 0],
        [-0.5 * height_cyl_1, -radius_cyl_1, 0],
        [0.5 * height_cyl_1, 0, 0],
        [-0.5 * height_cyl_2, 0, 0],
        [-0.5 * height_cyl_2, -radius_cyl_2, 0],
        [0.5 * height_cyl_2, 0, 0],
    ]
    vertices_dataset = nexus_wrapper.set_field_value(
        cylinders_group, "vertices", vertices
    )
    nexus_wrapper.set_attribute_value(vertices_dataset, "units", "m")
    cylinders = [[0, 1, 2], [3, 4, 5]]
    nexus_wrapper.set_field_value(cylinders_group, "cylinders", cylinders)

    cylinder = CylindricalGeometry(nexus_wrapper, cylinders_group)
    assert cylinder.radius == approx(radius_cyl_1)
    assert cylinder.height == approx(height_cyl_1)


def test_get_expected_height_and_radius_when_cylinder_vertices_are_out_of_order_in_nexus_file(
    nexus_wrapper
):
    height_cyl = 4.2
    radius_cyl = 3.7
    cylinders_group = nexus_wrapper.create_nx_group(
        "cylinders", "NXcylindrical_geometry", nexus_wrapper.nexus_file
    )
    vertices = [
        [-0.5 * height_cyl, 0, 0],
        [0.5 * height_cyl, 0, 0],
        [-0.5 * height_cyl, -radius_cyl, 0],
    ]
    vertices_dataset = nexus_wrapper.set_field_value(
        cylinders_group, "vertices", vertices
    )
    nexus_wrapper.set_attribute_value(vertices_dataset, "units", "m")
    cylinders = [[0, 2, 1]]  # not in 0,1,2 order
    nexus_wrapper.set_field_value(cylinders_group, "cylinders", cylinders)

    cylinder = CylindricalGeometry(nexus_wrapper, cylinders_group)
    assert cylinder.radius == approx(radius_cyl)
    assert cylinder.height == approx(height_cyl)


@pytest.mark.parametrize(
    "axis_direction,height,radius",
    [
        (QVector3D(1, 0, 0), 1.0, 1.0),
        (QVector3D(2, 3, 8), 0.5, 1.7),
        (QVector3D(0, -1, 0), 42.0, 4.2),
    ],
)
def test_calculate_vertices_gives_cylinder_centre_at_origin(
    axis_direction, height, radius
):
    vertices = calculate_vertices(axis_direction, height, radius)
    base_centre = numpy_array_to_qvector3d(vertices[:][0])
    top_centre = numpy_array_to_qvector3d(vertices[:][2])
    cylinder_centre = top_centre + base_centre

    assert cylinder_centre.x() == approx(0), "Expect cylinder centre to be at 0, 0, 0"
    assert cylinder_centre.y() == approx(0), "Expect cylinder centre to be at 0, 0, 0"
    assert cylinder_centre.z() == approx(0), "Expect cylinder centre to be at 0, 0, 0"


@pytest.mark.parametrize(
    "axis_direction,height,radius",
    [
        (QVector3D(1, 0, 0), 1.0, 1.0),
        (QVector3D(2, 3, 8), 0.5, 1.7),
        (QVector3D(0, -1, 0), 42.0, 4.2),
    ],
)
def test_calculate_vertices_gives_vertices_consistent_with_specified_height_and_radius(
    axis_direction, height, radius
):
    vertices = calculate_vertices(axis_direction, height, radius)
    base_centre = numpy_array_to_qvector3d(vertices[0][:])
    base_edge = numpy_array_to_qvector3d(vertices[1][:])
    top_centre = numpy_array_to_qvector3d(vertices[2][:])

    output_axis = top_centre - base_centre
    output_radius = base_edge - base_centre

    assert output_axis.length() == approx(height)
    assert output_radius.length() == approx(radius)


def test_GIVEN_pixel_ids_WHEN_initialising_cylindrical_geometry_THEN_ids_in_geometry_match_ids_in_mapping(
    nexus_wrapper, nx_cylindrical_geometry
):

    num_detectors = 6
    expected_dataset = [i for i in range(num_detectors)]
    pixel_mapping = PixelMapping(expected_dataset)

    # Patch the validation method so that it doesn't mind information being absent from the NeXus group
    with patch(
        "nexus_constructor.geometry.cylindrical_geometry.CylindricalGeometry._verify_in_file"
    ):
        cylindrical_geometry = CylindricalGeometry(
            nexus_wrapper, nx_cylindrical_geometry, pixel_mapping
        )

    actual_dataset = cylindrical_geometry.detector_number

    assert array_equal(array(expected_dataset), actual_dataset)
