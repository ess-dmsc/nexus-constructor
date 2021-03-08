from typing import Union

import attr

"""
The message field should be populated with a string that makes sense to a user
The warning messages are wrapped in these classes to facilitate testing that
the expected warning is triggered without having to test exact warning string
"""


@attr.s
class InvalidJson:
    message = attr.ib(type=str)


@attr.s
class TransformDependencyMissing:
    message = attr.ib(type=str)


@attr.s
class NameFieldMissing:
    message = attr.ib(type=str)


@attr.s
class NXClassAttributeMissing:
    message = attr.ib(type=str)


JsonWarning = Union[
    InvalidJson, TransformDependencyMissing, NameFieldMissing, NXClassAttributeMissing
]
