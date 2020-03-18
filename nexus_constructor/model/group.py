import attr

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.helpers import get_item, set_item


@attr.s
class Group:
    name = attr.ib()
    attributes = attr.ib(default=[])
    children = attr.ib(default=[])

    def __getitem__(self, key):
        return get_item(self.children, key)

    def __setitem__(self, key, value):
        set_item(self.children, key, value)

    @property
    def nx_class(self):
        return get_item(self.attributes, CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        set_item(self.attributes, CommonAttrs.NX_CLASS, new_nx_class)
