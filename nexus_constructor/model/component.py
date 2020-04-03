import attr

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.attribute import FieldAttribute
from nexus_constructor.model.group import Group


@attr.s
class Component(Group):
    @property
    def description(self):
        return self[CommonAttrs.DESCRIPTION]

    @description.setter
    def description(self, new_description: str):
        self[CommonAttrs.DESCRIPTION] = FieldAttribute(CommonAttrs.DESCRIPTION, new_description)
