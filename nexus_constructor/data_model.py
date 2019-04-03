import attr
from enum import Enum, unique
from typing import List
from numpy import array, allclose
from numpy.linalg import norm
from nexus_constructor.geometry_types import Geometry


def validate_nonzero_vector(instance, attribute, value):
    if value.x == 0 and value.y == 0 and value.z == 0:
        raise ValueError("Vector is zero length")


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
        ...
        return self.__class__ == other.__class__ and allclose(self.vector, other.vector)


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
    axis = attr.ib(
        factory=lambda: Vector(0, 0, 1), type=Vector, validator=validate_nonzero_vector
    )
    angle = attr.ib(default=0)


@attr.s
class Translation(Transformation):
    vector = attr.ib(factory=lambda: Vector(0, 0, 0), type=Vector)


@unique
class ComponentType(Enum):
    SAMPLE = "Sample"
    DETECTOR = "Detector"
    MONITOR = "Monitor"
    SOURCE = "Source"
    SLIT = "Slit"
    MODERATOR = "Moderator"
    DISK_CHOPPER = "Disk Chopper"

    @classmethod
    def values(cls):
        return [item.value for item in cls]


@attr.s
class Component:
    """Components of an instrument"""

    component_type = attr.ib(ComponentType)
    name = attr.ib(str)
    description = attr.ib(default="", type=str)
    transform_parent = attr.ib(default=None, type=object)
    dependent_transform = attr.ib(default=None, type=Transformation)
    transforms = attr.ib(factory=list, type=List[Transformation])
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
