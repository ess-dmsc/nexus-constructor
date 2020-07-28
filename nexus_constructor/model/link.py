import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)

    def as_dict(self):
        return {CommonKeys.NAME: self.name, "target": self.target, CommonKeys.TYPE: NodeType.LINK}
