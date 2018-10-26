from geometry_constructor.geometry_models import OFFModel
from geometry_constructor.data_model import Vector
from PySide2.QtCore import QUrl

def test_load_off_cube():
    model = OFFModel()
    model.setData(0, QUrl('tests/cube.off'), OFFModel.FileNameRole)
    off_geometry = model.get_geometry()
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
