import attr
import numpy as np
from nexus_constructor.model.value_type import ValueType


@attr.s(eq=None)
class FieldAttribute:
    """
    Class for containing attributes in the nexus structure.
    Uses the long format (dict with "name" and "values" as keys) in the file-writer JSON format
    rather than the short form (name:value) as this works for everything and is more flexible, with
    the trade-off being a longer message (which is not a priority)
    """

    name = attr.ib(type=str)
    values = attr.ib(type=ValueType, cmp=False)

    def __eq__(self, other_attribute):
        assert self.name == other_attribute.name
        if np.isscalar(self.values):
            return self.values == other_attribute.values
        return self.values.all(other_attribute)
