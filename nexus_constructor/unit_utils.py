import logging

import pint

RADIANS = "radians"
METRES = "metres"
DEGREES = "deg"


ureg = pint.UnitRegistry()


def units_are_recognised_by_pint(input: str, emit_logging_msg: bool = True) -> bool:
    """
    Checks if a string is a unit that can be recognised by pint.
    :param input: The units string.
    :param emit_logging_msg: A bool indicating whether the logging message should be emitted. Sometimes false because
        the function calling `units_are_recognised_by_pint` may have a more detailed logging message it produces when
        `units_are_recognised_by_pint` returns false.
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


def units_are_expected_dimensionality(
    input: str, expected_unit_type: str, emit_logging_msg=True
) -> bool:
    """
    Checks if a unit is the expected dimensionality by trying to convert it.
    :param input: The units string.
    :return: True if the conversion was successful, False otherwise.
    """
    try:
        ureg(input).to(expected_unit_type)
    except (pint.errors.DimensionalityError, ValueError, AttributeError):
        if emit_logging_msg:
            logging.info(
                f"Unit input {input} has wrong type. Expected something that could be converted to {expected_unit_type}."
            )
        return False

    return True


def units_have_magnitude_of_one(input: str, emit_logging_msg=True) -> bool:
    """
    Checks that the unit has a magnitude of one. This will cause the checks to reject input in the form of "40cm,"
    "2 radians," etc.
    :param input: The units string.
    :return: True if the unit has a magnitude of one, False otherwise.
    """
    unit = ureg(input)
    if not isinstance(unit, ureg.Quantity):
        return False
    if unit.magnitude != 1:
        if emit_logging_msg:
            logging.info(
                f"Unit input {input} has wrong magnitude. The input should have a magnitude of one."
            )
        return False
    return True


def calculate_unit_conversion_factor(original_units: str, desired_units: str) -> float:
    """
    Determines the factor for multiplying values in the original units so that they are now in the desired units.
    :param original_units: The original units.
    :param desired_units: The units that the original units are to be converted to.
    :return: A float value for converting from the original units and the desired units.
    """
    return ureg(original_units).to(desired_units).magnitude
