import h5py
from nexus_constructor.vector import Vector


class Transformation:
    """
    Parent class for transformations on the model.
    """

    def __init__(self, name):
        """
        Creates an in-memory nexus file with a named entry containing an NXTransformation attribute.
        :param name: The name of the root entry in the nexus file.
        """
        self.nexus_file = h5py.File(name, driver='core', backing_store=False)
        self.transformation = self.nexus_file.create_group(name)
        self.transformation.attrs['NX_class'] = 'NXtransformation'

    @property
    def name(self):
        return self.transformation.name[1:]


class Rotation(Transformation):

    def __init__(self, angle: int, name='rotation', axis=Vector(0, 0, 1)):
        """
        Creates a rotation in the in-memory Nexus file under
        :param angle: The angle to rotate the object by.
        :param name: The root entry name for the nexus file.
        :param axis: The point to rotate the object.
        """
        super().__init__(name)
        self.transformation.attrs['transformation_type'] = 'rotation'
        self._angle = angle
        self._axis = axis

    @property
    def angle(self):
        return self._angle

    @property
    def axis(self):
        return self._axis

    # axis = attr.ib(factory=lambda: Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector)
    # angle = attr.ib(default=0)


class Translation(Transformation):

    def __init__(self, name='translation', vector=Vector(0, 0, 0)):
        """
        Creates a translation in the in-memory Nexus file
        :param name: The root entry name for the nexus file.
        :param vector: The vector for the translation.
        """
        super().__init__(name)
        self.transformation.attrs['transformation_type'] = 'translation'
        self._vector = vector
        self.transformation.attrs['vector'] = vector.xyz_list

    @property
    def vector(self):
        return self._vector

    # vector = attr.ib(factory=lambda: Vector(0, 0, 0), type=Vector)