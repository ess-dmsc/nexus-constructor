import attr


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)

    def as_dict(self):
        return {"name": self.name, "target": self.target, "type": "link"}
