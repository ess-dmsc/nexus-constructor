import attr
import numpy as np
from PySide2.QtGui import QVector3D
import h5py
from nexus_constructor.nexus import nexus_wrapper as nx


class TransformationsList(list):
    def __init__(self, parent):
        super().__init__()
        self.parent_component = parent


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
    def depends_on(self) -> 'TransformationModel':
        depends_on_path = self.file.get_attribute_value(self.dataset, "depends_on")
        if depends_on_path is not None:
            return TransformationModel(self.file, self.file[depends_on_path])

    @depends_on.setter
    def depends_on(self, depends_on: 'TransformationModel'):
        """
        Note, until Python 4.0 (or 3.7 with from __future__ import annotations) have
        to use string for depends_on type here, because the current class is not defined yet
        """
        if depends_on is None:
            self.file.set_attribute_value(self.dataset, "depends_on", ".")
        else:
            self.file.set_attribute_value(self.dataset, "depends_on", depends_on.dataset.name)


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
