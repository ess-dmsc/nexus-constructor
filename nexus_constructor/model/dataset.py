import attr
from typing import List, Dict, Any
import numpy as np

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.helpers import get_absolute_path
from nexus_constructor.model.value_type import ValueType


@attr.s
class Dataset:
    name = attr.ib(type=str)
    values = attr.ib(type=List[ValueType])
    type = attr.ib(type=str)
    size = attr.ib(factory=tuple)
    parent_node = attr.ib(type="Node", default=None)
    attributes = attr.ib(type=Attributes, factory=Attributes, init=False)

    @property
    def absolute_path(self):
        return get_absolute_path(self)

    @property
    def nx_class(self):
        return self.attributes.get_attribute_value(CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        self.attributes.set_attribute_value(CommonAttrs.NX_CLASS, new_nx_class)

    def as_dict(self) -> Dict[str, Any]:
        return_dict = {}
        return_dict["name"] = self.name
        if self.attributes:
            return_dict["attributes"] = self.attributes.as_dict()
        values = self.values
        if isinstance(values, np.ndarray):
            values = values.tolist()
        return_dict["type"] = "dataset"
        return_dict["values"] = values
        return_dict["dataset"] = {"type": self.type, "size": self.size}
        return return_dict
