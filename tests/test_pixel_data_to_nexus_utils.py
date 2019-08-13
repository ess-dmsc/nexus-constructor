import numpy as np
import pytest

from nexus_constructor.pixel_data import PixelMapping, PixelGrid, CountDirection, Corner
from nexus_constructor.pixel_data_to_nexus_utils import (
    detector_faces,
    pixel_grid_x_offsets,
    pixel_grid_y_offsets,
    pixel_grid_detector_ids,
    pixel_grid_z_offsets,
    detector_number,
)


@pytest.fixture(scope="function")
def pixel_grid():
    return PixelGrid(
        rows=5,
        columns=4,
        row_height=0.873,
        col_width=2.0 / 3,
        first_id=0,
        count_direction=CountDirection.ROW,
        initial_count_corner=Corner.BOTTOM_LEFT,
    )


@pytest.fixture(scope="function")
def pixel_mapping():
    ids_with_some_that_are_none = [i if i % 3 != 0 else None for i in range(10)]
    return PixelMapping(ids_with_some_that_are_none)


def test_GIVEN_list_of_ids_WHEN_calling_detector_faces_THEN_correct_detector_faces_list_is_returned(
    pixel_mapping
):

    ids_with_none_removed = [id for id in pixel_mapping.pixel_ids if id is not None]
    expected_faces = [
        (i, ids_with_none_removed[i]) for i in range(len(ids_with_none_removed))
    ]

    assert detector_faces(pixel_mapping) == expected_faces


def test_GIVEN_list_of_ids_WHEN_calling_detector_number_THEN_correct_detector_number_list_is_returned(
    pixel_mapping
):

    expected_numbers = [id for id in pixel_mapping.pixel_ids if id is not None]

    assert detector_number(pixel_mapping) == expected_numbers


def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_x_offsets_THEN_correct_x_offset_list_is_returned(
    pixel_grid
):

    offset_offset = (pixel_grid.columns - 1) * pixel_grid.col_width / 2
    expected_x_offsets = [
        [(i * pixel_grid.col_width) - offset_offset for i in range(pixel_grid.columns)]
        for _ in range(pixel_grid.rows)
    ]
    assert np.allclose(np.array(expected_x_offsets), pixel_grid_x_offsets(pixel_grid))


def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_y_offsets_THEN_correct_y_offset_list_is_returned(
    pixel_grid
):

    offset_offset = (pixel_grid.rows - 1) * pixel_grid.row_height / 2
    expected_y_offsets = [
        [(j * pixel_grid.row_height) - offset_offset for _ in range(pixel_grid.columns)]
        for j in reversed(range(pixel_grid.rows))
    ]
    assert np.allclose(np.array(expected_y_offsets), pixel_grid_y_offsets(pixel_grid))


def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_z_offsets_THEN_z_offsets_are_all_zero(
    pixel_grid
):

    z_offsets = pixel_grid_z_offsets(pixel_grid)

    assert len(z_offsets) == pixel_grid.rows
    expected_row = [0 for _ in range(pixel_grid.columns)]

    for actual_row in z_offsets:
        assert actual_row == expected_row


def test_nothing(pixel_grid):

    for direction in CountDirection:
        for corner in Corner:
            print(direction, corner)
            pixel_grid.count_direction = direction
            pixel_grid.initial_count_corner = corner

            detector_ids = pixel_grid_detector_ids(pixel_grid)

            for row in detector_ids:
                print(row)

            print("")
