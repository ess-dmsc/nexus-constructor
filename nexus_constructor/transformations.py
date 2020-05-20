import logging

import numpy as np
from PySide2.QtGui import QVector3D, QMatrix4x4
from PySide2.Qt3DCore import Qt3DCore
import h5py

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.nexus import nexus_wrapper as nx
from typing import TypeVar, Union, List, Optional

from nexus_constructor.nexus.nexus_wrapper import h5Node, get_nx_class
from nexus_constructor.transformation_types import TransformationType

TransformationOrComponent = TypeVar(
    "TransformationOrComponent", "Transformation", "Component"
)


class Transformation:
    """
    Provides an interface to an existing transformation dataset in a NeXus file
    """

    def __init__(self, nexus_file: nx.NexusWrapper, dataset: h5py.Dataset):
        self.file = nexus_file
        self._dataset = dataset

    def __eq__(self, other):
        try:
            return other.absolute_path == self.absolute_path
        except Exception:
            return False

    @property
    def name(self):
        return nx.get_name_of_node(self.dataset)

    @name.setter
    def name(self, new_name: str):
        self.file.rename_node(self.dataset, new_name)
        self._update_dependent_depends_on()

    def _update_dependent_depends_on(self):
        """
        Updates all of the directly dependent "depends_on" fields for this transformation.
        """
        for dependent in self.dependents:
            dependent.depends_on = self

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
    def absolute_path(self):
        """
        Get absolute path of the transform dataset in the NeXus file,
        this is guaranteed to be unique so it can be used as an ID for this Transformation
        :return: absolute path of the transform dataset in the NeXus file,
        """
        return self.dataset.name

    @property
    def type(self):
        """
        Get transformation type, should be "Translation" or "Rotation"
        """
        return self.file.get_attribute_value(
            self.dataset, CommonAttrs.TRANSFORMATION_TYPE
        ).capitalize()

    @type.setter
    def type(self, new_type: str):
        """
        Set transformation type, should be "Translation" or "Rotation"
        """
        self.file.set_attribute_value(
            self.dataset, CommonAttrs.TRANSFORMATION_TYPE, new_type.capitalize()
        )

    @property
    def units(self):
        return self.file.get_attribute_value(self.dataset, CommonAttrs.UNITS)

    @units.setter
    def units(self, new_units):
        self.file.set_attribute_value(self.dataset, CommonAttrs.UNITS, new_units)

    @property
    def vector(self):
        """
        Returns rotation axis or translation direction as a QVector3D
        """
        vector_as_np_array = self.file.get_attribute_value(
            self.dataset, CommonAttrs.VECTOR
        )
        return QVector3D(
            vector_as_np_array[0], vector_as_np_array[1], vector_as_np_array[2]
        )

    @vector.setter
    def vector(self, new_vector: QVector3D):
        vector_as_np_array = np.array([new_vector.x(), new_vector.y(), new_vector.z()])
        self.file.set_attribute_value(
            self.dataset, CommonAttrs.VECTOR, vector_as_np_array
        )

    @property
    def dataset(self) -> h5Node:
        return self._dataset

    @dataset.setter
    def dataset(self, new_data: h5Node):
        """
        Used for setting the transformation dataset to a stream group, link or scalar/array field
        :param new_data: the new data being set
        """
        old_attrs = {}
        for k, v in self.dataset.attrs.items():
            old_attrs[k] = v
        dataset_name = self.dataset.name

        del self.file.nexus_file[dataset_name]
        if isinstance(new_data, h5py.Dataset):
            self.file.nexus_file[dataset_name] = new_data[()]
        else:
            if isinstance(new_data, h5py.SoftLink):
                self.file.nexus_file[dataset_name] = h5py.SoftLink(new_data.path)
            else:
                self.file.nexus_file.copy(
                    source=new_data, dest=dataset_name, expand_soft=True
                )
        self._dataset = self.file.nexus_file[dataset_name]
        for k, v in old_attrs.items():
            self.file.set_attribute_value(self.dataset, k, v)

        if self.file.get_attribute_value(self.dataset, CommonAttrs.UI_VALUE) is None:
            self.file.set_attribute_value(self.dataset, CommonAttrs.UI_VALUE, 0)

    @property
    def ui_value(self) -> float:
        """
        Used for getting the 3d view magnitude (as a placeholder or if the dataset is scalar)
        :return:
        """
        if isinstance(self.dataset, h5py.Dataset):
            if np.isscalar(self.dataset[()]):
                try:
                    self.ui_value = float(self.dataset[()])
                    return float(self.dataset[()])
                except ValueError:
                    logging.debug(
                        "transformation value is not cast-able to float/int, using UI placeholder value instead."
                    )
            else:
                # Dataset value is array - try to use the first value of the array as the UI value
                try:
                    self.ui_value = float(self.dataset[...][0])
                    return float(self.dataset[...][0])
                except ValueError:
                    # Not cast-able to float - either return the UI value if it's present in the group or the default
                    # value if not.
                    pass
        if self.file.get_attribute_value(self.dataset, CommonAttrs.UI_VALUE) is None:
            # Link or stream
            default_value = 0.0
            self.ui_value = default_value
            return default_value

        return self.file.get_attribute_value(self.dataset, CommonAttrs.UI_VALUE)[()]

    @ui_value.setter
    def ui_value(self, new_value: float):
        """
        Used for setting the magnitude of the transformation in the 3d view
        :param new_value: the placeholder magnitude for the 3d view
        """
        self.file.set_attribute_value(self.dataset, CommonAttrs.UI_VALUE, new_value)

    @property
    def depends_on(self) -> Optional["Transformation"]:
        depends_on_path = self.file.get_attribute_value(
            self.dataset, CommonAttrs.DEPENDS_ON
        )
        if depends_on_path not in (None, "."):
            if f"{self.dataset.parent.name}/{depends_on_path}" in self.file.nexus_file:
                # depends_on is relative
                return create_transformation(
                    self.file,
                    self.file.nexus_file[
                        f"{self.dataset.parent.name}/{depends_on_path}"
                    ],
                )
            return create_transformation(
                self.file, self.file.nexus_file[depends_on_path]
            )

    @depends_on.setter
    def depends_on(self, depends_on: "Transformation"):
        """
        Note, until Python 4.0 (or 3.7 with from __future__ import annotations) have
        to use string for depends_on type here, because the current class is not defined yet
        """
        existing_depends_on = self.file.get_attribute_value(
            self.dataset, CommonAttrs.DEPENDS_ON
        )

        if (
            existing_depends_on is not None
            and existing_depends_on in self.file.nexus_file
        ):
            create_transformation(
                self.file, self.file.nexus_file[existing_depends_on]
            ).deregister_dependent(self)

        if depends_on is None:
            self.file.set_attribute_value(self.dataset, CommonAttrs.DEPENDS_ON, ".")
        else:
            self.file.set_attribute_value(
                self.dataset, CommonAttrs.DEPENDS_ON, depends_on.absolute_path
            )
            depends_on.register_dependent(self)

    def register_dependent(self, dependent: TransformationOrComponent):
        """
        Register dependent transform or component in the dependee_of list of this transform
        Note, "dependee_of" attribute is not part of the NeXus format
        :param dependent: transform or component that depends on this one
        """

        if self.file.get_attribute_value(self.dataset, CommonAttrs.DEPENDEE_OF) is None:
            self.file.set_attribute_value(
                self.dataset, CommonAttrs.DEPENDEE_OF, dependent.absolute_path
            )
        else:
            dependee_of_list = self.file.get_attribute_value(
                self.dataset, CommonAttrs.DEPENDEE_OF
            )
            if not isinstance(dependee_of_list, np.ndarray):
                dependee_of_list = np.array([dependee_of_list])
            dependee_of_list = dependee_of_list.astype("U")
            if dependent.absolute_path not in dependee_of_list:
                dependee_of_list = np.append(
                    dependee_of_list, np.array([dependent.absolute_path])
                )
                self.file.set_attribute_value(
                    self.dataset, CommonAttrs.DEPENDEE_OF, dependee_of_list
                )

    def deregister_dependent(self, former_dependent: TransformationOrComponent):
        """
        Remove former dependent from the dependee_of list of this transform
        Note, "dependee_of" attribute is not part of the NeXus format
        :param former_dependent: transform or component that used to depend on this one
        """
        if (
            self.file.get_attribute_value(self.dataset, CommonAttrs.DEPENDEE_OF)
            is not None
        ):
            dependee_of_list = self.file.get_attribute_value(
                self.dataset, CommonAttrs.DEPENDEE_OF
            )
            if (
                not isinstance(dependee_of_list, np.ndarray)
                and dependee_of_list == former_dependent.absolute_path
            ):
                # Must be a single string rather than a list, so simply delete it
                self.file.delete_attribute(self.dataset, CommonAttrs.DEPENDEE_OF)
            elif isinstance(dependee_of_list, np.ndarray):
                dependee_of_list = dependee_of_list[
                    dependee_of_list != former_dependent.absolute_path
                ]
                self.file.set_attribute_value(
                    self.dataset, CommonAttrs.DEPENDEE_OF, dependee_of_list
                )
            else:
                logging.warning(
                    f"Unable to de-register dependent {former_dependent.absolute_path} from {self.absolute_path} due to it not being registered."
                )

    @property
    def dependents(self) -> List[Union["Component", "Transformation"]]:
        """
        Returns the direct dependents of a transform, i.e. anything that has depends_on pointing to this transformation.
        """
        return_dependents = []

        if (
            self.file.get_attribute_value(self.dataset, CommonAttrs.DEPENDEE_OF)
            is not None
        ):
            dependents = self.file.get_attribute_value(
                self.dataset, CommonAttrs.DEPENDEE_OF
            )
            if not isinstance(dependents, np.ndarray):
                dependents = [dependents]
            for path in dependents:
                node = self.file.nexus_file[path]
                if isinstance(node, h5py.Group):
                    return_dependents.append(comp.Component(self.file, node))
                elif isinstance(node, h5py.Dataset):
                    return_dependents.append(create_transformation(self.file, node))
                else:
                    raise RuntimeError("Unknown type of node.")
        return return_dependents

    def remove_from_dependee_chain(self):
        """
        Remove this transformation from the depends_on chain by pointing any dependees to this transformation's depends_on.
        If this transformation either has no depends_on or points to itself, just deregister it as a dependent.
        """
        for dependee in self.dependents:
            if self.depends_on not in [None, "."]:
                # This transformation has a depends_on, so update the dependee to point to that instead
                if isinstance(dependee, Transformation):
                    # If a dependee is a transformation, register the dependee of this transform as a dependee to this
                    # transform's depends_on
                    self.depends_on.register_dependent(dependee)
            # Update the dependee to point to this transformation's depends_on
            dependee.depends_on = self.depends_on
            # Regardless of if this transformation has a depends_on field, deregister it from any dependees.
            self.deregister_dependent(dependee)
        # Set this transformation's depends_on to None to remove it from the chain.
        self.depends_on = None


class NXLogTransformation(Transformation):
    @property
    def ui_value(self) -> float:
        if "value" not in self.dataset.keys():
            if (
                self.file.get_attribute_value(self.dataset, CommonAttrs.UI_VALUE)
                is None
            ):
                self.ui_value = 0
            return self.file.get_attribute_value(self.dataset, CommonAttrs.UI_VALUE)
        value_group = self.dataset["value"]
        if np.isscalar(value_group):
            return value_group[()]
        else:
            return float(value_group[0][()])

    @ui_value.setter
    def ui_value(self, new_value):
        self.file.set_attribute_value(self.dataset, CommonAttrs.UI_VALUE, new_value)

    @property
    def units(self) -> Optional[str]:
        return self.file.get_attribute_value(self.dataset["value"], CommonAttrs.UNITS)

    @units.setter
    def units(self, new_units: str):
        self.file.set_attribute_value(
            self.dataset["value"], CommonAttrs.UNITS, new_units
        )

    @property
    def dataset(self) -> h5Node:
        return self._dataset

    @dataset.setter
    def dataset(self, new_dataset):
        pass


def create_transformation(wrapper: nx.NexusWrapper, node: h5Node) -> Transformation:
    """
    Factory for creating different types of transform.
    If it is an NXlog group then the magnitude and units fields will be different to a normal transformation dataset.
    """
    if get_nx_class(node) == "NXlog":
        return NXLogTransformation(wrapper, node)
    return Transformation(wrapper, node)
