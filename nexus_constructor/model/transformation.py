from typing import TYPE_CHECKING, Any, Dict, List, Union

import attr
import numpy as np
from PySide6.Qt3DCore import Qt3DCore
from PySide6.QtGui import QMatrix4x4, QVector3D
from typing import Optional

from nexus_constructor.common_attrs import (
    CommonAttrs,
    CommonKeys,
    NodeType,
    TransformationType,
)
from nexus_constructor.component_type import LOG_CLASS_NAME
from nexus_constructor.model.group import Group
from nexus_constructor.model.helpers import get_absolute_path
from nexus_constructor.model.module import Dataset, StreamModule
from nexus_constructor.model.value_type import ValueTypes
from nexus_constructor.unit_utils import (
    DEGREES,
    METRES,
    calculate_unit_conversion_factor,
)

if TYPE_CHECKING:
    from nexus_constructor.model.component import Component  # noqa: F401
    from nexus_constructor.model.value_type import ValueType  # noqa: F401


@attr.s
class Transformation(Dataset):
    """
    In the NeXus file this would be in an NXtransformations group and would be a scalar dataset
    or an NXlog if the the transformation changes with time, for example represents a motion axis
    """

    parent_component = attr.ib(type="Component", default=None)
    _dependents = attr.ib(type=list, init=False)
    _ui_value = attr.ib(type=float, default=None)
    _ui_scale_factor = attr.ib(type=float, default=1.0, init=False)
    _ui_offset_scale_factor = attr.ib(type=float, default=1.0, init=False)

    @property
    def absolute_path(self):
        return get_absolute_path(self)

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
    def offset_vector(self) -> QVector3D:
        vector = self.attributes.get_attribute_value(CommonAttrs.OFFSET)
        return (
            QVector3D(vector[0], vector[1], vector[2])
            if vector is not None
            else QVector3D(0.0, 0.0, 0.0)
        )

    @offset_vector.setter
    def offset_vector(self, new_vector: Optional[QVector3D]):
        if new_vector:
            vector_as_np_array = np.array(
                [new_vector.x(), new_vector.y(), new_vector.z()]
            )
            self.attributes.set_attribute_value(CommonAttrs.OFFSET, vector_as_np_array)

    @property
    def ui_value(self) -> float:
        try:
            if isinstance(self.values, Dataset):
                if np.isscalar(self.values.values):
                    val: "ValueType" = self.values.values
                    self.ui_value = float(val)
                else:
                    self.ui_value = float(self.values.values[0])
        except (ValueError, TypeError):
            pass

        if self._ui_value is None:
            self.ui_value = 0.0

        return self._ui_value

    @ui_value.setter
    def ui_value(self, new_value):
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
        for use in the 3D view
        """
        transform = Qt3DCore.QTransform()
        transform.matrix()
        if self.transform_type == TransformationType.ROTATION:
            # apply offset first to translate it, and then apply rotation
            transform.setTranslation(self.offset_vector * self._ui_offset_scale_factor)
            quaternion = transform.fromAxisAndAngle(
                self.vector, self.ui_value * self._ui_scale_factor
            )

            transform.setRotation(quaternion)
        elif self.transform_type == TransformationType.TRANSLATION:
            transform.setTranslation(
                self.vector.normalized() * self.ui_value * self._ui_scale_factor
                + self.offset_vector * self._ui_offset_scale_factor
            )
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
        self._evaluate_ui_scale_factor(new_units)
        self.attributes.set_attribute_value(CommonAttrs.UNITS, new_units)

    @property
    def offset_units(self):
        return self.attributes.get_attribute_value(CommonAttrs.OFFSET_UNITS)

    @offset_units.setter
    def offset_units(self, new_units):
        self._evaluate_ui_offset_scale_factor(new_units)
        self.attributes.set_attribute_value(CommonAttrs.OFFSET_UNITS, new_units)

    def _evaluate_ui_scale_factor(self, units):
        try:
            if self.transform_type == TransformationType.TRANSLATION:
                self._ui_scale_factor = calculate_unit_conversion_factor(units, METRES)
            elif self.transform_type == TransformationType.ROTATION:
                self._ui_scale_factor = calculate_unit_conversion_factor(units, DEGREES)
        except Exception:
            pass

    def _evaluate_ui_offset_scale_factor(self, units):
        self._ui_offset_scale_factor = calculate_unit_conversion_factor(units, METRES)

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

    def deregister_dependent(self, old_dependent: Union["Transformation", "Component"]):
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

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        self._set_transformation_values()
        return_dict = self.values.as_dict(error_collector)  # type: ignore
        if NodeType.CONFIG in return_dict:
            return_dict[NodeType.CONFIG][CommonKeys.NAME] = self.name

        if self.attributes:
            if CommonKeys.ATTRIBUTES not in return_dict:
                return_dict[CommonKeys.ATTRIBUTES] = []
            return_dict[CommonKeys.ATTRIBUTES] += [
                attribute.as_dict(error_collector)
                for attribute in self.attributes
                if attribute.name != CommonAttrs.DEPENDS_ON
            ]
            try:
                return_dict[CommonKeys.ATTRIBUTES].append(
                    {
                        CommonKeys.NAME: CommonAttrs.DEPENDS_ON,
                        CommonKeys.VALUES: self.depends_on.absolute_path,
                        CommonKeys.DATA_TYPE: ValueTypes.STRING,
                    }
                )
            except AttributeError:
                pass

        return return_dict

    def as_nexus(self, nexus_node, error_collector: List[str]):
        if not isinstance(self.values, Dataset):
            return
        temp_values = np.array(self.values.values)  # type: ignore
        temp_values.astype(np.float64).dtype
        nexus_dataset = nexus_node.create_dataset(self.name, data=temp_values)
        for attribute in self.attributes:
            try:
                if attribute.name == CommonAttrs.DEPENDS_ON:
                    if self.depends_on:
                        attribute_str = self.depends_on.absolute_path
                    else:
                        attribute_str = "."
                    nexus_dataset.attrs[CommonAttrs.DEPENDS_ON] = attribute_str
                else:
                    nexus_dataset.attrs[attribute.name] = attribute.values
            except TypeError as e:
                error_collector.append(f"for attribute {attribute.name}: {str(e)}.")

    def _set_transformation_values(self):
        if isinstance(self.values, StreamModule):
            nx_log = Group(name=self.name, parent_node=self)  # type: ignore
            nx_log.nx_class = LOG_CLASS_NAME
            self.values.parent_node = nx_log
            nx_log.children.append(self.values)
            self.values = nx_log
