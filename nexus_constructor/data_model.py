import attr
from enum import Enum, unique
from typing import List
from nexus_constructor.geometry_types import Geometry
from nexus_constructor.pixel_data import PixelData
from nexus_constructor.transformations import Transformation


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
