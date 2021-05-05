from typing import TYPE_CHECKING, Any, Dict, List, Union

import attr
import numpy as np

from nexus_constructor.common_attrs import CommonAttrs, CommonKeys, NodeType
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.helpers import get_absolute_path
from nexus_constructor.model.value_type import ValueType

if TYPE_CHECKING:
    from nexus_constructor.model.group import Group  # noqa: F401


@attr.s
class Dataset:
    name = attr.ib(type=str)
    values = attr.ib(type=Union[List[ValueType], ValueType])
    type = attr.ib(type=str)
    size = attr.ib(factory=tuple)
    parent_node = attr.ib(type="Group", default=None)
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
        values = self.values
        if isinstance(values, np.ndarray):
            values = values.tolist()
        return_dict = {
            CommonKeys.MODULE: "dataset",
            NodeType.CONFIG: {
                CommonKeys.NAME: self.name,
                CommonKeys.DATA_TYPE: self.type,
                CommonKeys.VALUES: values,
            },
        }
        if self.attributes:
            return_dict[CommonKeys.ATTRIBUTES] = self.attributes.as_dict()
        return return_dict
