import pint


def calculate_unit_conversion_factor(units):
    """
    Determines the factor for multiplying the geometry file points in order to convert it from its original units to
    metres.

    :param units: A unit of length in the form of a string.
    :return: A float value for converting between metres and the unit argument.
    """
    ureg = pint.UnitRegistry()
    units = ureg(units)
    units = ureg.m.from_(units)
    return units.magnitude
