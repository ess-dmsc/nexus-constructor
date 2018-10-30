import attr
from enum import Enum
from math import sqrt, sin, cos, pi, acos
from PySide2.QtGui import QVector3D, QMatrix4x4


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError('Vector is zero length')


@attr.s
class Vector:
    x = attr.ib(float)
    y = attr.ib(float)
    z = attr.ib(float)

    @property
    def magnitude(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    @property
    def xyz_list(self):
        return [self.x, self.y, self.z]

    @property
    def unit_list(self):
        magnitude = self.magnitude
        return [value / magnitude for value in self.xyz_list]


@attr.s
class Geometry:
    pass


@attr.s
class CylindricalGeometry(Geometry):
    axis_direction = attr.ib(default=Vector(1, 0, 0), type=Vector, validator=validate_nonzero_vector)
    height = attr.ib(default=1, type=float)
    radius = attr.ib(default=1, type=float)

    @property
    def base_center_point(self):
        return Vector(0, 0, 0)

    @property
    def base_edge_point(self):
        default_axis = QVector3D(0, 0, 1)
        desired_axis = QVector3D(self.axis_direction.x,
                                 self.axis_direction.y,
                                 self.axis_direction.z)
        rotate_axis = QVector3D.crossProduct(desired_axis, default_axis)
        rotate_radians = acos(QVector3D.dotProduct(desired_axis, default_axis) / self.axis_direction.magnitude)
        rotate_degrees = rotate_radians * 360 / (2 * pi)
        rotate_matrix = QMatrix4x4()
        rotate_matrix.rotate(rotate_degrees, rotate_axis)
        edge_point = QVector3D(self.radius, 0, 0) * rotate_matrix
        return Vector(edge_point.x(), edge_point.y(), edge_point.z())

    @property
    def top_center_point(self):
        values = [x * self.height for x in self.axis_direction.unit_list]
        return Vector(values[0], values[1], values[2])

    def as_off_geometry(self, steps=20):
        default_axis = QVector3D(0, 0, 1)
        desired_axis = QVector3D(self.axis_direction.x,
                                 self.axis_direction.y,
                                 self.axis_direction.z)
        rotate_axis = QVector3D.crossProduct(desired_axis, default_axis)
        rotate_radians = acos(QVector3D.dotProduct(desired_axis, default_axis) / self.axis_direction.magnitude)
        rotate_degrees = rotate_radians * 360 / (2 * pi)
        vertices = [QVector3D(sin(2 * pi * i / steps) * self.radius,
                              cos(2 * pi * i / steps) * self.radius,
                              0)
                    for i in range(steps)] + \
                   [QVector3D(sin(2 * pi * i / steps) * self.radius,
                              cos(2 * pi * i / steps) * self.radius,
                              self.height)
                    for i in range(steps)]
        rotate_matrix = QMatrix4x4()
        rotate_matrix.rotate(rotate_degrees, rotate_axis)
        vectors = []
        for vertex in vertices:
            rotated = vertex * rotate_matrix
            vectors.append(Vector(rotated.x(), rotated.y(), rotated.z()))
        return OFFGeometry(
            vertices=vectors,
            faces=[[i, steps + i, steps + ((i + 1) % steps), (i + 1) % steps]
                   for i in range(steps)] +
                  [[i for i in range(steps)],
                   [i for i in range((2 * steps) - 1, steps - 1, -1)]]
        )


@attr.s
class OFFGeometry(Geometry):
    vertices = attr.ib(factory=list)  # list of Vector objects
    faces = attr.ib(factory=list)  # List of lists. Each sublist is a polygon's points, as index numbers into vertices

    @property
    def flat_faces(self):
        return [point for face in self.faces for point in face]

    @property
    def winding_order(self):
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]


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
    description = attr.ib(default='', type=str)
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
    pixel_data = attr.ib(default=None, type=PixelData)
