import h5py
from geometry_constructor.Writers import HdfWriter
from geometry_constructor.Models import InstrumentModel, Detector, PixelGrid, Corner, CountDirection


def assess_pixel_grid_direction(direction, corner, expected_data):
    instrument = InstrumentModel()
    instrument.components.append(Detector(name='detector',
                                          id=1,
                                          transform_parent_id=0,
                                          pixel_data=PixelGrid(rows=3, columns=4, row_height=0.1, col_width=0.3,
                                                               first_id=0, count_direction=direction,
                                                               initial_count_corner=corner)))
    filename = 'grid_direction_testfile.hdf5'
    HdfWriter().save_instrument(filename, instrument)
    with h5py.File(filename, 'r') as file:
        dataset = file['/entry/instrument/detector/detector_number'][::].tolist()
        assert dataset == expected_data


def test_save_pixel_grid_counting_across_from_bottom_left():
    assess_pixel_grid_direction(CountDirection.ROW,
                                Corner.BOTTOM_LEFT,
                                [[0, 1, 2, 3],
                                 [4, 5, 6, 7],
                                 [8, 9, 10, 11]])


def test_save_pixel_grid_counting_across_from_top_left():
    assess_pixel_grid_direction(CountDirection.ROW,
                                Corner.TOP_LEFT,
                                [[8, 9, 10, 11],
                                 [4, 5, 6, 7],
                                 [0, 1, 2, 3]])


def test_save_pixel_grid_counting_across_from_top_right():
    assess_pixel_grid_direction(CountDirection.ROW,
                                Corner.TOP_RIGHT,
                                [[11, 10, 9, 8],
                                 [7, 6, 5, 4],
                                 [3, 2, 1, 0]])


def test_save_pixel_grid_counting_across_from_bottom_right():
    assess_pixel_grid_direction(CountDirection.ROW,
                                Corner.BOTTOM_RIGHT,
                                [[3, 2, 1, 0],
                                 [7, 6, 5, 4],
                                 [11, 10, 9, 8]])


def test_save_pixel_grid_counting_vertical_from_bottom_left():
    assess_pixel_grid_direction(CountDirection.COLUMN,
                                Corner.BOTTOM_LEFT,
                                [[0, 3, 6, 9],
                                 [1, 4, 7, 10],
                                 [2, 5, 8, 11]])


def test_save_pixel_grid_counting_vertical_from_top_left():
    assess_pixel_grid_direction(CountDirection.COLUMN,
                                Corner.TOP_LEFT,
                                [[2, 5, 8, 11],
                                 [1, 4, 7, 10],
                                 [0, 3, 6, 9]])


def test_save_pixel_grid_counting_vertical_from_top_right():
    assess_pixel_grid_direction(CountDirection.COLUMN,
                                Corner.TOP_RIGHT,
                                [[11, 8, 5, 2],
                                 [10, 7, 4, 1],
                                 [9, 6, 3, 0]])


def test_save_pixel_grid_counting_vertical_from_bottom_right():
    assess_pixel_grid_direction(CountDirection.COLUMN,
                                Corner.BOTTOM_RIGHT,
                                [[9, 6, 3, 0],
                                 [10, 7, 4, 1],
                                 [11, 8, 5, 2]])
