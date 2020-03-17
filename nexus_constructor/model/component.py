import attr

from nexus_constructor.model.group import Group


@attr.s
class Component(Group):
    @property
    def description(self):
        return self.children["description"] if "description" in self.children else None

    @description.setter
    def description(self, new_description):
        self.children["description"] = new_description

    @property
    def shape(self):
        # Do stuff here with shape
        pass
