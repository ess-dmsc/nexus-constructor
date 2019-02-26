import attr
from enum import Enum, unique
from math import sqrt, sin, cos, pi, acos
from typing import List
from PySide2.QtGui import QVector3D, QMatrix4x4


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError('Vector is zero length')


def validate_list_contains_transformations(instance, attribute, value):
    for item in value:
        assert isinstance(item, Transformation)


@attr.s
class Vector:
    """A vector in 3D space, defined by x, y and z coordinates"""
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
    """Base class for geometry a detector component can take"""
    pass


@attr.s
class CylindricalGeometry(Geometry):
    """
    Describes the shape of a cylinder in 3D space

    The cylinder is assumed to have the center of its base located at the origin of the local coordinate system, and is
    described by the direction of its axis, its height, and radius.
    """
    axis_direction = attr.ib(factory=lambda: Vector(1, 0, 0), type=Vector, validator=validate_nonzero_vector)
    height = attr.ib(default=1, type=float)
    radius = attr.ib(default=1, type=float)

    @property
    def base_center_point(self):
        return Vector(0, 0, 0)

    @property
    def base_edge_point(self):
        # rotate a point on the edge of a Z axis aligned cylinder by the rotation matrix
        edge_point = QVector3D(self.radius, 0, 0) * self.rotation_matrix
        return Vector(edge_point.x(), edge_point.y(), edge_point.z())

    @property
    def top_center_point(self):
        values = [x * self.height for x in self.axis_direction.unit_list]
        return Vector(values[0], values[1], values[2])

    def as_off_geometry(self, steps=20):
        # steps number of points around the base, and steps number around the top, aligned with the Z axis
        vertices = [QVector3D(sin(2 * pi * i / steps) * self.radius,
                              cos(2 * pi * i / steps) * self.radius,
                              0)
                    for i in range(steps)] + \
                   [QVector3D(sin(2 * pi * i / steps) * self.radius,
                              cos(2 * pi * i / steps) * self.radius,
                              self.height)
                    for i in range(steps)]
        # rotate each vertex to produce the desired cylinder mesh
        vectors = []
        rotate_matrix = self.rotation_matrix
        for vertex in vertices:
            rotated = vertex * rotate_matrix
            vectors.append(Vector(rotated.x(), rotated.y(), rotated.z()))
        # faces are rectangles joining the top and bottom, followed by a steps-sided shapes for the base and top
        # the final face uses steps of -1 to have the same winding order as the other faces
        return OFFGeometry(
            vertices=vectors,
            faces=[[i, steps + i, steps + ((i + 1) % steps), (i + 1) % steps]
                   for i in range(steps)] +
                  [[i for i in range(steps)],
                   [i for i in range((2 * steps) - 1, steps - 1, -1)]]
        )

    @property
    def rotation_matrix(self):
        """
        :return: A QMatrix4x4 describing the rotation from the Z axis to the cylinder's axis
        """
        default_axis = QVector3D(0, 0, 1)
        unit_axis = self.axis_direction.unit_list
        desired_axis = QVector3D(unit_axis[0],
                                 unit_axis[1],
                                 unit_axis[2])
        rotate_axis = QVector3D.crossProduct(desired_axis, default_axis)
        rotate_radians = acos(QVector3D.dotProduct(desired_axis, default_axis))
        rotate_degrees = rotate_radians * 360 / (2 * pi)
        rotate_matrix = QMatrix4x4()
        rotate_matrix.rotate(rotate_degrees, rotate_axis)
        return rotate_matrix


@attr.s
class OFFGeometry(Geometry):
    """
    Stores arbitrary 3D geometry as a list of vertices and faces, based on the Object File Format

    vertices:   list of Vector objects used as corners of polygons in the geometry
    faces:  list of integer lists. Each sublist is a winding path around the corners of a polygon. Each sublist item is
            an index into the vertices list to identify a specific point in 3D space
    """
    vertices = attr.ib(factory=list, type=List[Vector])
    faces = attr.ib(factory=list, type=List[List[int]])

    @property
    def winding_order(self):
        return [point for face in self.faces for point in face]

    @property
    def winding_order_indices(self):
        face_sizes = [len(face) for face in self.faces]
        return [sum(face_sizes[0:i]) for i in range(len(face_sizes))]


@attr.s
class NoShapeGeometry(Geometry):
    """
    Dummy object for components with no geometry - sphere
    """
    # radius = attr.ib(default=1, type=float)

    @property
    def base_center_point(self):
        return Vector(0, 0, 0)


@attr.s
class PixelData:
    """Base class for a detector's pixel description"""
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
    """
    Represents a grid of pixels arranged at regular intervals on a 2D plane

    Rows and columns increase along the X and Y axis positive directions, with the origin in the bottom left corner,
    the X axis increasing to the left, and the Y axis increasing upwards.

    The center of the detector is located at the origin of the pixel grid.

    ^ y
    |
    |    x
    +---->

    Detector numbers will be assigned from a starting value in the attribute 'first_id'
    This count will increase by 1 for each instance of the pixel in the grid.
    The corner that counting starts in, and whether counting should first happen along rows or columns can be set with
    the 'count_direction' and 'initial_count_corner' attributes, which respectively take 'CountDirection' and 'Corner'
    Enum values.
    """
    rows = attr.ib(default=1, type=int)
    columns = attr.ib(default=1, type=int)
    row_height = attr.ib(default=1, type=float)
    col_width = attr.ib(default=1, type=float)
    first_id = attr.ib(default=0, type=int)
    count_direction = attr.ib(default=CountDirection.ROW, type=CountDirection)
    initial_count_corner = attr.ib(default=Corner.BOTTOM_LEFT, type=Corner)


@attr.s
class PixelMapping(PixelData):
    """
    Maps faces in a 3D geometry to the detector id's

    To be used in conjunction with an OFFGeometry instance. This classes pixel_ids attribute should be the same length
    as the geometry's faces list. The value of this list at any given index should be the detector id number that the
    face is part of, or None if it isn't part of any detecting face or volume.

    Used to populate the detector_faces dataset of the NXoff_geometry class.
    See http://download.nexusformat.org/sphinx/classes/base_classes/NXoff_geometry.html
    """
    pixel_ids = attr.ib(list)


@attr.s
class SinglePixelId(PixelData):
    """Pixel data for components that only have a single detector ID"""
    pixel_id = attr.ib(int)


@attr.s
class Transformation:
    name = attr.ib(str)


@attr.s
class Rotation(Transformation):
    axis = attr.ib(factory=lambda: Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector)
    angle = attr.ib(default=0)


@attr.s
class Translation(Transformation):
    vector = attr.ib(factory=lambda: Vector(0, 0, 0), type=Vector)


@unique
class ComponentType(Enum):
    SAMPLE = 'Sample'
    DETECTOR = 'Detector'
    MONITOR = 'Monitor'
    SOURCE = 'Source'
    SLIT = 'Slit'
    MODERATOR = 'Moderator'
    DISK_CHOPPER = 'Disk Chopper'

    @classmethod
    def values(cls):
        return [item.value for item in cls]


@attr.s
class Component:
    """Components of an instrument"""
    component_type = attr.ib(ComponentType)
    name = attr.ib(str)
    description = attr.ib(default='', type=str)
    transform_parent = attr.ib(default=None, type=object)
    dependent_transform = attr.ib(default=None, type=Transformation)
    transforms = attr.ib(factory=list, type=List[Transformation], validator=validate_list_contains_transformations)
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
