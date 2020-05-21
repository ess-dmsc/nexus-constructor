# from nexus_constructor.model.component import PIXEL_SHAPE_GROUP_NAME, get_shape_from_component
#
# from nexus_constructor.model.geometry import (
#     NoShapeGeometry,
#     OFFGeometry,
#     CylindricalGeometry,
# )
# from typing import Optional, Union, List, Tuple
# from PySide2.QtGui import QVector3D
# import numpy as np
#
#
# def _create_transformation_vectors_for_pixel_offsets(
#     detector_group, wrapper
# ) -> List[QVector3D]:
#     """
#     Construct a transformation (as a QVector3D) for each pixel offset
#     """
#     x_offsets = wrapper.get_field_value(detector_group, "x_pixel_offset")
#     y_offsets = wrapper.get_field_value(detector_group, "y_pixel_offset")
#     z_offsets = wrapper.get_field_value(detector_group, "z_pixel_offset")
#     if x_offsets is None or y_offsets is None:
#         raise Exception(
#             "In pixel_shape_component expected to find x_pixel_offset and y_pixel_offset datasets"
#         )
#     if z_offsets is None:
#         z_offsets = np.zeros_like(x_offsets)
#     # offsets datasets can be 2D to match dimensionality of detector, so flatten to 1D
#     return [
#         QVector3D(x, y, z)
#         for x, y, z in zip(
#             x_offsets.flatten(), y_offsets.flatten(), z_offsets.flatten()
#         )
#     ]
#
#
# class PixelShape(ComponentShape):
#     def get_shape(
#         self,
#     ) -> Tuple[
#         Optional[Union[OFFGeometry, CylindricalGeometry, NoShapeGeometry]],
#         Optional[List[QVector3D]],
#     ]:
#         shape = get_shape_from_component(
#             self.component_group, self.file, PIXEL_SHAPE_GROUP_NAME
#         )
#         return (
#             shape,
#             _create_transformation_vectors_for_pixel_offsets(
#                 self.component_group, self.file
#             ),
#         )
#
#     def remove_shape(self):
#         if PIXEL_SHAPE_GROUP_NAME in self.component_group:
#             del self.component_group[PIXEL_SHAPE_GROUP_NAME]
