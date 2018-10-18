import attr
from enum import Enum
from math import sqrt


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError('Vector is zero length')


@attr.s
class Vector:
    x = attr.ib(float)
    y = attr.ib(float)
    z = attr.ib(float)

    def magnitude(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit_list(self):
        magnitude = self.magnitude()
        return [self.x / magnitude, self.y / magnitude, self.z / magnitude]


@attr.s
class Geometry:
    pass


@attr.s
class CylindricalGeometry(Geometry):
    axis_direction = attr.ib(default=Vector(1, 0, 0), type=Vector)
    height = attr.ib(default=1, type=float)
    radius = attr.ib(default=1, type=float)


@attr.s
class OFFGeometry(Geometry):
    vertices = attr.ib(factory=list)
    faces = attr.ib(factory=list)
    winding_order = attr.ib(factory=list)


@attr.s
class PixelData:
    pass


class CountDirection(Enum):
    ROW = 1
    COLUMN = 2


class Corner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


@attr.s
class PixelGrid(PixelData):
    rows = attr.ib(default=1, type=int)
    columns = attr.ib(default=1, type=int)
    row_height = attr.ib(default=1, type=float)
    col_width = attr.ib(default=1, type=float)
    first_id = attr.ib(default=0, type=int)
    count_direction = attr.ib(default=CountDirection.ROW, type=CountDirection)
    initial_count_corner = attr.ib(default=Corner.BOTTOM_LEFT, type=Corner)


@attr.s
class PixelMapping(PixelData):
    pixel_ids = attr.ib(list)  # pixel_ids[face_number] returns the pixel the face is part of, or None


@attr.s
class Component:
    name = attr.ib(str)
    description = attr.ib(str)
    transform_parent = attr.ib(default=None, type=object)
    translate_vector = attr.ib(default=Vector(0, 0, 0), type=Vector)
    rotate_axis = attr.ib(default=Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector)
    rotate_angle = attr.ib(default=0)
    geometry = attr.ib(default=None, type=Geometry)


@attr.s
class Sample(Component):
    pass


@attr.s
class Detector(Component):
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
