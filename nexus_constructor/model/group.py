import attr

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.helpers import (
    get_item,
    set_item,
    set_attribute_value,
    get_attribute_value,
)


@attr.s
class Group:
    """
    Base class for any group which has a set of children and an nx_class attribute.
    """

    name = attr.ib(type=str)
    attributes = attr.ib(default=[])
    children = attr.ib(default=[])

    def __getitem__(self, key):
        return get_item(self.children, key)

    def __setitem__(self, key, value):
        set_item(self.children, key, value)

    @property
    def nx_class(self):
        return get_attribute_value(self.attributes, CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        set_attribute_value(
            self.attributes, CommonAttrs.NX_CLASS, new_nx_class,
        )


class Instrument(Group):
    def __init__(self):
        self.nx_class = "NXinstrument"


class Entry(Group):
    def __init__(self):
        self.nx_class = "NXentry"
