import attr
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QVector3D, QMatrix4x4
import numpy as np

from nexus_constructor.model.group import Group
from nexus_constructor.model.helpers import (
    set_attribute_value,
    get_attribute_value,
)
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.transformation_types import TransformationType


class TransformationGroup(Group):
    def __init__(self):
        self.nx_class = "NXtransformations"


@attr.s
class Transformation:
    name = attr.ib(type=str)
    value = attr.ib()
    attributes = attr.ib(default={})

    @property
    def type(self) -> str:
        return get_attribute_value(self.attributes, CommonAttrs.TRANSFORMATION_TYPE)

    @type.setter
    def type(self, new_type):
        set_attribute_value(self.attributes, CommonAttrs.TRANSFORMATION_TYPE, new_type)

    @property
    def vector(self) -> QVector3D:
        vector = get_attribute_value(self.attributes, CommonAttrs.VECTOR)
        return (
            QVector3D(vector[0], vector[1], vector[2]) if vector is not None else None
        )

    @vector.setter
    def vector(self, new_vector: QVector3D):
        vector_as_np_array = np.array([new_vector.x(), new_vector.y(), new_vector.z()])
        set_attribute_value(self.attributes, CommonAttrs.VECTOR, vector_as_np_array)

    @property
    def ui_value(self) -> float:
        if isinstance(self.value, (float, int)):
            return float(self.value)
        return float(get_attribute_value(self.attributes, CommonAttrs.UI_VALUE))

    @ui_value.setter
    def ui_value(self, new_value: float):
        set_attribute_value(self.attributes, CommonAttrs.UI_VALUE, new_value)

    @property
    def qmatrix(self) -> QMatrix4x4:
        """
        Get a Qt3DCore.QTransform describing the transformation
        """
        transform = Qt3DCore.QTransform()
        if self.type == TransformationType.ROTATION:
            quaternion = transform.fromAxisAndAngle(self.vector, self.ui_value)
            transform.setRotation(quaternion)
        elif self.type == TransformationType.TRANSLATION:
            transform.setTranslation(self.vector.normalized() * self.ui_value)
        else:
            raise (
                RuntimeError('Unknown transformation of type "{}".'.format(self.type))
            )
        return transform.matrix()

    @property
    def units(self):
        return get_attribute_value(self.attributes, CommonAttrs.UNITS)

    @units.setter
    def units(self, new_units):
        set_attribute_value(self.attributes, CommonAttrs.UNITS, new_units)
