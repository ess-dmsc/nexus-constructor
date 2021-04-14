import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType

TARGET = "target"


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)
    parent_node = None
    attributes = None
    values = None

    def as_dict(self):
        return {
            CommonKeys.NAME: self.name,
            TARGET: self.target,
            CommonKeys.TYPE: NodeType.LINK,
        }
