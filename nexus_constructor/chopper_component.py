from nexus_constructor.component import Component
from nexus_constructor.geometry.cylindrical_geometry import CylindricalGeometry
from nexus_constructor.geometry import OFFGeometry
from nexus_constructor.geometry.disk_chopper.disk_chopper_checker import (
    NexusDefinedChopperChecker,
)
from nexus_constructor.geometry.disk_chopper.disk_chopper_geometry_creator import (
    DiskChopperGeometryCreator,
)
from nexus_constructor.transformations import Transformation
from typing import Optional, Union, List, Tuple


class ChopperComponent(Component):
    def get_shape(
        self
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry]],
        Optional[List[Transformation]],
    ]:
        # If there is a shape group then use that
        shape, _ = super().get_shape()
        if shape is not None:
            return shape, None

        # Otherwise see if we can generate shape from the details we have
        chopper_checker = NexusDefinedChopperChecker(self.group)
        if chopper_checker.validate_chopper():
            return (
                DiskChopperGeometryCreator(
                    chopper_checker.chopper_details
                ).create_disk_chopper_geometry(),
                None,
            )
        else:
            print("Validation failed. Unable to create disk chopper mesh.")
        return None, None
