from nexus_constructor.qml_models.geometry_models import (
    NoShapeModel,
    NoShapeGeometry,
    OFFModel,
    OFFGeometry,
    CylinderModel,
    CylindricalGeometry,
    InstrumentModel,
)


def test_GIVEN_nothing_WHEN_creating_no_shape_model_THEN_geometry_is_no_shape_geometry():
    model = NoShapeModel()
    assert isinstance(model.get_geometry(), NoShapeGeometry)
    assert model.geometry.geometry_str == "None"


def test_GIVEN_nothing_WHEN_creating_OFF_model_THEN_geometry_is_OFF_geometry():
    model = OFFModel()
    assert isinstance(model.get_geometry(), OFFGeometry)
    assert model.geometry.geometry_str == "OFF"


def test_GIVEN_nothing_WHEN_creating_cylinder_model_THEN_geometry_is_cylindrical_geometry():
    model = CylinderModel()
    assert isinstance(model.get_geometry(), CylindricalGeometry)
    assert model.cylinder.geometry_str == "Cylinder"


def test_GIVEN_vector_WHEN_setting_cylinder_model_x_axis_THEN_geometry_is_updated():
    point = 4
    model = CylinderModel()
    model.set_axis_x(point)
    assert model.get_axis_x() == point


def test_GIVEN_file_name_WHEN_setting_file_in_OFF_model_THEN_file_name_qurl_is_created():
    file_name = "something"
    model = OFFModel()
    model.load_data = lambda: 1
    model.set_file(file_name)
    assert model.get_file() == file_name


def test_GIVEN_non_default_units_WHEN_setting_units_THEN_units_are_updated_correctly_in_model():
    units = "km"
    model = OFFModel()
    model.set_units(units)

    assert model.get_units() == units


def test_GIVEN_instrument_model_WHEN_setting_geometry_on_cylindricalmodel_THEN_instrument_model_contains_component_geometry():
    inst = InstrumentModel()

    model = CylinderModel()
    model.set_geometry(0, inst)

    assert inst.components[0].geometry == model.get_geometry()


def test_GIVEN_instrument_model_WHEN_setting_geometry_on_offmodel_THEN_instrument_model_contains_component_geometry():
    inst = InstrumentModel()

    model = OFFModel()
    model.set_geometry(0, inst)

    assert inst.components[0].geometry == model.get_geometry()
