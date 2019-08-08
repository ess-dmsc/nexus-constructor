from nexus_constructor.pixel_data import PixelGrid, CountDirection, Corner, PixelMapping
import numpy as np


def negative(x):
    return -x


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
    if grid.columns % 2 == 0:
        distance = grid.col_width / 2
        second = [i * distance for i in range(1, (grid.columns // 2) + 1)]
        first = list(map(negative, reversed(second)))
        offsets = np.array(first + second)
        print(offsets)
    else:
        mid_point = grid.columns // 2
        end = grid.col_width * mid_point
        offsets = np.linspace(start=-end, stop=end, num=grid.columns)

    return np.tile(offsets, (grid.rows, 1))


def pixel_grid_y_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are y positions of pixel instances in the given PixelGrid
    """
    if grid.rows % 2 == 0:
        distance = grid.row_height / 2
        second = [i * distance for i in range(1, (grid.rows // 2) + 1)]
        first = list(map(negative, reversed(second)))
        offsets = np.array(first + second)
    else:
        mid_point = grid.rows // 2
        end = grid.row_height * mid_point
        offsets = np.linspace(start=-end, stop=end, num=grid.rows)

    return np.tile(np.flip(offsets), (grid.columns, 1)).transpose()


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
