import numpy as np
import pytest

from nexus_constructor.pixel_data import PixelMapping, PixelGrid, CountDirection, Corner
from nexus_constructor.pixel_data_to_nexus_utils import (
    detector_faces,
    pixel_grid_x_offsets,
    pixel_grid_y_offsets,
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
        initial_count_corner=Corner.TOP_RIGHT,
    )


def test_GIVEN_list_of_ids_THEN_correct_detector_faces_list_is_created():

    ids_with_some_that_are_none = [i if i % 3 != 0 else None for i in range(10)]
    mapping = PixelMapping(ids_with_some_that_are_none)

    ids_with_none_removed = [id for id in ids_with_some_that_are_none if id is not None]
    expected_faces = [
        (i, ids_with_none_removed[i]) for i in range(len(ids_with_none_removed))
    ]

    assert detector_faces(mapping) == expected_faces


def test_GIVEN_pixel_grid_THEN_correct_x_offset_list_is_created(pixel_grid):

    offset_offset = (pixel_grid.columns - 1) * pixel_grid.col_width / 2
    expected_x_offsets = [
        [(i * pixel_grid.col_width) - offset_offset for i in range(pixel_grid.columns)]
        for _ in range(pixel_grid.rows)
    ]
    assert np.allclose(np.array(expected_x_offsets), pixel_grid_x_offsets(pixel_grid))


def test_GIVEN_pixel_grid_THEN_correct_y_offset_list_is_created(pixel_grid):

    offset_offset = (pixel_grid.rows - 1) * pixel_grid.row_height / 2
    expected_y_offsets = [
        [(j * pixel_grid.row_height) - offset_offset for _ in range(pixel_grid.columns)]
        for j in reversed(range(pixel_grid.rows))
    ]
    assert np.allclose(np.array(expected_y_offsets), pixel_grid_y_offsets(pixel_grid))
