from geometry_constructor.data_model import Vector, OFFGeometry, PixelGrid
from geometry_constructor.geometry_models import OFFModel
from geometry_constructor.off_renderer import QtOFFGeometry
from PySide2.QtCore import QUrl
import struct


def test_load_off_file():
    model = OFFModel()
    model.setData(0, QUrl('tests/cube.off'), OFFModel.FileNameRole)
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
        Vector(0.5, -0.5, -0.5)
    ]
    assert off_geometry.faces == [
        [0, 1, 3, 2],
        [2, 3, 5, 4],
        [4, 5, 7, 6],
        [6, 7, 1, 0],
        [1, 7, 5, 3],
        [6, 0, 2, 4]
    ]
    assert off_geometry.winding_order == [0, 1, 3, 2, 2, 3, 5, 4, 4, 5, 7, 6, 6, 7, 1, 0, 1, 7, 5, 3, 6, 0, 2, 4]
    assert off_geometry.winding_order_indices == [0, 4, 8, 12, 16, 20]


def test_generate_off_mesh_without_repeating_grid():
    # A square with a triangle on the side
    off_geometry = OFFGeometry(vertices=[Vector(0, 0, 0),
                                         Vector(0, 1, 0),
                                         Vector(1, 1, 0),
                                         Vector(1, 0, 0),
                                         Vector(1.5, 0.5, 0)],
                               faces=[[0, 1, 2, 3],
                                      [2, 3, 4]])
    qt_geometry = QtOFFGeometry(off_geometry, None)
    # 2 sides per shape, 3 triangles total, 3 points per triangle
    assert qt_geometry.vertex_count == 2 * 3 * 3
    vertex_data_bytes = eval(str(qt_geometry.attributes()[0].buffer().data()))
    vertex_data = list(struct.unpack('%sf' % (qt_geometry.vertex_count * 3), vertex_data_bytes))
    generated_triangles = [vertex_data[i:i + 9] for i in range(0, len(vertex_data), 9)]

    triangles = [[0, 0, 0,
                  0, 1, 0,
                  1, 1, 0],
                 [0, 0, 0,
                  1, 1, 0,
                  1, 0, 0],
                 [1, 1, 0,
                  1, 0, 0,
                  1.5, 0.5, 0]]
    # check the triangle and its inverted winding are present
    for triangle in triangles:
        assert triangle in generated_triangles
        assert triangle[0:3] + triangle[6:9] + triangle[3:6] in generated_triangles


def test_generate_off_mesh_with_repeating_grid():
    rows = 2
    row_height = 3
    columns = 5
    column_width = 7
    # A square with a triangle on the side
    off_geometry = OFFGeometry(vertices=[Vector(0, 0, 0),
                                         Vector(0, 1, 0),
                                         Vector(1, 1, 0),
                                         Vector(1, 0, 0),
                                         Vector(1.5, 0.5, 0)],
                               faces=[[0, 1, 2, 3],
                                      [2, 3, 4]])
    qt_geometry = QtOFFGeometry(off_geometry, PixelGrid(rows=rows,
                                                        row_height=row_height,
                                                        columns=columns,
                                                        col_width=column_width))
    # rows of copies, 2 sides per shape, 3 triangles total, 3 points per triangle
    assert qt_geometry.vertex_count == rows * columns * 2 * 3 * 3

    vertex_data_bytes = eval(str(qt_geometry.attributes()[0].buffer().data()))
    vertex_data = list(struct.unpack('%sf' % (qt_geometry.vertex_count * 3), vertex_data_bytes))
    generated_triangles = [vertex_data[i:i + 9] for i in range(0, len(vertex_data), 9)]

    for i in range(rows):
        for j in range(columns):
            x_offset = j * column_width
            y_offset = i * row_height
            triangles = [[0+x_offset, 0+y_offset, 0,
                          0+x_offset, 1+y_offset, 0,
                          1+x_offset, 1+y_offset, 0],
                         [0+x_offset, 0+y_offset, 0,
                          1+x_offset, 1+y_offset, 0,
                          1+x_offset, 0+y_offset, 0],
                         [1+x_offset, 1+y_offset, 0,
                          1+x_offset, 0+y_offset, 0,
                          1.5+x_offset, 0.5+y_offset, 0]]
            # check the triangle and its inverted winding are present
            for triangle in triangles:
                assert triangle in generated_triangles
                assert triangle[0:3] + triangle[6:9] + triangle[3:6] in generated_triangles
