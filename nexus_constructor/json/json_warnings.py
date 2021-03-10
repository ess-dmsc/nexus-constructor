from typing import List, TypeVar, Union

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
class InvalidShape:
    message = attr.ib(type=str)


@attr.s
class InvalidTransformation:
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
    InvalidJson,
    InvalidShape,
    InvalidTransformation,
    TransformDependencyMissing,
    NameFieldMissing,
    NXClassAttributeMissing,
]

_T = TypeVar("_T", JsonWarning, "JsonWarningsContainer")


class JsonWarningsContainer(List[JsonWarning]):
    """
    This is a container class that should only store items of types given in JsonWarning.
    It does the necessary type checks before inserting new items into the container.
    """

    def __init__(self, *args, **kwargs):
        self._CHECK_TYPES = (JsonWarning.__args__, type(self))
        self.__add_constructor_param_items(args)
        self.__add_constructor_param_items(kwargs)

    def __add_constructor_param_items(self, other_items):
        if other_items:
            if not any(isinstance(item, self._CHECK_TYPES) for item in other_items):
                raise TypeError(
                    "The provided parameter to the constructor "
                    f"is not of type in {self._CHECK_TYPES}"
                )
            else:
                self.extend(other_items)

    def append(self, __object: _T) -> None:
        if __object and isinstance(__object, self._CHECK_TYPES):
            super().append(__object)
        else:
            raise TypeError(
                f"Tried to add item of type {type(__object)}."
                f" Item can only be added if it is of type in {self._CHECK_TYPES}"
            )

    def insert(self, __index: int, __object: _T) -> None:
        if __object and isinstance(__object, self._CHECK_TYPES):
            super().insert(__index, __object)
        else:
            raise TypeError(
                f"Tried to add item of type {type(__object)}."
                f" Item can only be inserted if it is of type in {self._CHECK_TYPES}"
            )

    def __add__(self, __object: _T) -> None:
        self.append(__object)
        return self

    def __iadd__(self, __object: _T) -> None:
        self.append(__object)
        return self
