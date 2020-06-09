import attr

from nexus_constructor.model.value_type import ValueType


@attr.s
class FieldAttribute:
    """
    Class for containing attributes in the nexus structure.
    Uses the long format (dict with "name" and "values" as keys) in the file-writer JSON format
    rather than the short form (name:value) as this works for everything and is more flexible, with
    the trade-off being a longer message (which is not a priority)
    """

    name = attr.ib(type=str)
    values = attr.ib(type=ValueType)
