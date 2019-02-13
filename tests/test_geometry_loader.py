from nexus_constructor.data_model import Vector, OFFGeometry, PixelGrid
from nexus_constructor.geometry_loader import load_geometry, is_length
from nexus_constructor.off_renderer import QtOFFGeometry
from nexus_constructor.qml_models.geometry_models import OFFModel
from PySide2.QtCore import QUrl
import struct
import pint


def test_vertices_and_faces_loaded_correctly_from_off_cube_file():
    model = OFFModel()
    model.setData(0, QUrl("tests/cube.off"), OFFModel.FileNameRole)
    off_geometry = model.get_geometry()
    assert isinstance(off_geometry, OFFGeometry)
    assert off_geometry.vertices == [
        Vector(-0.5, -0.5, 0.5),
        Vector(0.5, -0.5, 0.5),
        Vector(-0.5, 0.5, 0.5),
        Vector(0.5, 0.5, 0.5),
        Vector(-0.5, 0.5, -0.5),
        Vector(0.5, 0.5, -0.5),
        Vector(-0.5, -0.5, -0.5),
        Vector(0.5, -0.5, -0.5),
    ]
    assert off_geometry.faces == [
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
        [6, 7, 1, 0],
        [1, 7, 5, 3],
        [6, 0, 2, 4],
    ]
    assert off_geometry.winding_order == [
        0,
        1,
        3,
        2,
        2,
        3,
        5,
        4,
        4,
        5,
        7,
        6,
        6,
        7,
        1,
        0,
        1,
        7,
        5,
        3,
        6,
        0,
        2,
        4,
    ]
    assert off_geometry.winding_order_indices == [0, 4, 8, 12, 16, 20]


def test_all_faces_present_in_geometry_loaded_from_stl_cube_file():
    length = 30
    left_lower_rear = Vector(0, 0, 0)
    right_lower_rear = Vector(length, 0, 0)
    left_upper_rear = Vector(0, length, 0)
    right_upper_rear = Vector(length, length, 0)
    left_lower_front = Vector(0, 0, length)
    right_lower_front = Vector(length, 0, length)
    left_upper_front = Vector(0, length, length)
    right_upper_front = Vector(length, length, length)
    # faces on a cube with a right hand winding order
    faces = [
        [
            left_lower_front,
            left_lower_rear,
            right_lower_rear,
            right_lower_front,
        ],  # bottom
        [left_lower_front, left_upper_front, left_upper_rear, left_lower_rear],  # left
        [
            left_upper_front,
            left_lower_front,
            right_lower_front,
            right_upper_front,
        ],  # front
        [
            right_upper_front,
            right_lower_front,
            right_lower_rear,
            right_upper_rear,
        ],  # right
        [right_upper_rear, right_lower_rear, left_lower_rear, left_upper_rear],  # rear
        [left_upper_rear, left_upper_front, right_upper_front, right_upper_rear],  # top
    ]

    geometry = load_geometry("tests/cube.stl")
    # 2 triangles per face, 6 faces in the cube
    assert len(geometry.faces) == 6 * 2
    assert geometry.winding_order_indices == [i * 3 for i in range(12)]
    # each expected vertex is in the shape
    for vertex in [
        left_lower_rear,
        right_lower_rear,
        left_upper_rear,
        right_upper_rear,
        left_lower_front,
        right_lower_front,
        left_upper_front,
        right_upper_front,
    ]:
        assert vertex in geometry.vertices
    # each face must be in the loaded geometry
    for face in faces:
        face_found = False
        # each face could be split into triangles in one of two ways
        for triangle_split in [
            [[face[0], face[1], face[2]], [face[2], face[3], face[0]]],
            [[face[1], face[2], face[3]], [face[3], face[0], face[1]]],
        ]:
            triangle_matches = 0
            # each triangle in the square's split must be in the loaded geometry for the square to be
            for triangle in triangle_split:
                # check the triangle against each rotation of each triangle in the geometry
                for candidate_triangle_indices in geometry.faces:
                    a = geometry.vertices[candidate_triangle_indices[0]]
                    b = geometry.vertices[candidate_triangle_indices[1]]
                    c = geometry.vertices[candidate_triangle_indices[2]]
                    if (
                        triangle == [a, b, c]
                        or triangle == [b, c, a]
                        or triangle == [c, a, b]
                    ):
                        triangle_matches += 1
            if triangle_matches == 2:
                face_found = True
        assert face_found


def test_load_geometry_returns_empty_geometry_for_unrecognised_file_extension():
    geometry = load_geometry("tests/collapsed lines.txt")
    assert len(geometry.vertices) == 0
    assert len(geometry.faces) == 0


def test_generate_off_mesh_without_repeating_grid():
    # A square with a triangle on the side
    off_geometry = OFFGeometry(
        vertices=[
            Vector(0, 0, 0),
            Vector(0, 1, 0),
            Vector(1, 1, 0),
            Vector(1, 0, 0),
            Vector(1.5, 0.5, 0),
        ],
        faces=[[0, 1, 2, 3], [2, 3, 4]],
    )
    qt_geometry = QtOFFGeometry(off_geometry, None)
    # 3 triangles total, 3 points per triangle
    assert qt_geometry.vertex_count == 3 * 3
    vertex_data_bytes = eval(str(qt_geometry.attributes()[0].buffer().data()))
    vertex_data = list(
        struct.unpack("%sf" % (qt_geometry.vertex_count * 3), vertex_data_bytes)
    )
    generated_triangles = [
        vertex_data[i : i + 9] for i in range(0, len(vertex_data), 9)
    ]

    triangles = [
        [0, 0, 0, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 1, 0, 1, 0, 0],
        [1, 1, 0, 1, 0, 0, 1.5, 0.5, 0],
    ]
    # check the triangles are present
    for triangle in triangles:
        assert triangle in generated_triangles


def test_generate_off_mesh_with_repeating_grid():
    rows = 2
    row_height = 3
    columns = 5
    column_width = 7
    # A square with a triangle on the side
    off_geometry = OFFGeometry(
        vertices=[
            Vector(0, 0, 0),
            Vector(0, 1, 0),
            Vector(1, 1, 0),
            Vector(1, 0, 0),
            Vector(1.5, 0.5, 0),
        ],
        faces=[[0, 1, 2, 3], [2, 3, 4]],
    )
    qt_geometry = QtOFFGeometry(
        off_geometry,
        PixelGrid(
            rows=rows, row_height=row_height, columns=columns, col_width=column_width
        ),
    )
    # rows of copies, 3 triangles total, 3 points per triangle
    assert qt_geometry.vertex_count == rows * columns * 3 * 3

    vertex_data_bytes = eval(str(qt_geometry.attributes()[0].buffer().data()))
    vertex_data = list(
        struct.unpack("%sf" % (qt_geometry.vertex_count * 3), vertex_data_bytes)
    )
    generated_triangles = [
        vertex_data[i : i + 9] for i in range(0, len(vertex_data), 9)
    ]

    for i in range(rows):
        for j in range(columns):
            x_offset = j * column_width
            y_offset = i * row_height
            triangles = [
                [
                    0 + x_offset,
                    0 + y_offset,
                    0,
                    0 + x_offset,
                    1 + y_offset,
                    0,
                    1 + x_offset,
                    1 + y_offset,
                    0,
                ],
                [
                    0 + x_offset,
                    0 + y_offset,
                    0,
                    1 + x_offset,
                    1 + y_offset,
                    0,
                    1 + x_offset,
                    0 + y_offset,
                    0,
                ],
                [
                    1 + x_offset,
                    1 + y_offset,
                    0,
                    1 + x_offset,
                    0 + y_offset,
                    0,
                    1.5 + x_offset,
                    0.5 + y_offset,
                    0,
                ],
            ]
            # check the triangles are present
            for triangle in triangles:
                assert triangle in generated_triangles


def test_is_length():

    lengths = ["mile", "cm", "centimetre", "yard", "km"]
    not_lengths = ["minute", "hour", "ounce", "stone", "pound", "amp", "abc"]

    for unit in lengths:
        assert is_length(unit)

    for unit in not_lengths:
        assert not is_length(unit)
