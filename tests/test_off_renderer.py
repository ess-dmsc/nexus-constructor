from nexus_constructor.off_renderer import (
    QtOFFGeometry,
    create_vertex_buffer,
    create_normal_buffer,
)
from nexus_constructor.data_model import OFFGeometry
import itertools
from PySide2.QtGui import QVector3D

TRIANGLES_IN_SQUARE = 2
VERTICIES_IN_TRIANGLE = 3
POINTS_IN_VERTEX = 3


def test_GIVEN_a_single_triangle_face_WHEN_creating_vertex_buffer_THEN_output_is_correct():
    vertices = [QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0)]
    faces = [[0, 1, 2]]

    vertex_buffer = create_vertex_buffer(vertices, faces)

    expected_output = itertools.chain.from_iterable([v.toTuple() for v in vertices])

    assert list(vertex_buffer) == list(expected_output)


def test_GIVEN_a_set_of_triangle_faces_WHEN_creating_vertex_buffer_THEN_length_is_total_points_in_all_faces():
    vertices = [QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0), QVector3D(1, 0, 1)]
    faces = [[0, 1, 2], [3, 2, 0], [2, 3, 1]]

    vertex_buffer = create_vertex_buffer(vertices, faces)

    NUM_OF_TRIANGLES = len(faces)

    assert (
        len(list(vertex_buffer))
        == NUM_OF_TRIANGLES * VERTICIES_IN_TRIANGLE * POINTS_IN_VERTEX
    )


def test_GIVEN_a_square_WHEN_creating_vertex_buffer_THEN_length_is_correct():
    vertices = [QVector3D(0, 0, 0), QVector3D(1, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0)]
    faces = [[0, 1, 2, 3]]

    vertex_buffer = create_vertex_buffer(vertices, faces)

    assert (
        len(list(vertex_buffer))
        == TRIANGLES_IN_SQUARE * VERTICIES_IN_TRIANGLE * POINTS_IN_VERTEX
    )


def test_GIVEN_a_single_triangle_face_WHEN_creating_normal_buffer_THEN_output_is_correct():
    vertices = [QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0)]
    faces = [[0, 1, 2]]

    normal = create_normal_buffer(vertices, faces)

    expected_output = [0.0, 0.0, -1.0] * 3

    assert list(normal) == expected_output


def test_GIVEN_a_square_face_WHEN_creating_normal_buffer_THEN_output_is_correct():
    vertices = [QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0), QVector3D(1, 0, 0)]
    faces = [[0, 1, 2, 3]]

    normal = create_normal_buffer(vertices, faces)

    expected_output = [0.0, 0.0, -1.0] * TRIANGLES_IN_SQUARE * VERTICIES_IN_TRIANGLE

    assert list(normal) == expected_output


def test_GIVEN_a_triangle_WHEN_creating_off_geometry_with_no_pixel_data_THEN_vertex_count_equals_3():
    off_geometry = OFFGeometry(
        vertices=[QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 1, 0)], faces=[[0, 1, 2]]
    )

    qt_geometry = QtOFFGeometry(off_geometry, None)

    assert qt_geometry.vertex_count == 3
