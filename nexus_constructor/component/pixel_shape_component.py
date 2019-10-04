from nexus_constructor.component.component import (
    Component,
    PIXEL_SHAPE_GROUP_NAME,
    get_shape_from_component,
)
from nexus_constructor.geometry.cylindrical_geometry import CylindricalGeometry
from nexus_constructor.geometry import OFFGeometry
from nexus_constructor.transformations import Transformation
from typing import Optional, Union, List, Tuple


class PixelShapeComponent(Component):
    def get_shape(
        self
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry]],
        Optional[List[Transformation]],
    ]:
        shape = get_shape_from_component(self.group, self.file, PIXEL_SHAPE_GROUP_NAME)
        # TODO construct a transformation for each pixel offset
        return shape, None
