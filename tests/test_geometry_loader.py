from nexus_constructor.pixel_data import PixelGrid
from nexus_constructor.geometry import OFFGeometryNoNexus
from nexus_constructor.geometry.geometry_loader import load_geometry_from_file_object
from nexus_constructor.off_renderer import QtOFFGeometry, repeat_shape_over_grid
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


def test_WHEN_generate_off_mesh_with_no_repeat_THEN_off_unchanged():
    original_vertices = [
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
        ]
    original_faces = [[0, 1, 2, 3], [2, 3, 4]]

    # A square with a triangle on the side
    off_geometry = OFFGeometryNoNexus(
        vertices=original_vertices,
        faces=original_faces,
    )

    pixel_grid = PixelGrid(
            rows=1, row_height=1, columns=1, col_width=1
        )

    faces, vertices = repeat_shape_over_grid(off_geometry, pixel_grid)

    assert faces == original_faces
    assert vertices == original_vertices

def test_WHEN_generate_off_mesh_with_two_by_two_grid_THEN_original_shape_remains():
    original_vertices = [
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
        ]
    original_faces = [[0, 1, 2, 3], [2, 3, 4]]

    # A square with a triangle on the side
    off_geometry = OFFGeometryNoNexus(
        vertices=original_vertices,
        faces=original_faces,
    )

    pixel_grid = PixelGrid(
            rows=2, row_height=1, columns=2, col_width=1
        )

    faces, vertices = repeat_shape_over_grid(off_geometry, pixel_grid)

    assert faces[:len(original_faces)] == original_faces
    assert vertices[:len(original_vertices)] == original_vertices


def test_WHEN_generate_off_mesh_with_row_of_two_THEN_second_shape_just_translation_of_first():
    original_vertices = [
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
        ]
    original_faces = [[0, 1, 2, 3], [2, 3, 4]]

    # A square with a triangle on the side
    off_geometry = OFFGeometryNoNexus(
        vertices=original_vertices,
        faces=original_faces,
    )

    pixel_grid = PixelGrid(
            rows=1, row_height=1, columns=2, col_width=1
        )

    faces, vertices = repeat_shape_over_grid(off_geometry, pixel_grid)

    second_shape_faces = faces[len(original_faces):]
    second_shape_vertices = vertices[len(original_vertices):]

    # Faces will just be the same but every vertex added to be len(verticies)
    shifted_faces = []
    for face in second_shape_faces:
        shifted_face = []
        for vertex in face:
            shifted_face.append(vertex - len(original_vertices))
        shifted_faces.append(shifted_face)

    assert shifted_faces == original_faces

    # Vertices will be the same by shifted by 1
    for vertex in second_shape_vertices:
        vertex.setX(vertex.x()-1)

    assert second_shape_vertices == original_vertices


def test_WHEN_generate_off_mesh_with_column_of_two_THEN_second_shape_just_translation_of_first():
    original_vertices = [
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0),
            QVector3D(1, 1, 0),
            QVector3D(1, 0, 0),
            QVector3D(1.5, 0.5, 0),
        ]
    original_faces = [[0, 1, 2, 3], [2, 3, 4]]

    # A square with a triangle on the side
    off_geometry = OFFGeometryNoNexus(
        vertices=original_vertices,
        faces=original_faces,
    )

    pixel_grid = PixelGrid(
            rows=2, row_height=1, columns=1, col_width=1
        )

    faces, vertices = repeat_shape_over_grid(off_geometry, pixel_grid)

    second_shape_faces = faces[len(original_faces):]
    second_shape_vertices = vertices[len(original_vertices):]

    # Faces will just be the same but every vertex added to be len(verticies)
    shifted_faces = []
    for face in second_shape_faces:
        shifted_face = []
        for vertex in face:
            shifted_face.append(vertex - len(original_vertices))
        shifted_faces.append(shifted_face)

    assert shifted_faces == original_faces

    # Vertices will be the same by shifted by 1
    for vertex in second_shape_vertices:
        vertex.setY(vertex.y()-1)

    assert second_shape_vertices == original_vertices