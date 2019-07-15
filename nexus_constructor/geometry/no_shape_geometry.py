from nexus_constructor.geometry.off_geometry import OFFGeometry, OFFGeometryNoNexus
from PySide2.QtGui import QVector3D

__half_side_length = 0.5

OFFCube = OFFGeometryNoNexus(
    vertices=[
        QVector3D(-__half_side_length, -__half_side_length, __half_side_length),
        QVector3D(__half_side_length, -__half_side_length, __half_side_length),
        QVector3D(-__half_side_length, __half_side_length, __half_side_length),
        QVector3D(__half_side_length, __half_side_length, __half_side_length),
        QVector3D(-__half_side_length, __half_side_length, -__half_side_length),
        QVector3D(__half_side_length, __half_side_length, -__half_side_length),
        QVector3D(-__half_side_length, -__half_side_length, -__half_side_length),
        QVector3D(__half_side_length, -__half_side_length, -__half_side_length),
    ],
    faces=[
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
        [6, 7, 1, 0],
        [1, 7, 5, 3],
        [6, 0, 2, 4],
    ],
)


class NoShapeGeometry:
    """
    Dummy object for components with no geometry.
    """

    geometry_str = "None"

    def __init__(self):
        pass

    @property
    def off_geometry(self) -> OFFGeometry:
        return OFFCube
