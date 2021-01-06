import attr


# frozen=True makes objects hashable
@attr.s(frozen=True)
class TransformId:
    component_name = attr.ib(type=str)
    transform_name = attr.ib(type=str)
