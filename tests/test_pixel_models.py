from nexus_constructor.qml_models.pixel_models import (
    PixelGridModel,
    PixelMappingModel,
    PixelMapping,
    SinglePixelModel,
    SinglePixelId,
    InstrumentModel,
    PixelGrid,
)


def test_GIVEN_nothing_WHEN_creating_single_pixel_model_THEN_pixel_id_is_zero():
    model = SinglePixelModel()
    assert model.get_pixel_id() == 0


def test_GIVEN_pixel_id_WHEN_creating_single_pixel_model_THEN_pixel_id_is_set_in_model():
    custom_id = 5
    model = SinglePixelModel()
    model.set_pixel_id(custom_id)
    assert model.get_pixel_id() == custom_id


def test_GIVEN_pixel_model_WHEN_creating_pixelgridmodel_THEN_model_is_updated():
    pixel_data = PixelGrid(rows=5)
    model = PixelGridModel()
    inst = InstrumentModel()
    inst.components[0].pixel_data = pixel_data
    model.set_pixel_model(0, inst)

    assert pixel_data == model.get_pixel_model()


def test_GIVEN_another_pixel_id_object_WHEN_setting_model_THEN_model_is_replaced():
    pixel_data = SinglePixelId(5)
    model = SinglePixelModel()
    inst = InstrumentModel()
    inst.components[0].pixel_data = pixel_data
    model.set_pixel_model(0, inst)

    assert pixel_data == model.get_pixel_model()


def test_GIVEN_columns_WHEN_setting_pixel_data_columns_in_pixelgridmodel_THEN_model_is_updated():
    model = PixelGridModel()
    num_of_columns = 5
    model.set_columns(num_of_columns)
    assert model.get_columns() == num_of_columns


def test_GIVEN_pixel_object_WHEN_setting_pixel_model_on_mapping_model_THEN_model_is_updated_with_new_object():
    pixel_data = PixelMapping([1])
    inst = InstrumentModel()
    inst.components[0].pixel_data = pixel_data
    model = PixelMappingModel()

    model.set_pixel_model(0, inst)

    assert model.get_pixel_model() == pixel_data


def test_GIVEN_nothing_WHEN_creating_PixelMappingModel_THEN_pixeldata_type_is_mapping():
    model = PixelMappingModel()
    assert model.get_pixel_model().type == "PixelMapping"


def test_GIVEN_nothing_WHEN_creating_SinglePixelModel_THEN_pixeldata_type_is_single_pixel():
    model = SinglePixelModel()
    assert model.get_pixel_model().type == "SinglePixel"


def test_GIVEN_nothing_WHEN_creating_PixelGridModel_THEN_pixeldata_type_is_pixel_grid():
    model = PixelGridModel()
    assert model.get_pixel_model().type == "PixelGrid"


def test_GIVEN_same_pixelid_WHEN_setting_data_on_pixelMappingModel_THEN_returns_changed_as_false():
    id = 1
    component_index = 0
    pixel_data = PixelMapping([id])
    inst = InstrumentModel()
    inst.components[component_index].pixel_data = pixel_data
    model = PixelMappingModel()
    model.set_pixel_model(component_index, inst)

    assert not model.setData(inst.index(component_index), id, model.PixelIdRole)


def test_GIVEN_different_pixelid_WHEN_setting_data_on_pixelMappingModel_THEN_model_is_updated():
    component_index = 0
    original_id = 0
    pixel_data = PixelMapping([original_id])
    inst = InstrumentModel()
    inst.components[component_index].pixel_data = pixel_data
    model = PixelMappingModel()
    model.set_pixel_model(component_index, inst)

    changed_id = 1

    assert model.setData(inst.index(component_index), changed_id, model.PixelIdRole)

    assert model.data(inst.index(component_index), model.PixelIdRole) == changed_id
