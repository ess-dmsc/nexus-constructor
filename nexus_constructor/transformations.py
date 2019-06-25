import attr
import numpy as np
from PySide2.QtGui import QVector3D
from typing import Any


def create_transform(type: str, vector: np.array, value: Any):
    if type == "Rotation":
        return Rotation(type, QVector3D(vector[0], vector[1], vector[2]), value)
    if type == "Translation":
        return Translation(type, value * vector)
    raise ValueError("Unexpected transformation type encountered in create_transform()")


@attr.s
class Transformation:
    name = attr.ib(str)
    type = "Transformation"


def validate_nonzero_vector(instance, attribute, vector: QVector3D):
    """
    Returns True if the vector does not contain (0,0,0), otherwise returns False
    """
    if vector.isNull():
        raise ValueError


@attr.s
class Rotation(Transformation):
    axis = attr.ib(
        factory=lambda: QVector3D(0, 0, 1),
        type=QVector3D,
        validator=validate_nonzero_vector,
    )
    angle = attr.ib(default=0)
    type = "Rotation"


@attr.s
class Translation(Transformation):
    vector = attr.ib(factory=lambda: QVector3D(0, 0, 0), type=QVector3D)
    type = "Translation"
