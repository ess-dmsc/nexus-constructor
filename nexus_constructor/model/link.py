import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType

TARGET = "target"


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)

    def as_dict(self):
        return {
            CommonKeys.NAME: self.name,
            TARGET: self.target,
            CommonKeys.DATA_TYPE: NodeType.LINK,
        }
