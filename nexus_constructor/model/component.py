import attr

from nexus_constructor.model.group import Group


@attr.s
class Component(Group):
    @property
    def description(self):
        return self["description"]

    @description.setter
    def description(self, new_description: str):
        self["description"] = new_description
