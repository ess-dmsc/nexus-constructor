from PySide2.QtGui import QVector3D
import numpy as np


def validate_nonzero_qvector(value: QVector3D):
    if value.x() == 0 and value.y() == 0 and value.z() == 0:
        raise ValueError("Vector is zero length")


def get_an_orthogonal_unit_vector(input_vector: QVector3D):
    """
    Return a unit vector which is orthogonal to the input vector
    There are infinite valid solutions, just one is returned
    """
    if np.abs(input_vector.z()) < np.abs(input_vector.x()):
        vector = QVector3D(input_vector.x(), -input_vector.y(), 0.0)
        return vector.normalized()
    return QVector3D(0.0, -input_vector.z(), input_vector.y()).normalized()
