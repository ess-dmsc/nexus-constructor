import pint

ureg = pint.UnitRegistry()


def units_are_recognised_by_pint(input: str) -> bool:
    """
    Checks if a string is a unit that can be recognised by pint.
    :param input: The units string.
    :return: True if the unit is contained in the pint registry, False otherwise.
    """
    try:
        ureg(input)
    except (
        pint.errors.UndefinedUnitError,
        AttributeError,
        pint.compat.tokenize.TokenError,
    ):
        return False

    return True


def units_are_expected_type(input: str, expected_unit_type: str) -> bool:
    """
    Checks if a unit is the expected type by trying to convert it.
    :param input: The units string.
    :return: True if the conversion was successful, False otherwise.
    """
    try:
        ureg(input).to(expected_unit_type)
    except (pint.errors.DimensionalityError, ValueError):
        return False

    return True


def units_have_dimension_of_one(input: str) -> bool:
    """
    Checks that the unit has a dimension of one. This will cause the checks to reject input in the form of "40cm,"
    "2 radians," etc.
    :param input: The units string.
    :return: True if the unit has a dimension of one, False otherwise.
    """
    return ureg(input).magnitude == 1


def calculate_unit_conversion_factor(units: str):
    """
    Determines the factor for multiplying the geometry file points in order to convert it from its original units to
    metres.
    :param units: A unit of length in the form of a string.
    :return: A float value for converting between metres and the unit argument.
    """
    input_quantity = 1.0 * ureg.parse_expression(units)
    return input_quantity.to(ureg.m).magnitude
