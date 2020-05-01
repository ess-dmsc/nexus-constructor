from nexus_constructor.geometry import NoShapeGeometry
from nexus_constructor.geometry.no_shape_geometry import OFFCube


def test_GIVEN_nothing_WHEN_constructing_NoShapeGeometry_THEN_off_geometry_returns_an_OFFCube():
    geom = NoShapeGeometry()
    assert geom.off_geometry == OFFCube
