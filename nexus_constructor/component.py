import attr
from nexus_constructor.transformations import Transformation
from nexus_constructor.pixel_data import PixelData
from nexus_constructor.geometry_types import Geometry
from typing import List


@attr.s
class Component:
    """Components of an instrument"""

    nx_class = attr.ib(str)
    name = attr.ib(str)
    description = attr.ib(default="", type=str)
    transform_parent = attr.ib(default=None, type=object)
    dependent_transform = attr.ib(default=None, type=Transformation)
    transforms = attr.ib(factory=list, type=List[Transformation])
    geometry = attr.ib(default=None, type=Geometry)
    pixel_data = attr.ib(default=None, type=PixelData)
