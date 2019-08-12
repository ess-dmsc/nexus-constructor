import numpy as np

from nexus_constructor.pixel_data import PixelGrid, CountDirection, Corner, PixelMapping


def detector_faces(mapping: PixelMapping):
    """
    Returns a list of tuples. Each sublist contains a face ID followed by the face's detector ID.
    Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
    """
    return list(enumerate([id for id in mapping.pixel_ids if id is not None]))


def pixel_grid_x_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are x positions of pixel instances in the given PixelGrid
    """
    half_distance = grid.col_width / 2
    end = half_distance * (grid.columns - 1)

    offsets = np.linspace(start=-end, stop=end, num=grid.columns)
    return np.tile(offsets, (grid.rows, 1))


def pixel_grid_y_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are y positions of pixel instances in the given PixelGrid
    """
    half_distance = grid.row_height / 2
    end = half_distance * (grid.rows - 1)

    offsets = np.linspace(start=end, stop=-end, num=grid.rows)
    return np.tile(offsets, (grid.columns, 1)).transpose()


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
