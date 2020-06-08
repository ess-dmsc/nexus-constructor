from typing import List, Tuple, Union

import numpy as np

from nexus_constructor.pixel_data import PixelGrid, CountDirection, Corner, PixelMapping

PIXEL_FIELDS = [
    "x_pixel_offset",
    "y_pixel_offset",
    "z_pixel_offset",
    "detector_number",
    "detector_faces",
]


def get_detector_faces_from_pixel_mapping(
    mapping: PixelMapping,
) -> List[Tuple[int, int]]:
    """
    Returns a list of tuples. Each tuple contains a face ID followed by the face's detector ID.
    Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
    """
    detector_faces = [
        (id[0], id[1]) for id in enumerate(mapping.pixel_ids) if id[1] is not None
    ]
    return detector_faces


def get_detector_number_from_pixel_mapping(mapping: PixelMapping,) -> List[int]:
    """
    Returns a list of pixel IDs. Used for writing information to the detector_number field in NXdetector and
    NXcylindrical_geometry.
    """
    detector_numbers = [id for id in mapping.pixel_ids if id is not None]
    return detector_numbers


def get_x_offsets_from_pixel_grid(grid: PixelGrid) -> Union[np.ndarray, float]:
    """
    Returns an array of x-offsets. Each value in the array is the x position of a pixel instance defined in the
    PixelGrid.
    """
    half_distance = grid.col_width / 2
    end = half_distance * (grid.columns - 1)

    offsets = np.linspace(start=-end, stop=end, num=grid.columns)
    return np.tile(offsets, (grid.rows, 1))


def get_y_offsets_from_pixel_grid(grid: PixelGrid) -> Union[np.ndarray, float]:
    """
    Returns an array of y-offsets. Each value in the array is the y position of a pixel instance defined in the
    PixelGrid.
    """
    half_distance = grid.row_height / 2
    end = half_distance * (grid.rows - 1)

    offsets = np.linspace(start=end, stop=-end, num=grid.rows)
    return np.tile(offsets, (grid.columns, 1)).transpose()


def get_z_offsets_from_pixel_grid(grid: PixelGrid) -> Union[np.ndarray, float]:
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are z positions of pixel instances in the given PixelGrid.
    """
    return np.zeros((grid.rows, grid.columns))


def get_detector_ids_from_pixel_grid(grid: PixelGrid) -> Union[np.ndarray, int]:
    """
    Returns an array of detector IDs. Starts with a 1D array of numbers and reorders them depending on the count
    direction and initial count corner supplied by the user.
    """
    ids = np.arange(grid.rows * grid.columns) + grid.first_id

    if grid.count_direction == CountDirection.COLUMN:
        # Reshape the array with column-major/Fortran-like index order. This means that first index is changing fastest,
        # and the last index changing slowest.
        ids = ids.reshape((grid.rows, grid.columns), order="F")
    else:
        # Reshape the array. Without an order argument this will be column-major order by default.
        ids = ids.reshape(grid.rows, grid.columns)

    if grid.initial_count_corner == Corner.TOP_RIGHT:
        # Invert the columns in the case of a top-right starting corner.
        ids = np.fliplr(ids)

    if grid.initial_count_corner == Corner.BOTTOM_LEFT:
        # Invert the rows in the case of a bottom-left starting corner.
        ids = np.flipud(ids)

    # Rotate the array 180 degrees clockwise in the case of a bottom-right starting corner.
    if grid.initial_count_corner == Corner.BOTTOM_RIGHT:
        ids = np.rot90(ids, 2)

    return ids
