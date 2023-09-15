from typing import Iterable, List, TypeVar, Union

import attr

"""
The message field should be populated with a string that makes sense to a user
The warning messages are wrapped in these classes to facilitate testing that
the expected warning is triggered without having to test exact warning string
"""


@attr.s
class InvalidJson:
    message: str = attr.ib()


@attr.s
class InvalidShape:
    message: str = attr.ib()


@attr.s
class InvalidTransformation:
    message: str = attr.ib()


@attr.s
class TransformDependencyMissing:
    message: str = attr.ib()


@attr.s
class RelativeDependsonWrong:
    message = attr.ib(type=str)


@attr.s
class NameFieldMissing:
    message: str = attr.ib()


@attr.s
class NXClassAttributeMissing:
    message: str = attr.ib()


JsonWarning = Union[
    InvalidJson,
    InvalidShape,
    InvalidTransformation,
    TransformDependencyMissing,
    RelativeDependsonWrong,
    NameFieldMissing,
    NXClassAttributeMissing,
]


_T = TypeVar("_T", bound=JsonWarning)


class JsonWarningsContainer(List[JsonWarning]):
    """
    This is a container class that should only store items of types given in JsonWarning.
    It does the necessary type checks before inserting new items into the container.
    """

    def __init__(self, *args, **kwargs):
        # Using type ignore here as API for typing package is very limited and
        # __args__ has to be used.
        self._CHECK_TYPES = (JsonWarning.__args__, type(self))  # type: ignore
        self.__add_constructor_param_items(args)
        self.__add_constructor_param_items(kwargs)

    def __add_constructor_param_items(self, other_items):
        """
        Internal method to add items into the container if they are provided in
        the constructor call.
        """
        if other_items:
            if not any(isinstance(item, self._CHECK_TYPES) for item in other_items):
                raise TypeError(
                    "The provided parameter to the constructor "
                    f"is not of type in {self._CHECK_TYPES}"
                )
            else:
                self.extend(other_items)

    def append(self, __object: _T) -> None:
        """
        Overriding the append function so that a type check is done before new
        items are appended into the container via the append function in the
        superclass.
        """
        if isinstance(__object, self._CHECK_TYPES):
            super().append(__object)
        else:
            raise TypeError(
                f"Tried to add item of type {type(__object)}."
                f" Item can only be added if it is of type in {self._CHECK_TYPES}"
            )

    def insert(self, __index: int, __object: _T) -> None:
        """
        Overriding the insert function so that a type check is done before new
        items are inserted into the container via the insert function in the
        superclass.
        """
        if isinstance(__object, self._CHECK_TYPES):
            super().insert(__index, __object)
        else:
            raise TypeError(
                f"Tried to add item of type {type(__object)}."
                f" Item can only be inserted if it is of type in {self._CHECK_TYPES}"
            )

    def __add__(self, other: List[JsonWarning]) -> List[JsonWarning]:
        """
        Overriding the primitive add operation in list by checking that
        other is of type JsonWarningsContainer.
        """
        if isinstance(other, JsonWarningsContainer):
            return super().__add__(other)
        else:
            raise TypeError("It is only possible to add a JsonWarningsContainer.")

    def __iadd__(self, other: Iterable[JsonWarning]) -> "JsonWarningsContainer":
        """
        Overriding the primitive add-assign operation in list by checking that
        other is of type JsonWarningsContainer.
        """
        if isinstance(other, JsonWarningsContainer):
            return super().__iadd__(other)
        else:
            raise TypeError(
                "It is only possible to concatenate a JsonWarningsContainer."
            )
