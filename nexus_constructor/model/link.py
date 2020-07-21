import attr


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)
    type = attr.ib(type=str, default="link", init=False)

    def as_dict(self):
        return {"name": self.name, "target": self.target, "type": self.type}
