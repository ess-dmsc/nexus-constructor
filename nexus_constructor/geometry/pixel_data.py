from abc import ABC
from enum import Enum

import attr


class CountDirection(Enum):
    ROW = 1
    COLUMN = 2


class Corner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class PixelData(ABC):
    """Base class for a detector's pixel description"""

    type = "PixelData"


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

    pixel_ids = attr.ib(default=[], type=list)
