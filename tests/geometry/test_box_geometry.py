from pytest import approx

from nexus_constructor.model.component import Component


def test_box_has_property_values_it_was_created_with():
    component = Component("test")
    length = 1.0
    width = 2.0
    height = 3.0
    units = "m"
    box = component.set_box_shape(
        height=height, width=width, length=length, units=units
    )

    assert box.size[0] == approx(length)
    assert box.size[1] == approx(width)
    assert box.size[2] == approx(height)
    assert box.units == units
