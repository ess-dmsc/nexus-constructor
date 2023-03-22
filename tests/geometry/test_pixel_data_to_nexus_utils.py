import numpy as np
import pytest

from nexus_constructor.geometry.pixel_data import (
    Corner,
    CountDirection,
    PixelGrid,
    PixelMapping,
)
from nexus_constructor.geometry.pixel_data_utils import (
    get_detector_faces_from_pixel_mapping,
    get_detector_ids_from_pixel_grid,
    get_detector_number_from_pixel_mapping,
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
)

EXPECTED_DETECTOR_IDS = {
    CountDirection.ROW: {
        Corner.TOP_LEFT: [[0, 1, 2], [3, 4, 5]],
        Corner.TOP_RIGHT: [[2, 1, 0], [5, 4, 3]],
        Corner.BOTTOM_LEFT: [[3, 4, 5], [0, 1, 2]],
        Corner.BOTTOM_RIGHT: [[5, 4, 3], [2, 1, 0]],
    },
    CountDirection.COLUMN: {
        Corner.TOP_LEFT: [[0, 2, 4], [1, 3, 5]],
        Corner.TOP_RIGHT: [[4, 2, 0], [5, 3, 1]],
        Corner.BOTTOM_LEFT: [[1, 3, 5], [0, 2, 4]],
        Corner.BOTTOM_RIGHT: [[5, 3, 1], [4, 2, 0]],
    },
}

ROW_COL_VALS = [4, 7]


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
    pixel_mapping,
):
    expected_faces = [
        (i, pixel_mapping.pixel_ids[i])
        for i in range(len(pixel_mapping.pixel_ids))
        if pixel_mapping.pixel_ids[i] is not None
    ]

    assert get_detector_faces_from_pixel_mapping(pixel_mapping) == expected_faces


def test_GIVEN_single_id_WHEN_calling_detector_faces_THEN_list_is_not_returned(
    pixel_mapping,
):
    pixel_id = 3
    pixel_mapping.pixel_ids = [pixel_id]
    assert get_detector_faces_from_pixel_mapping(pixel_mapping) == [(0, pixel_id)]


def test_GIVEN_list_of_ids_WHEN_calling_detector_number_THEN_correct_detector_number_list_is_returned(
    pixel_mapping,
):
    expected_numbers = [id for id in pixel_mapping.pixel_ids if id is not None]

    assert get_detector_number_from_pixel_mapping(pixel_mapping) == expected_numbers


def test_GIVEN_single_id_WHEN_calling_detector_number_THEN_list_is_not_returned(
    pixel_mapping,
):
    pixel_id = 3
    pixel_mapping.pixel_ids = [pixel_id]
    assert get_detector_number_from_pixel_mapping(pixel_mapping) == [pixel_id]


@pytest.mark.parametrize("rows", ROW_COL_VALS)
@pytest.mark.parametrize("columns", ROW_COL_VALS)
def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_x_offsets_THEN_correct_x_offset_list_is_returned(
    pixel_grid, rows, columns
):
    pixel_grid.columns = columns
    pixel_grid.rows = rows

    offset_offset = (pixel_grid.columns - 1) * pixel_grid.col_width / 2
    expected_x_offsets = [
        [(i * pixel_grid.col_width) - offset_offset for i in range(pixel_grid.columns)]
        for _ in range(pixel_grid.rows)
    ]

    assert np.allclose(
        np.array(expected_x_offsets), get_x_offsets_from_pixel_grid(pixel_grid)
    )


@pytest.mark.parametrize("rows", ROW_COL_VALS)
@pytest.mark.parametrize("columns", ROW_COL_VALS)
def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_y_offsets_THEN_correct_y_offset_list_is_returned(
    pixel_grid, rows, columns
):
    pixel_grid.columns = columns
    pixel_grid.rows = rows

    offset_offset = (pixel_grid.rows - 1) * pixel_grid.row_height / 2
    expected_y_offsets = [
        [(j * pixel_grid.row_height) - offset_offset for _ in range(pixel_grid.columns)]
        for j in reversed(range(pixel_grid.rows))
    ]

    assert np.allclose(
        np.array(expected_y_offsets), get_y_offsets_from_pixel_grid(pixel_grid)
    )


@pytest.mark.parametrize("rows", ROW_COL_VALS)
@pytest.mark.parametrize("columns", ROW_COL_VALS)
def test_GIVEN_pixel_grid_WHEN_calling_pixel_grid_z_offsets_THEN_z_offsets_are_all_zero(
    pixel_grid, rows, columns
):
    pixel_grid.rows = rows
    pixel_grid.columns = columns

    z_offsets = get_z_offsets_from_pixel_grid(pixel_grid)

    assert np.array_equal(np.zeros((rows, columns)), z_offsets)


@pytest.mark.parametrize("direction", CountDirection)
@pytest.mark.parametrize("corner", Corner)
def test_GIVEN_direction_and_initial_count_corner_WHEN_calling_pixel_grid_detector_ids_THEN_correct_grid_is_returned(
    pixel_grid, direction, corner
):
    pixel_grid.rows = 2
    pixel_grid.columns = 3
    pixel_grid.count_direction = direction
    pixel_grid.initial_count_corner = corner
    pixel_grid.first_id = 2

    assert np.array_equal(
        np.array(EXPECTED_DETECTOR_IDS[direction][corner]) + pixel_grid.first_id,
        get_detector_ids_from_pixel_grid(pixel_grid),
    )


def test_GIVEN_one_by_one_pixel_grid_when_calling_offset_functions_THEN_offsets_and_pixel_id_are_scalars(
    pixel_grid,
):
    pixel_grid.rows = 1
    pixel_grid.columns = 1

    assert get_x_offsets_from_pixel_grid(pixel_grid) == 0
    assert get_y_offsets_from_pixel_grid(pixel_grid) == 0
    assert get_z_offsets_from_pixel_grid(pixel_grid) == 0

    assert get_detector_ids_from_pixel_grid(pixel_grid) == pixel_grid.first_id
