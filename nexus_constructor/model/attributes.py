from typing import Any, Dict

import attr
import numpy as np

from nexus_constructor.common_attrs import CommonKeys
from nexus_constructor.model.helpers import _get_item, _set_item
from nexus_constructor.model.value_type import ValueType, ValueTypes


class Attributes(list):
    """Abstract class used for common functionality between a group and dataset."""

    def set_attribute_value(
        self,
        attribute_name: str,
        attribute_value: Any,
        attribute_type: str = ValueTypes.STRING,
    ):
        _set_item(
            self,
            self,
            attribute_name,
            FieldAttribute(
                name=attribute_name, values=attribute_value, type=attribute_type
            ),
        )

    def get_attribute_value(self, attribute_name: str):
        return _get_item(self, attribute_name).values

    def contains_attribute(self, attribute_name):
        result = _get_item(self, attribute_name)
        return True if result is not None else False

    def as_dict(self):
        return [attribute.as_dict() for attribute in self]


@attr.s(eq=False)
class FieldAttribute:
    """
    Class for containing attributes in the nexus structure.
    Uses the long format (dict with "name" and "values" as keys) in the file-writer JSON format
    rather than the short form (name:value) as this works for everything and is more flexible, with
    the trade-off being a longer message (which is not a priority)
    """

    name = attr.ib(type=str)
    values = attr.ib(type=ValueType, cmp=False)
    type = attr.ib(type=str, default=ValueTypes.STRING)

    def __eq__(self, other_attribute):
        if not self.name == other_attribute.name:
            return False
        if np.isscalar(self.values) or isinstance(self.values, list):
            return self.values == other_attribute.values
        return np.array_equal(self.values, other_attribute.values)

    def as_dict(self) -> Dict[str, Any]:
        values = self.values
        if isinstance(values, np.ndarray):
            values = values.tolist()
        return {
            CommonKeys.NAME: self.name,
            CommonKeys.DATA_TYPE: self.type,
            CommonKeys.VALUES: values,
        }
