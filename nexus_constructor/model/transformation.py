from typing import List, Union, Dict, Any

import attr
import numpy as np
from PySide2.Qt3DCore import Qt3DCore
from PySide2.QtGui import QVector3D, QMatrix4x4

from nexus_constructor.common_attrs import (
    CommonAttrs,
    CommonKeys,
    NodeType,
    TransformationType,
)
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.value_type import ValueTypes

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nexus_constructor.model.component import Component  # noqa: F401


@attr.s
class Transformation(Dataset):
    """
    Wrapper for an individual transformation. In the NeXus file this would be translated as a transformation dataset.
    """

    parent_component = attr.ib(type="Component", default=None)
    _dependents = attr.ib(type=List[Union["Transformation", "Component"]], init=False)
    _ui_value = attr.ib(type=float, default=None)

    @_dependents.default
    def _initialise_dependents(self):
        return [] if self.parent_component is None else [self.parent_component]

    @property
    def transform_type(self) -> str:
        return self.attributes.get_attribute_value(CommonAttrs.TRANSFORMATION_TYPE)

    @transform_type.setter
    def transform_type(self, new_type):
        self.attributes.set_attribute_value(CommonAttrs.TRANSFORMATION_TYPE, new_type)

    @property
    def vector(self) -> QVector3D:
        vector = self.attributes.get_attribute_value(CommonAttrs.VECTOR)
        return (
            QVector3D(vector[0], vector[1], vector[2]) if vector is not None else None
        )

    @vector.setter
    def vector(self, new_vector: QVector3D):
        vector_as_np_array = np.array([new_vector.x(), new_vector.y(), new_vector.z()])
        self.attributes.set_attribute_value(CommonAttrs.VECTOR, vector_as_np_array)

    @property
    def ui_value(self) -> float:
        try:
            if isinstance(self.values, Dataset):
                if np.isscalar(self.values.values):
                    self.ui_value = float(self.values.values)
                    return float(self.values.values)
                else:
                    self.ui_value = float(self.values.values[0])
                    return float(self.values.values[0])
        except (ValueError, TypeError):
            pass

        if self._ui_value is None:
            default_value = 0.0
            self.ui_value = 0.0
            return default_value

        return self._ui_value

    @ui_value.setter
    def ui_value(self, new_value: float):
        if np.isscalar(new_value):
            value = new_value
        else:
            value = new_value[0]
        try:
            self._ui_value = float(value)
        except ValueError:
            self._ui_value = 0.0

    @property
    def qmatrix(self) -> QMatrix4x4:
        """
        Get a Qt3DCore.QTransform describing the transformation
        """
        transform = Qt3DCore.QTransform()
        if self.transform_type == TransformationType.ROTATION:
            quaternion = transform.fromAxisAndAngle(self.vector, self.ui_value)
            transform.setRotation(quaternion)
        elif self.transform_type == TransformationType.TRANSLATION:
            transform.setTranslation(self.vector.normalized() * self.ui_value)
        else:
            raise (
                RuntimeError(f'Unknown transformation of type "{self.transform_type}".')
            )
        return transform.matrix()

    @property
    def units(self):
        return self.attributes.get_attribute_value(CommonAttrs.UNITS)

    @units.setter
    def units(self, new_units):
        self.attributes.set_attribute_value(CommonAttrs.UNITS, new_units)

    @property
    def depends_on(self) -> "Transformation":
        return self.attributes.get_attribute_value(CommonAttrs.DEPENDS_ON)

    @depends_on.setter
    def depends_on(self, new_depends_on: "Transformation"):
        try:
            if self.depends_on is not None:
                # deregister this transform as a dependent of the old depends_on transformation
                self.depends_on.deregister_dependent(self)
        except AttributeError:
            pass
        self.attributes.set_attribute_value(CommonAttrs.DEPENDS_ON, new_depends_on)
        if new_depends_on is not None:
            new_depends_on.register_dependent(self)

    @property
    def dependents(self) -> List[Union["Transformation", "Component"]]:
        return self._dependents

    def deregister_dependent(self, old_dependent: ["Transformation", "Component"]):
        try:
            self._dependents.remove(old_dependent)
        except ValueError:
            pass

    def register_dependent(self, new_dependent: Union["Transformation", "Component"]):
        if new_dependent not in self._dependents:
            self._dependents.append(new_dependent)

    def remove_from_dependee_chain(self):
        parent = self.depends_on
        if parent is not None:
            # deregister this transformation from the parent transformation
            parent.deregister_dependent(self)

        # Copy dependents to a tuple (because self.dependents will be modified in the loop)
        current_dependents = tuple(self.dependents)
        for dependent_transform in current_dependents:
            # update dependent's depends_on to point at this transforms depends_on
            dependent_transform.depends_on = parent
            # update the parent transform to include the previously dependent transform as a dependent of the parent
            if parent is not None:
                parent.register_dependent(dependent_transform)

        self._dependents = []

    def as_dict(self) -> Dict[str, Any]:
        return_dict = {
            CommonKeys.NAME: self.name,
            CommonKeys.TYPE: NodeType.DATASET,
            CommonKeys.ATTRIBUTES: [
                attribute.as_dict()
                for attribute in self.attributes
                if attribute.name != CommonAttrs.DEPENDS_ON
            ]
            if self.attributes
            else None,
            CommonKeys.VALUES: self.values.as_dict() if self.values else [],
        }
        try:
            return_dict[CommonKeys.ATTRIBUTES].append(
                {
                    CommonKeys.NAME: CommonAttrs.DEPENDS_ON,
                    CommonKeys.VALUES: self.depends_on.absolute_path,
                    CommonKeys.TYPE: ValueTypes.STRING,
                }
            )
        except AttributeError:
            pass

        return return_dict
