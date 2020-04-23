from typing import List

import attr

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.attribute import FieldAttribute
from nexus_constructor.model.node import Node


@attr.s
class DatasetMetadata:
    size = attr.ib(type=List)
    type = attr.ib(type=str)


@attr.s
class Dataset(Node):
    dataset = attr.ib(type=DatasetMetadata)
    values = attr.ib(type=List, default=attr.Factory(list))
    type = attr.ib(type=str, default="dataset")
    attributes = attr.ib(type=List[FieldAttribute], default=attr.Factory(list))

    @property
    def nx_class(self):
        return self.get_attribute_value(CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        self.set_attribute_value(
            CommonAttrs.NX_CLASS, new_nx_class,
        )
