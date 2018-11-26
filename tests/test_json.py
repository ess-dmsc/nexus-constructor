import json
import jsonschema
from geometry_constructor.data_model import Component, ComponentType, CylindricalGeometry, PixelMapping, PixelGrid,\
    SinglePixelId, Vector, CountDirection, Corner
from geometry_constructor.geometry_models import OFFModel
from geometry_constructor.instrument_model import InstrumentModel
from geometry_constructor.json_writer import JsonWriter
from geometry_constructor.json_loader import JsonLoader
from PySide2.QtCore import QUrl


def build_sample_model():
    model = InstrumentModel()

    offmodel = OFFModel()
    offmodel.setData(0, QUrl('tests/cube.off'), OFFModel.FileNameRole)
    off_geometry = offmodel.get_geometry()

    model.components += [
        Component(component_type=ComponentType.DETECTOR,
                  name='Detector 1',
                  description='Pixel mapped cube',
                  translate_vector=Vector(3, 7, 5),
                  rotate_axis=Vector(1, 2, 0),
                  rotate_angle=45,
                  geometry=off_geometry,
                  pixel_data=PixelMapping(pixel_ids=[1, 2, None, 3, None, 5])),
        Component(component_type=ComponentType.DETECTOR,
                  name='Detector 2',
                  description='Cylinder array',
                  translate_vector=Vector(-1.3, 0.1, -3.14),
                  rotate_axis=Vector(0.7, 0.7, 0.7),
                  rotate_angle=63.4,
                  geometry=CylindricalGeometry(axis_direction=Vector(2, 2, 1),
                                               height=0.7,
                                               radius=0.1),
                  pixel_data=PixelGrid(rows=3, columns=5,
                                       row_height=0.5, col_width=0.4,
                                       first_id=10,
                                       count_direction=CountDirection.ROW,
                                       initial_count_corner=Corner.TOP_LEFT)),
        Component(component_type=ComponentType.MONITOR,
                  name='Monitor Alpha',
                  description='A geometry-less monitor',
                  translate_vector=Vector(1, 2, 3),
                  rotate_axis=Vector(-1, 0, -1.5),
                  rotate_angle=0.0,
                  geometry=CylindricalGeometry(),
                  pixel_data=SinglePixelId(42)),
    ]
    # set transform parents
    model.components[0].transform_parent = None
    model.components[1].transform_parent = model.components[0]
    model.components[2].transform_parent = model.components[1]

    return model


def test_loading_generated_json():
    model = build_sample_model()

    assert model.components == model.components

    json = JsonWriter().generate_json(model)

    loaded_model = InstrumentModel()
    JsonLoader().load_json_into_instrument_model(json, loaded_model)

    assert model.components == loaded_model.components


def test_json_schema_compliance():
    with open('Instrument.schema.json') as file:
        schema = json.load(file)

    model = build_sample_model()
    model_json = JsonWriter().generate_json(model)
    model_data = json.loads(model_json)

    jsonschema.validate(model_data, schema)
