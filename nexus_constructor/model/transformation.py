from typing import List, Union

import attr
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QVector3D, QMatrix4x4
import numpy as np

from nexus_constructor.model.group import Group
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.transformation_types import TransformationType


@attr.s
class TransformationGroup(Group):
    """
    Group containing transformations.
    """

    name = attr.ib(type=str, default="transformations", init=True)
    nx_class = "NXtransformations"


@attr.s
class Transformation(Dataset):
    """
    Wrapper for an individual transformation. In the NeXus file this would be translated as a transformation dataset.
    """

    _dependents = attr.ib(factory=list, type=List["Transformation"])

    @property
    def type(self) -> str:
        return self.get_attribute_value(CommonAttrs.TRANSFORMATION_TYPE)

    @type.setter
    def type(self, new_type):
        self.set_attribute_value(CommonAttrs.TRANSFORMATION_TYPE, new_type)

    @property
    def vector(self) -> QVector3D:
        vector = self.get_attribute_value(CommonAttrs.VECTOR)
        return (
            QVector3D(vector[0], vector[1], vector[2]) if vector is not None else None
        )

    @vector.setter
    def vector(self, new_vector: QVector3D):
        vector_as_np_array = np.array([new_vector.x(), new_vector.y(), new_vector.z()])
        self.set_attribute_value(CommonAttrs.VECTOR, vector_as_np_array)

    @property
    def ui_value(self) -> float:

        if isinstance(self.values, (float, int)):
            return float(self.values)

        if not self.values:
            default_value = 0.0
            self.ui_value = default_value
            return default_value

        ui_value = self.get_attribute_value(CommonAttrs.UI_VALUE)

        if isinstance(ui_value, (np.ndarray, list)):
            try:
                return float(ui_value[0])
            except ValueError:
                pass

        return float(ui_value)

    @ui_value.setter
    def ui_value(self, new_value: float):
        self.set_attribute_value(CommonAttrs.UI_VALUE, new_value)

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
            raise (RuntimeError(f'Unknown transformation of type "{self.type}".'))
        return transform.matrix()

    @property
    def units(self):
        return self.get_attribute_value(CommonAttrs.UNITS)

    @units.setter
    def units(self, new_units):
        self.set_attribute_value(CommonAttrs.UNITS, new_units)

    @property
    def depends_on(self) -> "Transformation":
        return self.get_attribute_value(CommonAttrs.DEPENDS_ON)

    @depends_on.setter
    def depends_on(self, new_depends_on: "Transformation"):
        self.set_attribute_value(CommonAttrs.DEPENDS_ON, new_depends_on)

    @property
    def dependents(self) -> List["Transformation"]:
        return self._dependents

    def deregister_dependent(self, old_dependent: "Transformation"):
        try:
            self._dependents.remove(old_dependent)
        except ValueError:
            pass

    def register_dependent(self, new_dependent: Union["Transformation", "Component"]):
        if new_dependent not in self._dependents:
            self._dependents.append(new_dependent)


def create_transformation(name: str, dataset: Dataset):
    return Transformation(name, dataset)
