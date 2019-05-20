import pint


def calculate_unit_conversion_factor(units: str):
    """
    Determines the factor for multiplying the geometry file points in order to convert it from its original units to
    metres.

    :param units: A unit of length in the form of a string.
    :return: A float value for converting between metres and the unit argument.
    """
    ureg = pint.UnitRegistry()
    input_quantity = 1.0 * ureg.parse_expression(units)
    return input_quantity.to(ureg.m).magnitude
