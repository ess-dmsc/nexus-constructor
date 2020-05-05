import h5py
from typing import Tuple, Optional, Union, List
from PySide2.QtGui import QVector3D

from nexus_constructor.model.component import (
    SHAPE_GROUP_NAME,
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    OFF_GEOMETRY_NX_CLASS,
)
from nexus_constructor.model.geometry import CylindricalGeometry, NoShapeGeometry
from nexus_constructor.nexus.nexus_wrapper import get_nx_class
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.geometry import OFFGeometryNexus, OFFGeometry


def get_shape_from_component(
    component_group: h5py.Group, nexus_file: nx.NexusWrapper, shape_group_name: str
) -> Union[OFFGeometry, CylindricalGeometry, NoShapeGeometry]:
    if shape_group_name in component_group:
        shape_group = component_group[shape_group_name]
        nx_class = get_nx_class(shape_group)
        if nx_class == CYLINDRICAL_GEOMETRY_NX_CLASS:
            return CylindricalGeometry(nexus_file, shape_group)
        if nx_class == OFF_GEOMETRY_NX_CLASS:
            return OFFGeometryNexus(nexus_file, shape_group)

    # else return a placeholder to indicate the component's position
    return NoShapeGeometry()


class ComponentShape:
    def __init__(self, nexus_file: nx.NexusWrapper, component_group: h5py.Group):
        self.file = nexus_file
        self.component_group = component_group

    def get_shape(
        self,
    ) -> Tuple[
        Optional[Union[OFFGeometry, CylindricalGeometry, NoShapeGeometry]],
        Optional[List[QVector3D]],
    ]:
        """
        Get the shape of the component if there is one defined, and optionally a
        list of transformations relative to the component's depends_on chain which
        describe where the shape should be repeated
        (used in subclass for components where the shape describes each pixel)

        :return: Component shape, each transformation where the shape is repeated
        """
        shape = get_shape_from_component(
            self.component_group, self.file, SHAPE_GROUP_NAME
        )
        return shape, None

    def remove_shape(self):
        if SHAPE_GROUP_NAME in self.component_group:
            del self.component_group[SHAPE_GROUP_NAME]
