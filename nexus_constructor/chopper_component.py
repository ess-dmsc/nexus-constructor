from nexus_constructor.component import Component
from nexus_constructor.geometry.cylindrical_geometry import CylindricalGeometry
from nexus_constructor.geometry import OFFGeometry
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    NexusDefinedChopperChecker,
)
from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    DiskChopperGeometryCreator,
)
from typing import Optional, Union


class ChopperComponent(Component):
    def get_shape(self) -> Optional[Union[OFFGeometry, CylindricalGeometry]]:
        # If there is a shape group then use that
        shape = super().get_shape()
        if shape is not None:
            return shape

        # Otherwise see if we can generate shape from the details we have
        chopper_checker = NexusDefinedChopperChecker(self.group)
        if chopper_checker.validate_chopper():
            return DiskChopperGeometryCreator(
                chopper_checker.get_chopper_details()
            ).create_disk_chopper_geometry()
        else:
            print("Validation failed. Unable to create disk chopper mesh.")
