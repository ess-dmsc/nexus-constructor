import attr


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)
    type = attr.ib(type=str, default="link", init=False)
