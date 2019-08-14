import numpy as np

from nexus_constructor.pixel_data import PixelGrid, CountDirection, Corner, PixelMapping


def detector_faces(mapping: PixelMapping):
    """
    Returns a list of tuples. Each tuple contains a face ID followed by the face's detector ID.
    Corresponds to the detector_faces dataset structure of the NXoff_geometry class.
    """
    return list(enumerate([id for id in mapping.pixel_ids if id is not None]))


def detector_number(mapping: PixelMapping):
    """
    Returns a list of pixel IDs. Used for writing information to the detector_number field in NXdetector and
    NXcylindrical_geometry.
    """
    return [id for id in mapping.pixel_ids if id is not None]


def pixel_grid_x_offsets(grid: PixelGrid):
    """
    Returns an array of x-offsets. Each value in the array is the x position of a pixel instance defined in the
    PixelGrid.
    """
    half_distance = grid.col_width / 2
    end = half_distance * (grid.columns - 1)

    offsets = np.linspace(start=-end, stop=end, num=grid.columns)
    return np.tile(offsets, (grid.rows, 1))


def pixel_grid_y_offsets(grid: PixelGrid):
    """
    Returns an array of y-offsets. Each value in the array is the y position of a pixel instance defined in the
    PixelGrid.
    """
    half_distance = grid.row_height / 2
    end = half_distance * (grid.rows - 1)

    offsets = np.linspace(start=end, stop=-end, num=grid.rows)
    return np.tile(offsets, (grid.columns, 1)).transpose()


def pixel_grid_z_offsets(grid: PixelGrid):
    """
    Returns a list of 'row' lists of 'column' length.
    Each entry in the sublists are z positions of pixel instances in the given PixelGrid.
    """
    return [[0] * grid.columns] * grid.rows


def pixel_grid_detector_ids(grid: PixelGrid):
    """
    Returns an array of detector IDs. Starts with a 1D array of numbers and reorders them depending on the count
    direction and initial count corner supplied by the user.
    """

    ids = np.arange(grid.rows * grid.columns) + grid.first_id

    if grid.count_direction == CountDirection.COLUMN:
        ids = ids.reshape((grid.rows, grid.columns), order="F")
    else:
        ids = ids.reshape(grid.rows, grid.columns)

    if grid.initial_count_corner == Corner.TOP_LEFT:
        return ids

    if grid.initial_count_corner == Corner.TOP_RIGHT:
        return np.fliplr(ids)

    if grid.initial_count_corner == Corner.BOTTOM_LEFT:
        return np.flipud(ids)

    return np.rot90(ids, 2)
