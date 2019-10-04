from nexus_constructor.component.component import (
    Component,
    PIXEL_SHAPE_GROUP_NAME,
    CYLINDRICAL_GEOMETRY_NEXUS_NAME,
    OFF_GEOMETRY_NEXUS_NAME,
)
from nexus_constructor.geometry.cylindrical_geometry import CylindricalGeometry
from nexus_constructor.geometry import OFFGeometry, OFFGeometryNexus
from nexus_constructor.transformations import Transformation
from nexus_constructor.nexus.nexus_wrapper import get_nx_class
from typing import Optional, Union, List, Tuple


class PixelShapeComponent(Component):
    def get_shape(
        self
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry]],
        Optional[List[Transformation]],
    ]:
        if PIXEL_SHAPE_GROUP_NAME in self.group:
            shape_group = self.group[PIXEL_SHAPE_GROUP_NAME]
            nx_class = get_nx_class(shape_group)
            if nx_class == CYLINDRICAL_GEOMETRY_NEXUS_NAME:
                return CylindricalGeometry(self.file, shape_group), None
            if nx_class == OFF_GEOMETRY_NEXUS_NAME:
                return OFFGeometryNexus(self.file, shape_group), None
        return None, None
