import json
import jsonschema
from nexus_constructor.data_model import (
    Component,
    ComponentType,
    CylindricalGeometry,
    PixelMapping,
    PixelGrid,
    SinglePixelId,
    Vector,
    CountDirection,
    Corner,
    Translation,
    Rotation,
)
import nexus_constructor.nexus_constructor_json as gc_json
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import QUrl


def build_sample_model():
    model = InstrumentModel()

    offmodel = OFFModel()
    offmodel.setData(1, "m", OFFModel.UnitsRole)
    offmodel.setData(0, QUrl("tests/cube.off"), OFFModel.FileNameRole)
    off_geometry = offmodel.get_geometry()

    model.components += [
        Component(
            component_type=ComponentType.DETECTOR,
            name="Detector 1",
            description="Pixel mapped cube",
            transforms=[
                Rotation(name="rotate1", axis=Vector(1, 2, 0), angle=45),
                Translation(name="translate1", vector=Vector(3, 7, 5)),
            ],
            geometry=off_geometry,
            pixel_data=PixelMapping(pixel_ids=[1, 2, None, 3, None, 5]),
        ),
        Component(
            component_type=ComponentType.DETECTOR,
            name="Detector 2",
            description="Cylinder array",
            transforms=[
                Rotation(name="rotate2", axis=Vector(0.7, 0.7, 0.7), angle=63.4),
                Translation(name="translate2", vector=Vector(-1.3, 0.1, -3.14)),
            ],
            geometry=CylindricalGeometry(
                units="m", axis_direction=Vector(2, 2, 1), height=0.7, radius=0.1
            ),
            pixel_data=PixelGrid(
                rows=3,
                columns=5,
                row_height=0.5,
                col_width=0.4,
                first_id=10,
                count_direction=CountDirection.ROW,
                initial_count_corner=Corner.TOP_LEFT,
            ),
        ),
        Component(
            component_type=ComponentType.MONITOR,
            name="Monitor Alpha",
            description="A geometry-less monitor",
            transforms=[
                Rotation(name="rotate3", axis=Vector(-1, 0, -1.5), angle=0.0),
                Translation(name="translate3", vector=Vector(1, 2, 3)),
            ],
            geometry=CylindricalGeometry(units="m"),
            pixel_data=SinglePixelId(42),
        ),
        Component(
            component_type=ComponentType.SOURCE,
            name="Uranium chunk #742",
            description="A lump of radiation emitting material",
            transforms=[
                Rotation(name="rotate4", axis=Vector(0, 1, 0), angle=0.0),
                Translation(name="translate4", vector=Vector(0, 0, -20)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.SLIT,
            name="Slit One",
            description="A hole in a thing",
            transforms=[
                Rotation(name="rotate5", axis=Vector(0, 1, 0), angle=0.0),
                Translation(name="translate5", vector=Vector(0, 0, -5)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.MODERATOR,
            name="My Moderator",
            description="Some sort of moderator I guess",
            transforms=[
                Rotation(name="rotate6", axis=Vector(0, 1, 0), angle=0.0),
                Translation(name="translate6", vector=Vector(0, 0, -17)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.DISK_CHOPPER,
            name="Spinny thing",
            description="A spinning disk with some holes in it",
            transforms=[
                Rotation(name="rotate7", axis=Vector(0, 1, 0), angle=0.0),
                Translation(name="translate7a", vector=Vector(0, 0, -10)),
                Translation(name="translate7b", vector=Vector(0, 0, -10)),
            ],
            geometry=CylindricalGeometry(
                axis_direction=Vector(0, 0, 1), height=0.3, radius=1.5, units="m"
            ),
        ),
    ]
    # set transform parents
    model.components[0].transform_parent = None
    model.components[1].transform_parent = model.components[0]
    model.components[2].transform_parent = model.components[1]
    model.components[3].transform_parent = model.components[2]

    model.components[2].dependent_transform = model.components[1].transforms[0]
    model.components[3].dependent_transform = model.components[2].transforms[1]

    return model


def test_loading_generated_json():
    model = build_sample_model()

    assert model.components == model.components

    json_string = gc_json.generate_json(model)

    loaded_model = InstrumentModel()
    gc_json.load_json_object_into_instrument_model(
        json.loads(json_string), loaded_model
    )

    assert model.components == loaded_model.components


def test_json_schema_compliance():
    with open("Instrument.schema.json") as file:
        schema = json.load(file)

    model = build_sample_model()
    model_json = gc_json.generate_json(model)
    model_data = json.loads(model_json)

    jsonschema.validate(model_data, schema)
