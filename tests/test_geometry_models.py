from nexus_constructor.qml_models.geometry_models import (
    NoShapeModel,
    NoShapeGeometry,
    OFFModel,
    OFFGeometry,
    CylinderModel,
    CylindricalGeometry,
)


def test_GIVEN_nothing_WHEN_creating_no_shape_model_THEN_geometry_is_no_shape_geometry():
    model = NoShapeModel()
    assert isinstance(model.get_geometry(), NoShapeGeometry)
    assert model.rowCount() == 1


def test_GIVEN_nothing_WHEN_creating_OFF_model_THEN_geometry_is_OFF_geometry():
    model = OFFModel()
    geometry = model.get_geometry()
    assert isinstance(geometry, OFFGeometry)
    assert model.rowCount() == 1


def test_GIVEN_nothing_WHEN_creating_cylinder_model_THEN_geometry_is_cylindrical_geometry():
    model = CylinderModel()
    geometry = model.get_geometry()
    assert isinstance(geometry, CylindricalGeometry)
    assert model.rowCount() == 1
