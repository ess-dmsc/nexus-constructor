import attr
import numpy as np
from PySide2.QtGui import QVector3D
import h5py
from nexus_constructor.nexus import nexus_wrapper as nx
from typing import TypeVar

TransformationOrComponent = TypeVar(
    "TransformationOrComponent", "TransformationModel", "ComponentModel"
)

class TransformationsList(list):
    def __init__(self, parent):
        super().__init__()
        self.parent_component = parent
        self.has_link = False


class TransformationModel:
    """
    Provides an interface to an existing transformation dataset in a NeXus file
    """

    def __init__(self, nexus_file: nx.NexusWrapper, dataset: h5py.Dataset):
        self.file = nexus_file
        self.dataset = dataset

    @property
    def name(self):
        return nx.get_name_of_node(self.dataset)

    @name.setter
    def name(self, new_name: str):
        self.file.rename_node(self.dataset, new_name)

    @property
    def absolute_path(self):
        """
        Get absolute path of the transform dataset in the NeXus file,
        this is guarenteed to be unique so it can be used as an ID for this Transformation
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
    def depends_on(self) -> "TransformationModel":
        depends_on_path = self.file.get_attribute_value(self.dataset, "depends_on")
        if depends_on_path is not None:
            return TransformationModel(self.file, self.file.nexus_file[depends_on_path])

    @depends_on.setter
    def depends_on(self, depends_on: "TransformationModel"):
        """
        Note, until Python 4.0 (or 3.7 with from __future__ import annotations) have
        to use string for depends_on type here, because the current class is not defined yet
        """
        existing_depends_on = self.file.get_attribute_value(self.dataset, "depends_on")
        if existing_depends_on is not None:
            TransformationModel(
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
            dependee_of_list = np.append(
                dependee_of_list, np.array([dependent.absolute_path])
            )
            self.file.set_attribute_value(self.dataset, "dependee_of", dependee_of_list)

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
            else:
                dependee_of_list = dependee_of_list[
                    dependee_of_list != former_dependent.absolute_path
                ]
                self.file.set_attribute_value(
                    self.dataset, "dependee_of", dependee_of_list
                )

    def get_dependents(self):
        if "dependee_of" in self.dataset.attrs.keys():
            dependents = self.file.get_attribute_value(self.dataset, "dependee_of")
            if not isinstance(dependents, np.ndarray):
                return [dependents]
            return dependents.tolist()


@attr.s
class Transformation:
    """
    OBSOLETE: Use TransformationModel
    """

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
    """
    OBSOLETE: Use TransformationModel
    """

    axis = attr.ib(
        factory=lambda: QVector3D(0, 0, 1),
        type=QVector3D,
        validator=validate_nonzero_vector,
    )
    angle = attr.ib(default=0)
    type = "Rotation"


@attr.s
class Translation(Transformation):
    """
    OBSOLETE: Use TransformationModel
    """

    vector = attr.ib(factory=lambda: QVector3D(0, 0, 0), type=QVector3D)
    type = "Translation"
