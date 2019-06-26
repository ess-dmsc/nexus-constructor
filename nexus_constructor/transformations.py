import attr
import numpy as np
from PySide2.QtGui import QVector3D
from typing import Any
import h5py
from nexus_constructor.nexus import nexus_wrapper as nx


def create_transform(type: str, vector: np.array, value: Any):
    if type == "Rotation":
        return Rotation(type, QVector3D(vector[0], vector[1], vector[2]), value)
    if type == "Translation":
        return Translation(type, value * vector)
    raise ValueError("Unexpected transformation type encountered in create_transform()")


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


@attr.s
class Transformation:
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
    axis = attr.ib(
        factory=lambda: QVector3D(0, 0, 1),
        type=QVector3D,
        validator=validate_nonzero_vector,
    )
    angle = attr.ib(default=0)
    type = "Rotation"


@attr.s
class Translation(Transformation):
    vector = attr.ib(factory=lambda: QVector3D(0, 0, 0), type=QVector3D)
    type = "Translation"
