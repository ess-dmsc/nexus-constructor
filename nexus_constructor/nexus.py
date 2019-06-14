from nexus_constructor.transformations import Transformation
from nexus_constructor.component import Component
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, CountDirection, Corner
from typing import List, Union


def pixel_mapping(mapping: PixelMapping):
    """
    Returns a list of two-item lists. Each sublist contains a face ID followed by the face's detector ID.
    Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
    """
    return [
        [face_id, mapping.pixel_ids[face_id]]
        for face_id in range(len(mapping.pixel_ids))
        if mapping.pixel_ids[face_id] is not None
    ]


def pixel_grid_x_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are x positions of pixel instances in the given PixelGrid
    """
    return [[x * grid.col_width for x in range(grid.columns)]] * grid.rows


def pixel_grid_y_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are y positions of pixel instances in the given PixelGrid
    """
    return [[y * grid.row_height] * grid.columns for y in range(grid.rows)]


def pixel_grid_z_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are z positions of pixel instances in the given PixelGrid
    """
    return [[0] * grid.columns] * grid.rows


def pixel_grid_detector_ids(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are detector id's of pixel instances in the given PixelGrid
    """

    ids = [[0] * grid.columns for _ in range(grid.rows)]

    for id_offset in range(grid.rows * grid.columns):
        # Determine a coordinate for the id based on the count direction from (0,0)
        if grid.count_direction == CountDirection.ROW:
            col = id_offset % grid.columns
            row = id_offset // grid.columns
        else:
            col = id_offset // grid.rows
            row = id_offset % grid.rows
        # Invert axes needed if starting in a different corner
        if grid.initial_count_corner in (Corner.TOP_LEFT, Corner.TOP_RIGHT):
            row = grid.rows - (1 + row)
        if grid.initial_count_corner in (Corner.TOP_RIGHT, Corner.BOTTOM_RIGHT):
            col = grid.columns - (1 + col)
        # Set the id at the calculated coordinate
        ids[row][col] = grid.first_id + id_offset

    return ids


def ancestral_dependent_transform(component: Component):
    """
    Returns a string of the nexus location of the transform the given component is positioned relative to.
    """
    if component.transform_parent is None or component.transform_parent == component:
        dependent_on = "."
    else:
        dependent_on = "."
        dependent_found = False
        no_dependent = False
        ancestor = component.transform_parent
        index = -1
        if component.dependent_transform is not None:
            index = component.transform_parent.transforms.index(
                component.dependent_transform
            )
        while not (dependent_found or no_dependent):
            if len(ancestor.transforms) > 0:
                dependent_on = absolute_transform_path_name(
                    ancestor.transforms[index],
                    ancestor,
                    ancestor.component_type not in external_component_types(),
                )
                dependent_found = True
            elif (
                ancestor.transform_parent is None
                or ancestor.transform_parent == ancestor
            ):
                no_dependent = True
            else:
                if ancestor.dependent_transform is None:
                    index = -1
                else:
                    index = component.transform_parent.transforms.index(
                        component.dependent_transform
                    )
                ancestor = ancestor.transform_parent
    return dependent_on


def absolute_transform_path_name(
    transform: Union[Transformation, str],
    containing_component: Union[Component, str],
    in_instrument: bool,
):
    """
    Determine the absolute path to a transform in a nexus file
    :param transform: The transform, or its name
    :param containing_component: The component that contains the transform, or its name
    :param in_instrument: Whether or not the containing component is located in /entry/instrument
    :return: The path to the transform in the nexus file
    """
    if isinstance(transform, Transformation):
        transform_name = transform.name
    else:
        transform_name = transform
    if isinstance(containing_component, Component):
        component_name = containing_component.name
    else:
        component_name = containing_component
    if in_instrument:
        parent = "/entry/instrument"
    else:
        parent = "/entry"

    return "{}/{}/transforms/{}".format(parent, component_name, transform_name)


def external_component_types():
    """Returns a set of component types that should be stored separately to /entry/instrument in a nexus file"""
    return {"Sample", "Monitor"}


def geometry_group_name(component: Component):
    """
    Returns the name the component's geometry group should have

    For NXdetector groups:
        'detector_shape' if NXoff_geometry containing 'detector_faces', or NXcylindrical_geometry containing
    'detector_number'. 'pixel_shape' otherwise
    For other groups:
        'shape'
    """
    # As of writing, Nexus constructor NXcylindrical_geometry's don't contain 'detector_number', simplifying the
    # logic here
    if component.nx_class == "Detector":
        if isinstance(component.pixel_data, PixelMapping):
            return "detector_shape"
        else:
            return "pixel_shape"
    else:
        return "shape"


def component_class_name(component_type):
    return "NX{}".format(component_type.lower())


class NexusDecoder:
    @staticmethod
    def unwound_off_faces(wound_faces, face_indices):
        """
        Returns a list of face point index lists, to be used as OFFGeometry.faces

        :param wound_faces: flattened list of face indices made from OFFGeometry.faces
        :param face_indices: indexes in wound_faces at which each face in the shape starts
        """
        slicing_indices = face_indices + [len(wound_faces)]
        return [
            wound_faces[slicing_indices[i] : slicing_indices[i + 1]]
            for i in range(len(face_indices))
        ]

    @staticmethod
    def unmap_pixel_ids(detector_id_mapping: List[List[int]], faces: int):
        """
        Returns a list of detector id's for faces in a components PixelMapping

        :param detector_id_mapping: A list of two-item lists. Each sublist contains a face ID followed by the face's
        detector ID. Corresponds to the detector_faces dataset of the NXoff_geometry class.
        :param faces: The total number of faces that should be mapped
        :return: a PixelMapping instance
        """
        pixel_ids = {}
        for mapping in detector_id_mapping:
            pixel_ids[mapping[0]] = mapping[1]
        return PixelMapping(
            pixel_ids=[
                pixel_ids[face_id] if face_id in pixel_ids else None
                for face_id in range(faces)
            ]
        )

    @staticmethod
    def build_pixel_grid(
        x_offsets: List[List[int]],
        y_offsets: List[List[int]],
        z_offsets: List[List[int]],
        detector_ids: List[List[int]],
    ):
        # Lists of 'row' sublists of 'column' length

        # Each array must be the same shape
        assert len(x_offsets) == len(y_offsets) == len(z_offsets) == len(detector_ids)
        for row in x_offsets[1:]:
            assert len(row) == len(x_offsets[0])
        for row in y_offsets:
            assert len(row) == len(x_offsets[0])
        for row in z_offsets:
            assert len(row) == len(x_offsets[0])
        for row in detector_ids:
            assert len(row) == len(x_offsets[0])

        rows = len(x_offsets)
        columns = len(x_offsets[0])

        if rows > 1:
            row_height = y_offsets[1][0] - y_offsets[0][0]
        else:
            row_height = 1

        if columns > 1:
            column_width = x_offsets[0][1] - x_offsets[0][0]
        else:
            column_width = 1

        corner_ids = {
            detector_ids[0][0]: Corner.BOTTOM_LEFT,
            detector_ids[0][columns - 1]: Corner.BOTTOM_RIGHT,
            detector_ids[rows - 1][0]: Corner.TOP_LEFT,
            detector_ids[rows - 1][columns - 1]: Corner.TOP_RIGHT,
        }
        first_id = min(corner_ids.keys())
        initial_count_corner = corner_ids[first_id]

        if rows > 1 and columns > 1:
            column_neighbour_ids = {
                Corner.BOTTOM_LEFT: detector_ids[1][0],
                Corner.BOTTOM_RIGHT: detector_ids[1][columns - 1],
                Corner.TOP_LEFT: detector_ids[rows - 2][0],
                Corner.TOP_RIGHT: detector_ids[rows - 2][columns - 1],
            }
            column_neighbour_id = column_neighbour_ids[initial_count_corner]
            if column_neighbour_id == first_id + 1:
                count_direction = CountDirection.COLUMN
            else:
                count_direction = CountDirection.ROW
        else:
            count_direction = CountDirection.ROW

        return PixelGrid(
            rows=rows,
            columns=columns,
            row_height=row_height,
            col_width=column_width,
            first_id=first_id,
            count_direction=count_direction,
            initial_count_corner=initial_count_corner,
        )

    @staticmethod
    def extract_dependency_names(dependency_path: str):
        """Takes the path to a nexus transform, and returns the name of the component and transform from it"""
        if dependency_path == ".":
            return None, None

        parts = dependency_path.split("/")
        return parts[-3], parts[-1]
