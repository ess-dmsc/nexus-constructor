import attr
from enum import Enum


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError('Vector is zero length')


@attr.s
class Vector:
    x = attr.ib(float)
    y = attr.ib(float)
    z = attr.ib(float)


@attr.s
class Geometry:
    pass


@attr.s
class CylindricalGeometry(Geometry):
    bottom_center = attr.ib(Vector)
    top_center = attr.ib(Vector)
    bottom_edge = attr.ib(Vector)


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
    rows = attr.ib(int)
    columns = attr.ib(int)
    row_height = attr.ib(float)
    col_width = attr.ib(float)
    first_id = attr.ib(int)
    count_direction = attr.ib(CountDirection)
    initial_count_corner = attr.ib(Corner)


@attr.s
class PixelMapping(PixelData):
    pixel_ids = attr.ib(list)  # pixel_ids[face_number] returns the pixel the face is part of, or None


@attr.s
class Component:
    name = attr.ib(str)
    id = attr.ib(int)
    translate_vector = attr.ib(default=Vector(0, 0, 0), type=Vector)
    rotate_axis = attr.ib(default=Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector)
    rotate_angle = attr.ib(default=0)
    transform_parent_id = attr.ib(default=None)
    geometry = attr.ib(default=None, type=Geometry)


@attr.s
class Sample(Component):
    pass


@attr.s
class Detector(Component):
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
