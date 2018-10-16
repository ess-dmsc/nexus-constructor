import h5py
from math import sqrt
from pytest import approx
from geometry_constructor.writers import HdfWriter
from geometry_constructor.data_model import Detector, PixelGrid, Corner, CountDirection, Vector
from geometry_constructor.instrument_model import InstrumentModel


def assess_unit_length_3d_vector(vector, original):
    assert len(vector) == 3
    assert sum(i**2 for i in vector) == approx(1)
    assert original[0] / vector[0] == approx(original[1] / vector[1])
    assert original[0] / vector[0] == approx(original[2] / vector[2])


def make_instrument_with_sample_transform():
    instrument = InstrumentModel()
    instrument.components[0].translate_vector = Vector(7, 8, 9)
    instrument.components[0].rotate_axis = Vector(10, 11, 12)
    instrument.components[0].rotate_angle = 45
    instrument.components.append(Detector(name='detector1',
                                          transform_parent=instrument.components[0],
                                          translate_vector=Vector(1, 2, 3),
                                          rotate_axis=Vector(4, 5, 6),
                                          rotate_angle=90))
    return instrument


def test_save_root_component_translate():
    instrument = make_instrument_with_sample_transform()
    # use an in memory file to avoid disk usage during tests
    with h5py.File('transforms_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
        sample = file['entry/instrument/Sample']

        assert sample.attrs['NX_class'] == 'NXsample'
        assert sample.attrs['depends_on'] == 'translate'

        sample_translate = sample['translate']
        assert sample_translate[0] == approx(sqrt(sum(i**2 for i in [7, 8, 9])))
        assert sample_translate.attrs['NX_class'] == 'NXtransformations'
        assert sample_translate.attrs['transformation_type'] == 'translation'
        assert sample_translate.attrs['units'] == 'm'
        assess_unit_length_3d_vector(sample_translate.attrs['vector'], [7, 8, 9])
        assert sample_translate.attrs['depends_on'] == 'rotate'


def test_save_root_component_rotate():
    instrument = make_instrument_with_sample_transform()
    # use an in memory file to avoid disk usage during tests
    with h5py.File('transforms_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
        sample = file['entry/instrument/Sample']

        sample_rotate = sample['rotate']
        assert sample_rotate[0] == 45
        assert sample_rotate.attrs['NX_class'] == 'NXtransformations'
        assert sample_rotate.attrs['transformation_type'] == 'rotation'
        assert sample_rotate.attrs['units'] == 'degrees'
        assess_unit_length_3d_vector(sample_rotate.attrs['vector'], [10, 11, 12])
        assert sample_rotate.attrs['depends_on'] == '.'


def test_save_dependent_component_translate():
    instrument = make_instrument_with_sample_transform()
    # use an in memory file to avoid disk usage during tests
    with h5py.File('transforms_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
        detector = file['entry/instrument/detector1']

        assert detector.attrs['NX_class'] == 'NXdetector'
        assert detector.attrs['depends_on'] == 'translate'

        detector_translate = detector['translate']
        assert detector_translate[0] == approx(sqrt(sum(i**2 for i in [1, 2, 3])))
        assert detector_translate.attrs['NX_class'] == 'NXtransformations'
        assert detector_translate.attrs['transformation_type'] == 'translation'
        assert detector_translate.attrs['units'] == 'm'
        assess_unit_length_3d_vector(detector_translate.attrs['vector'], [1, 2, 3])
        assert detector_translate.attrs['depends_on'] == 'rotate'


def test_save_dependent_component_rotate():
    instrument = make_instrument_with_sample_transform()
    # use an in memory file to avoid disk usage during tests
    with h5py.File('transforms_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
        detector = file['entry/instrument/detector1']

        detector_rotate = detector['rotate']
        assert detector_rotate[0] == 90
        assert detector_rotate.attrs['NX_class'] == 'NXtransformations'
        assert detector_rotate.attrs['transformation_type'] == 'rotation'
        assert detector_rotate.attrs['units'] == 'degrees'
        assess_unit_length_3d_vector(detector_rotate.attrs['vector'], [4, 5, 6])
        assert detector_rotate.attrs['depends_on'] == '/entry/instrument/Sample/translate'


def test_save_pixel_grid_coordinates():
    instrument = InstrumentModel()
    instrument.components.append(Detector(name='detector',
                                          pixel_data=PixelGrid(rows=3, columns=4, row_height=1.5, col_width=2,
                                                               first_id=0, count_direction=CountDirection.ROW,
                                                               initial_count_corner=Corner.BOTTOM_LEFT)))
    # use an in memory file to avoid disk usage during tests
    with h5py.File('grid_coordinate_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
        x_dataset = file['/entry/instrument/detector/x_pixel_offset'][::].tolist()
        y_dataset = file['/entry/instrument/detector/y_pixel_offset'][::].tolist()
        z_dataset = file['/entry/instrument/detector/z_pixel_offset'][::].tolist()
        assert x_dataset == [[0, 2, 4, 6],
                             [0, 2, 4, 6],
                             [0, 2, 4, 6]]
        assert y_dataset == [[0, 0, 0, 0],
                             [1.5, 1.5, 1.5, 1.5],
                             [3, 3, 3, 3]]
        assert z_dataset == [[0, 0, 0, 0],
                             [0, 0, 0, 0],
                             [0, 0, 0, 0]]


def assess_pixel_grid_direction(direction, corner, expected_data):
    instrument = InstrumentModel()
    instrument.components.append(Detector(name='detector',
                                          pixel_data=PixelGrid(rows=3, columns=4, row_height=0.1, col_width=0.3,
                                                               first_id=0, count_direction=direction,
                                                               initial_count_corner=corner)))
    # use an in memory file to avoid disk usage during tests
    with h5py.File('grid_direction_testfile', driver='core', backing_store=False) as file:
        HdfWriter().save_instrument_to_file(file, instrument)
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
