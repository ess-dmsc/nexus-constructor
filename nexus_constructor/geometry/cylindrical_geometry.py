from PySide2.QtGui import QVector3D, QMatrix4x4
from PySide2.Qt3DExtras import Qt3DExtras
from math import acos, degrees
import h5py
import numpy as np
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.nexus.validation import (
    NexusFormatError,
    ValidateDataset,
    validate_group,
)
from nexus_constructor.ui_utils import (
    numpy_array_to_qvector3d,
    qvector3d_to_numpy_array,
)
from nexus_constructor.geometry.utils import get_an_orthogonal_unit_vector
from typing import Tuple


def calculate_vertices(
    axis_direction: QVector3D, height: float, radius: float
) -> np.ndarray:
    """
    Given cylinder axis, height and radius, calculate the base centre, base edge and top centre vertices
    :param axis_direction: axis of the cylinder (not required to be unit vector)
    :param height: height of the cylinder
    :param radius: radius of the cylinder
    :return: base centre, base edge and top centre vertices as a numpy array
    """
    axis_direction = axis_direction.normalized()
    top_centre = axis_direction * height / 2.0
    base_centre = axis_direction * height / -2.0
    radial_direction = get_an_orthogonal_unit_vector(axis_direction).normalized()
    base_edge = base_centre + (radius * radial_direction)
    vertices = np.vstack(
        (
            qvector3d_to_numpy_array(base_centre),
            qvector3d_to_numpy_array(base_edge),
            qvector3d_to_numpy_array(top_centre),
        )
    )
    return vertices


class CylindricalGeometry:
    """
    Describes the shape of a cylinder in 3D space. The cylinder's centre is the origin of the local coordinate system.
    This wrapper does not have setters, delete cylinder and create a new one if the cylinder needs to change.

    Note, the NXcylindrical_geometry group can describe multiple cylinders, but here we are using it only for one.
    """

    geometry_str = "Cylinder"

    def __init__(self, nexus_file: nx.NexusWrapper, group: h5py.Group):
        self.file = nexus_file
        self.group = group
        self._verify_in_file()

    def _verify_in_file(self):
        """
        Check all the datasets and attributes we require are in the NXcylindrical_geometry group
        """
        problems = validate_group(
            self.group,
            "NXcylindrical_geometry",
            (
                ValidateDataset(
                    "vertices", shape=(None, 3), attributes={"units": None}
                ),
                ValidateDataset("cylinders"),
            ),
        )
        if problems:
            raise NexusFormatError("\n".join(problems))

    @property
    def units(self) -> str:
        return str(self.group["vertices"].attrs["units"])

    @property
    def height(self) -> float:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.length()

    def _get_cylinder_vertices(self) -> Tuple[QVector3D, QVector3D, QVector3D]:
        """
        Get the three points defining the cylinder
        We define "base" as the end of the cylinder in the -ve axis direction
        :return: base centre point, base edge point, top centre point
        """
        # flatten cylinders in case there are multiple cylinders defined, we'll take the first three elements,
        # so effectively any cylinder after the first one is ignored
        cylinders = self.file.get_field_value(self.group, "cylinders").flatten()
        vertices = self.file.get_field_value(self.group, "vertices")
        return tuple(
            numpy_array_to_qvector3d(vertices[cylinders[i], :]) for i in range(3)
        )

    @property
    def radius(self) -> float:
        base_centre, base_edge, _ = self._get_cylinder_vertices()
        cylinder_radius = base_edge - base_centre
        return cylinder_radius.length()

    @property
    def axis_direction(self) -> QVector3D:
        base_centre, _, top_centre = self._get_cylinder_vertices()
        cylinder_axis = top_centre - base_centre
        return cylinder_axis.normalized()

    @property
    def mesh(self) -> Qt3DExtras.QCylinderMesh:
        geom = Qt3DExtras.QCylinderMesh()
        geom.setLength(self.height)
        geom.setRadius(self.radius)
        return geom

    def _rotation_matrix(self) -> QMatrix4x4:
        """
        :return: A QMatrix4x4 describing the rotation from the Z axis to the cylinder's axis
        """
        default_axis = QVector3D(0, 0, 1)
        desired_axis = self.axis_direction.normalized()
        rotate_axis = QVector3D.crossProduct(desired_axis, default_axis)
        rotate_radians = acos(QVector3D.dotProduct(desired_axis, default_axis))
        rotate_matrix = QMatrix4x4()
        rotate_matrix.rotate(degrees(rotate_radians), rotate_axis)
        return rotate_matrix
