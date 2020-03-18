from typing import Any

import attr


@attr.s
class FieldAttribute:
    name = attr.ib(type=str)
    values = attr.ib(type=Any)
