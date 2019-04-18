import attr
from PySide2.QtGui import QVector3D


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
