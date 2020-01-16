import logging

import numpy as np
from PySide2.QtGui import QVector3D, QMatrix4x4
from PySide2.Qt3DCore import Qt3DCore
import h5py
from nexus_constructor.nexus import nexus_wrapper as nx
from typing import TypeVar

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
        self.dataset = dataset

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

    @property
    def qmatrix(self) -> QMatrix4x4:
        """
        Get a Qt3DCore.QTransform describing the transformation
        """
        transform = Qt3DCore.QTransform()
        if self.type == TransformationType.ROTATION.value:
            quaternion = transform.fromAxisAndAngle(self.vector, self.value)
            transform.setRotation(quaternion)
        elif self.type == TransformationType.TRANSLATION.value:
            transform.setTranslation(self.vector.normalized() * self.value)
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
        return self.file.get_attribute_value(self.dataset, "transformation_type")

    @type.setter
    def type(self, new_type: str):
        """
        Set transformation type, should be "Translation" or "Rotation"
        """
        self.file.set_attribute_value(self.dataset, "transformation_type", new_type)

    @property
    def vector(self):
        """
        Returns rotation axis or translation direction as a QVector3D
        """
        vector_as_np_array = self.file.get_attribute_value(self.dataset, "vector")
        return QVector3D(
            vector_as_np_array[0], vector_as_np_array[1], vector_as_np_array[2]
        )

    @vector.setter
    def vector(self, new_vector: QVector3D):
        vector_as_np_array = np.array([new_vector.x(), new_vector.y(), new_vector.z()])
        self.file.set_attribute_value(self.dataset, "vector", vector_as_np_array)

    @property
    def value(self):
        """
        Get the magnitude of the transformation
        :return: distance or rotation angle
        """
        return self.dataset[...]

    @value.setter
    def value(self, new_value: float):
        """
        Set the magnitude of the transformation: distance or rotation angle
        """
        self.dataset[...] = new_value

    @property
    def depends_on(self) -> "Transformation":
        depends_on_path = self.file.get_attribute_value(self.dataset, "depends_on")
        if depends_on_path is not None:
            return Transformation(self.file, self.file.nexus_file[depends_on_path])

    @depends_on.setter
    def depends_on(self, depends_on: "Transformation"):
        """
        Note, until Python 4.0 (or 3.7 with from __future__ import annotations) have
        to use string for depends_on type here, because the current class is not defined yet
        """
        existing_depends_on = self.file.get_attribute_value(self.dataset, "depends_on")
        if existing_depends_on is not None:
            Transformation(
                self.file, self.file.nexus_file[existing_depends_on]
            ).deregister_dependent(self)

        if depends_on is None:
            self.file.set_attribute_value(self.dataset, "depends_on", ".")
        else:
            self.file.set_attribute_value(
                self.dataset, "depends_on", depends_on.absolute_path
            )
            depends_on.register_dependent(self)

    def register_dependent(self, dependent: TransformationOrComponent):
        """
        Register dependent transform or component in the dependee_of list of this transform
        Note, "dependee_of" attribute is not part of the NeXus format
        :param dependent: transform or component that depends on this one
        """

        if "dependee_of" not in self.dataset.attrs.keys():
            self.file.set_attribute_value(
                self.dataset, "dependee_of", dependent.absolute_path
            )
        else:
            dependee_of_list = self.file.get_attribute_value(
                self.dataset, "dependee_of"
            )
            if not isinstance(dependee_of_list, np.ndarray):
                dependee_of_list = np.array([dependee_of_list])
            dependee_of_list = dependee_of_list.astype("U")
            if dependent.absolute_path not in dependee_of_list:
                dependee_of_list = np.append(
                    dependee_of_list, np.array([dependent.absolute_path])
                )
                self.file.set_attribute_value(
                    self.dataset, "dependee_of", dependee_of_list
                )

    def deregister_dependent(self, former_dependent: TransformationOrComponent):
        """
        Remove former dependent from the dependee_of list of this transform
        Note, "dependee_of" attribute is not part of the NeXus format
        :param former_dependent: transform or component that used to depend on this one
        """
        if "dependee_of" in self.dataset.attrs.keys():
            dependee_of_list = self.file.get_attribute_value(
                self.dataset, "dependee_of"
            )
            if (
                not isinstance(dependee_of_list, np.ndarray)
                and dependee_of_list == former_dependent.absolute_path
            ):
                # Must be a single string rather than a list, so simply delete it
                self.file.delete_attribute(self.dataset, "dependee_of")
            elif isinstance(dependee_of_list, np.ndarray):
                dependee_of_list = dependee_of_list[
                    dependee_of_list != former_dependent.absolute_path
                ]
                self.file.set_attribute_value(
                    self.dataset, "dependee_of", dependee_of_list
                )
            else:
                logging.warning(
                    f"Unable to de-register dependent {former_dependent.absolute_path} from {self.absolute_path} due to it not being registered."
                )

    def get_dependents(self):
        import nexus_constructor.component.component as comp

        if "dependee_of" in self.dataset.attrs.keys():
            return_dependents = []
            dependents = self.file.get_attribute_value(self.dataset, "dependee_of")
            if not isinstance(dependents, np.ndarray):
                dependents = [dependents]
            for path in dependents:
                node = self.file.nexus_file[path]
                if isinstance(node, h5py.Group):
                    return_dependents.append(comp.Component(self.file, node))
                elif isinstance(node, h5py.Dataset):
                    return_dependents.append(Transformation(self.file, node))
                else:
                    raise RuntimeError("Unknown type of node.")
            return return_dependents

    def remove_from_dependee_chain(self):
        all_dependees = self.get_dependents()
        new_depends_on = self.depends_on
        if self.depends_on.absolute_path == "/":
            new_depends_on = None
        else:
            for dependee in all_dependees:
                if isinstance(dependee, Transformation):
                    new_depends_on.register_dependent(dependee)
        for dependee in all_dependees:
            dependee.depends_on = new_depends_on
            self.deregister_dependent(dependee)
        self.depends_on = None
