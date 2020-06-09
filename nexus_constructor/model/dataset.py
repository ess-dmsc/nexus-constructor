import attr
from typing import List

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.node import Node
from nexus_constructor.model.value_type import ValueType


@attr.s
class DatasetMetadata:
    type = attr.ib(type=str)
    size = attr.ib(factory=tuple)


@attr.s
class Dataset(Node):
    dataset = attr.ib(type=DatasetMetadata)
    values = attr.ib(factory=list, type=List[ValueType])
    type = attr.ib(type=str, default="dataset", init=False)

    @property
    def nx_class(self):
        return self.get_attribute_value(CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        self.set_attribute_value(CommonAttrs.NX_CLASS, new_nx_class)
