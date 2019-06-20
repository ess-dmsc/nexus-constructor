from nexus_constructor.qml_models.geometry_models import NoShapeModel
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
    inst = InstrumentModel()
    model = PixelGridModel()
    inst.add_component(
        "Detector", "test", pixel_model=model, geometry_model=NoShapeModel()
    )
    inst.components[-1].pixel_data = pixel_data
    model.set_pixel_model(len(inst.components) - 1, inst)

    assert pixel_data == model.get_pixel_model()


def test_GIVEN_single_pixel_id_WHEN_setting_model_THEN_model_is_replaced():
    pixel_data = SinglePixelId(5)
    inst = InstrumentModel()
    model = SinglePixelModel()

    inst.add_component(
        "Detector", "test", pixel_model=model, geometry_model=NoShapeModel()
    )
    inst.components[-1].pixel_data = pixel_data
    model.set_pixel_model(len(inst.components) - 1, inst)

    assert pixel_data == model.get_pixel_model()


def test_GIVEN_columns_WHEN_setting_pixel_data_columns_in_pixelgridmodel_THEN_model_is_updated():
    model = PixelGridModel()
    num_of_columns = 5
    model.set_columns(num_of_columns)
    assert model.get_columns() == num_of_columns


def test_GIVEN_pixel_object_WHEN_setting_pixel_model_on_mapping_model_THEN_model_is_updated_with_new_object():
    pixel_data = PixelMapping([1])
    inst = InstrumentModel()
    model = PixelMappingModel()
    inst.add_component(
        "Detector", "test", pixel_model=model, geometry_model=NoShapeModel()
    )

    inst.components[-1].pixel_data = pixel_data

    model.set_pixel_model(len(inst.components) - 1, inst)

    assert model.get_pixel_model() == pixel_data


def test_GIVEN_same_pixelid_WHEN_setting_data_on_pixelMappingModel_THEN_returns_changed_as_false():
    inst = InstrumentModel()
    model = PixelMappingModel()
    inst.add_component(
        "Detector", "test", pixel_model=model, geometry_model=NoShapeModel()
    )
    component_index = len(inst.components) - 1
    id = 1
    pixel_data = PixelMapping([id])
    inst.components[component_index].pixel_data = pixel_data
    model.set_pixel_model(component_index, inst)

    assert not model.setData(inst.index(component_index), id, model.PixelIdRole)


def test_GIVEN_different_pixelid_WHEN_setting_data_on_pixelMappingModel_THEN_model_is_updated():
    original_id = 0
    pixel_data = PixelMapping([original_id])
    inst = InstrumentModel()
    model = PixelMappingModel()
    inst.add_component(
        "Detector", "test", pixel_model=model, geometry_model=NoShapeModel()
    )
    component_index = len(inst.components) - 1
    inst.components[component_index].pixel_data = pixel_data
    model.set_pixel_model(component_index, inst)

    changed_id = 1
    assert model.setData(inst.index(component_index), changed_id, model.PixelIdRole)
    assert model.data(inst.index(component_index), model.PixelIdRole) == changed_id
