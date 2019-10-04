from nexus_constructor.component.component import Component
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
        return None, None
