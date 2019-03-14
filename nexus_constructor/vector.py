import attr
from numpy import array, allclose
from numpy.linalg import norm


class Vector:
    """A vector in 3D space, defined by x, y and z coordinates"""

    def __init__(self, x, y, z):
        """
        :param x: The x coordinate.
        :param y: The y coordinate.
        :param z: The z coordinate.
        """
        self.vector = array([x, y, z], dtype=float)

    @property
    def x(self):
        return self.vector[0].item()

    @x.setter
    def x(self, value):
        self.vector[0] = value

    @property
    def y(self):
        return self.vector[1].item()

    @y.setter
    def y(self, value):
        self.vector[1] = value

    @property
    def z(self):
        return self.vector[2].item()

    @z.setter
    def z(self, value):
        self.vector[2] = value

    @property
    def magnitude(self):
        return norm(self.vector)

    @property
    def unit_list(self):
        return self.vector / self.magnitude

    def __eq__(self, other):
        return self.__class__ == other.__class__ and allclose(self.vector, other.vector)
