from pytest import approx

from nexus_constructor.unit_utils import METRES, calculate_unit_conversion_factor


def test_unit_conversion_factor():
    # List of units and their expected value in metres
    units = [("cm", 0.01), ("km", 1000), ("m", 1.0), ("inch", 0.0254), ("foot", 0.3048)]

    # Check that the unit conversion factor can correctly find the unit in terms of meters
    for unit in units:
        assert approx(calculate_unit_conversion_factor(unit[0], METRES)) == unit[1]
