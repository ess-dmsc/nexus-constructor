from nexus_constructor.pixel_data import PixelGrid
from nexus_constructor.geometry import OFFGeometryNoNexus
from nexus_constructor.geometry_loader import load_geometry_from_file_object
from nexus_constructor.off_renderer import QtOFFGeometry
from PySide2.QtGui import QVector3D
import struct
from io import StringIO


def test_GIVEN_off_file_containing_geometry_WHEN_loading_geometry_to_file_THEN_vertices_and_faces_loaded_are_the_same_as_the_file():
    model = OFFGeometryNoNexus()
    model.units = "m"

    off_file = (
        "OFF\n"
        "#  cube.off\n"
        "#  A cube\n"
        "8 6 0\n"
        "-0.500000 -0.500000 0.500000\n"
        "0.500000 -0.500000 0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "0.500000 0.500000 0.500000\n"
        "-0.500000 0.500000 -0.500000\n"
        "0.500000 0.500000 -0.500000\n"
        "-0.500000 -0.500000 -0.500000\n"
        "0.500000 -0.500000 -0.500000\n"
        "4 0 1 3 2\n"
        "4 2 3 5 4\n"
        "4 4 5 7 6\n"
        "4 6 7 1 0\n"
        "4 1 7 5 3\n"
        "4 6 0 2 4\n"
    )

    load_geometry_from_file_object(StringIO(off_file), ".off", model.units, model)

    assert model.vertices == [
        QVector3D(-0.5, -0.5, 0.5),
        QVector3D(0.5, -0.5, 0.5),
        QVector3D(-0.5, 0.5, 0.5),
        QVector3D(0.5, 0.5, 0.5),
        QVector3D(-0.5, 0.5, -0.5),
        QVector3D(0.5, 0.5, -0.5),
        QVector3D(-0.5, -0.5, -0.5),
        QVector3D(0.5, -0.5, -0.5),
    ]
    assert model.faces == [
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
        [6, 7, 1, 0],
        [1, 7, 5, 3],
        [6, 0, 2, 4],
    ]
    assert model.winding_order == [
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
    assert model.winding_order_indices == [0, 4, 8, 12, 16, 20]


def test_GIVEN_stl_file_with_cube_geometry_WHEN_loading_geometry_THEN_all_faces_are_present():
    length = 30
    left_lower_rear = QVector3D(0, 0, 0)
    right_lower_rear = QVector3D(length, 0, 0)
    left_upper_rear = QVector3D(0, length, 0)
    right_upper_rear = QVector3D(length, length, 0)
    left_lower_front = QVector3D(0, 0, length)
    right_lower_front = QVector3D(length, 0, length)
    left_upper_front = QVector3D(0, length, length)
    right_upper_front = QVector3D(length, length, length)
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

    cube = """solid vcg
        facet normal -1.000000e+00  0.000000e+00  0.000000e+00
        outer loop
        vertex   0.000000e+00  3.000000e+01  0.000000e+00
        vertex   0.000000e+00  0.000000e+00  3.000000e+01
        vertex   0.000000e+00  3.000000e+01  3.000000e+01
        endloop
        endfacet
        facet normal -1.000000e+00  0.000000e+00  0.000000e+00
        outer loop
        vertex   0.000000e+00  0.000000e+00  0.000000e+00
        vertex   0.000000e+00  0.000000e+00  3.000000e+01
        vertex   0.000000e+00  3.000000e+01  0.000000e+00
        endloop
        endfacet
        facet normal  1.000000e+00 -0.000000e+00  0.000000e+00
        outer loop
        vertex   3.000000e+01  0.000000e+00  3.000000e+01
        vertex   3.000000e+01  3.000000e+01  0.000000e+00
        vertex   3.000000e+01  3.000000e+01  3.000000e+01
        endloop
        endfacet
        facet normal  1.000000e+00  0.000000e+00  0.000000e+00
        outer loop
        vertex   3.000000e+01  0.000000e+00  3.000000e+01
        vertex   3.000000e+01  0.000000e+00  0.000000e+00
        vertex   3.000000e+01  3.000000e+01  0.000000e+00
        endloop
        endfacet
        facet normal  0.000000e+00 -1.000000e+00  0.000000e+00
        outer loop
        vertex   3.000000e+01  0.000000e+00  0.000000e+00
        vertex   3.000000e+01  0.000000e+00  3.000000e+01
        vertex   0.000000e+00  0.000000e+00  0.000000e+00
        endloop
        endfacet
        facet normal  0.000000e+00 -1.000000e+00  0.000000e+00
        outer loop
        vertex   0.000000e+00  0.000000e+00  0.000000e+00
        vertex   3.000000e+01  0.000000e+00  3.000000e+01
        vertex   0.000000e+00  0.000000e+00  3.000000e+01
        endloop
        endfacet
        facet normal  0.000000e+00  1.000000e+00  0.000000e+00
        outer loop
        vertex   3.000000e+01  3.000000e+01  3.000000e+01
        vertex   3.000000e+01  3.000000e+01  0.000000e+00
        vertex   0.000000e+00  3.000000e+01  0.000000e+00
        endloop
        endfacet
        facet normal  0.000000e+00  1.000000e+00  0.000000e+00
        outer loop
        vertex   3.000000e+01  3.000000e+01  3.000000e+01
        vertex   0.000000e+00  3.000000e+01  0.000000e+00
        vertex   0.000000e+00  3.000000e+01  3.000000e+01
        endloop
        endfacet
        facet normal  0.000000e+00  0.000000e+00 -1.000000e+00
        outer loop
        vertex   0.000000e+00  3.000000e+01  0.000000e+00
        vertex   3.000000e+01  3.000000e+01  0.000000e+00
        vertex   0.000000e+00  0.000000e+00  0.000000e+00
        endloop
        endfacet
        facet normal  0.000000e+00  0.000000e+00 -1.000000e+00
        outer loop
        vertex   0.000000e+00  0.000000e+00  0.000000e+00
        vertex   3.000000e+01  3.000000e+01  0.000000e+00
        vertex   3.000000e+01  0.000000e+00  0.000000e+00
        endloop
        endfacet
        facet normal  0.000000e+00  0.000000e+00  1.000000e+00
        outer loop
        vertex   3.000000e+01  3.000000e+01  3.000000e+01
        vertex   0.000000e+00  3.000000e+01  3.000000e+01
        vertex   0.000000e+00  0.000000e+00  3.000000e+01
        endloop
        endfacet
        facet normal  0.000000e+00  0.000000e+00  1.000000e+00
        outer loop
        vertex   3.000000e+01  3.000000e+01  3.000000e+01
        vertex   0.000000e+00  0.000000e+00  3.000000e+01
        vertex   3.000000e+01  0.000000e+00  3.000000e+01
        endloop
        endfacet
        endsolid vcg"""

    geometry = load_geometry_from_file_object(StringIO(cube), ".stl", "m")

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


def test_GIVEN_unrecognised_file_extension_WHEN_loading_geometry_THEN_returns_empty_geometry():
    geometry = load_geometry_from_file_object(StringIO(), ".txt", "m")
    assert len(geometry.vertices) == 0
    assert len(geometry.faces) == 0


def test_generate_off_mesh_without_repeating_grid():
    # A square with a triangle on the side
    off_geometry = OFFGeometryNoNexus(
        vertices=[
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
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
    off_geometry = OFFGeometryNoNexus(
        vertices=[
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
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
