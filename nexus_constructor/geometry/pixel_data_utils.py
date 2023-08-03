from typing import List, Tuple, Union

import numpy as np

from nexus_constructor.geometry.pixel_data import (
    Corner,
    CountDirection,
    PixelGrid,
    PixelMapping,
)
from nexus_constructor.model.geometry import (
    DETECTOR_FACES,
    DETECTOR_NUMBER,
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    Z_PIXEL_OFFSET,
)

PIXEL_FIELDS = [
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    Z_PIXEL_OFFSET,
    DETECTOR_NUMBER,
    DETECTOR_FACES,
]


def get_detector_faces_from_pixel_mapping(
    mapping: PixelMapping,
) -> List[Tuple[int, int]]:
    """
    Returns a list of tuples. Each tuple contains a face ID followed by the face's detector ID.
    Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
    """
    detector_faces: List[Tuple[int, int]] = []
    idx: Tuple[int, int]
    for idx in enumerate(mapping.pixel_ids):
        if idx[1] is not None:
            detector_faces.append((idx[0], idx[1]))

    return detector_faces


def get_detector_number_from_pixel_mapping(
    mapping: PixelMapping,
) -> List[int]:
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
    if grid.gap_every_columns > 0:
        total_width = (
            grid.columns * grid.col_width
            + ((grid.columns - 1) // grid.gap_every_columns) * grid.column_gap_width
        )
    else:
        total_width = grid.columns * grid.col_width

    start = -total_width / 2 + grid.col_width / 2
    offsets = np.zeros(grid.columns)
    gap_counter = 0
    for i in range(grid.columns):
        offsets[i] = start + i * grid.col_width + gap_counter * grid.column_gap_width
        # If there is a gap, increment the gap counter
        if grid.gap_every_columns > 0 and (i + 1) % grid.gap_every_columns == 0:
            gap_counter += 1
    return np.tile(offsets, (grid.rows, 1))


def get_y_offsets_from_pixel_grid(grid: PixelGrid) -> Union[np.ndarray, float]:
    """
    Returns an array of y-offsets. Each value in the array is the y position of a pixel instance defined in the
    PixelGrid.
    """
    if grid.gap_every_rows > 0:
        total_height = (
            grid.rows * grid.row_height
            + ((grid.rows - 1) // grid.gap_every_rows) * grid.row_gap_height
        )
    else:
        total_height = grid.rows * grid.row_height

    start = total_height / 2 - grid.row_height / 2
    offsets = np.zeros(grid.rows)
    gap_counter = 0
    for i in range(grid.rows):
        offsets[i] = start - i * grid.row_height - gap_counter * grid.row_gap_height
        # If there is a gap, increment the gap counter
        if grid.gap_every_rows > 0 and (i + 1) % grid.gap_every_rows == 0:
            gap_counter += 1
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
