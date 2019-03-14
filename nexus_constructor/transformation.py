import h5py
from nexus_constructor.vector import Vector
from uuid import uuid4


class Transformation:
    """
    Parent class for transformations on the model.
    """

    def __init__(self, name):
        """
        Creates an in-memory nexus file with a named entry containing an NXTransformation attribute.
        :param name: The name of the root entry in the nexus file.
        """
        file_name = str(uuid4())
        self.nexus_file = h5py.File(file_name, driver="core", backing_store=False)
        self.transformation = self.nexus_file.create_group(name)
        self.transformation.attrs["NX_class"] = "NXtransformations"

    @property
    def name(self):
        return self.transformation.name[1:]


class Rotation(Transformation):
    def __init__(self, angle=0.0, name="rotation", axis=Vector(0, 0, 1)):
        """
        Creates a rotation in the in-memory Nexus file under
        :param angle: The angle to rotate the object by.
        :param name: The root entry name for the nexus file.
        :param axis: The point to rotate the object.
        """
        super().__init__(name)
        self.transformation.attrs["transformation_type"] = "rotation"
        self.transformation.attrs["angle"] = angle
        self.transformation.attrs["axis"] = axis.vector.tolist()
        self._axis = axis

    @property
    def angle(self):
        return self.transformation.attrs["angle"]

    @angle.setter
    def angle(self, angle):
        self.transformation.attrs["angle"] = angle

    @property
    def axis(self):
        return self._axis


class Translation(Transformation):
    def __init__(self, name="translation", vector=Vector(0, 0, 0)):
        """
        Creates a translation in the in-memory Nexus file
        :param name: The root entry name for the nexus file.
        :param vector: The vector for the translation.
        """
        super().__init__(name)
        self.transformation.attrs["transformation_type"] = "translation"
        self.transformation.attrs["vector"] = vector.vector.tolist()
        self._vector = vector

    @property
    def vector(self):
        return self._vector
