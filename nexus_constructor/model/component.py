import attr

from nexus_constructor.model.group import Group
from nexus_constructor.model.helpers import get_item, set_item


@attr.s
class Component(Group):
    @property
    def description(self):
        return get_item(self.children, "description")

    @description.setter
    def description(self, new_description: str):
        set_item(self.children, "description", new_description)

    @property
    def shape(self):
        # Do stuff here with shape
        pass
