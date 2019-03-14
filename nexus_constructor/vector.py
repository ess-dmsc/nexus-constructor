import attr
from math import sqrt


@attr.s
class Vector:
    """A vector in 3D space, defined by x, y and z coordinates"""

    x = attr.ib(float)
    y = attr.ib(float)
    z = attr.ib(float)

    @property
    def magnitude(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @property
    def xyz_list(self):
        return [self.x, self.y, self.z]

    @property
    def unit_list(self):
        magnitude = self.magnitude
        return [value / magnitude for value in self.xyz_list]
