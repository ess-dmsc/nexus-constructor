import pint

RADIANS = "radians"
METRES = "metres"

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
        ureg(expected_unit_type).to(input)
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


def calculate_unit_conversion_factor(units: str, desired_units: str) -> float:
    """
    Determines the factor for multiplying values in the original units so that they are now in the desired units.
    :param units: The original units.
    :param desired_units: The units that to be used for the conversion.
    :return: A float value for converting between the original units and the desired units.
    """
    input_quantity = 1.0 * ureg.parse_expression(units)
    return input_quantity.to(desired_units).magnitude
