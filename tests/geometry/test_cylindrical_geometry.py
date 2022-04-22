import pytest
from PySide2.QtGui import QVector3D
from pytest import approx

from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import CylindricalGeometry
from nexus_constructor.ui_utils import numpy_array_to_qvector3d


def test_cylinder_has_property_values_it_was_created_with():
    component = Component("test")
    height = 3
    radius = 4
    units = "cubits"
    cylinder = component.set_cylinder_shape(
        axis_direction=QVector3D(1, 0, 0), height=height, radius=radius, units=units
    )

    assert cylinder.radius == approx(radius)
    assert cylinder.height == approx(height)
    assert cylinder.units == units


def test_axis_direction_must_be_non_zero():
    component = Component("test")
    height = 3
    radius = 4
    assert not component.set_cylinder_shape(
        axis_direction=QVector3D(0, 0, 0), height=height, radius=radius, units="m"
    )


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
    vertices = CylindricalGeometry.calculate_vertices(axis_direction, height, radius)
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
    vertices = CylindricalGeometry.calculate_vertices(axis_direction, height, radius)
    base_centre = numpy_array_to_qvector3d(vertices[0][:])
    base_edge = numpy_array_to_qvector3d(vertices[1][:])
    top_centre = numpy_array_to_qvector3d(vertices[2][:])

    output_axis = top_centre - base_centre
    output_radius = base_edge - base_centre

    assert output_axis.length() == approx(height)
    assert output_radius.length() == approx(radius)
