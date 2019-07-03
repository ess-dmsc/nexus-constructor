from pytest import approx, raises
from PySide2.QtGui import QVector3D
from .helpers import create_nexus_wrapper, add_component_to_file


def test_cylinder_has_property_values_it_was_created_with():
    nexus_wrapper = create_nexus_wrapper()
    component = add_component_to_file(nexus_wrapper)
    height = 3
    radius = 4
    cylinder = component.add_cylinder(
        axis_direction=QVector3D(1, 0, 0), height=height, radius=radius, units="m"
    )

    assert cylinder.radius == approx(radius)
    assert cylinder.height == approx(height)
    assert cylinder.geometry_str == "Cylinder"


def test_axis_direction_must_be_non_zero():
    nexus_wrapper = create_nexus_wrapper()
    component = add_component_to_file(nexus_wrapper)
    height = 3
    radius = 4
    with raises(ValueError):
        component.add_cylinder(
            axis_direction=QVector3D(0, 0, 0), height=height, radius=radius, units="m"
        )
