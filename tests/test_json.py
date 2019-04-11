import json
import jsonschema
from nexus_constructor.data_model import (
    Component,
    ComponentType,
    PixelMapping,
    PixelGrid,
    SinglePixelId,
    CountDirection,
    Corner,
    Translation,
    Rotation,
)
from nexus_constructor.geometry_types import CylindricalGeometry
import nexus_constructor.nexus_constructor_json as gc_json
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import QUrl
from PySide2.QtGui import QVector3D
from io import StringIO


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
                Rotation(name="rotate", axis=QVector3D(1, 2, 0), angle=45),
                Translation(name="translate", vector=QVector3D(3, 7, 5)),
            ],
            geometry=off_geometry,
            pixel_data=PixelMapping(pixel_ids=[1, 2, None, 3, None, 5]),
        ),
        Component(
            component_type=ComponentType.DETECTOR,
            name="Detector 2",
            description="Cylinder array",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0.7, 0.7, 0.7), angle=63.4),
                Translation(name="translate", vector=QVector3D(-1.3, 0.1, -3.14)),
            ],
            geometry=CylindricalGeometry(
                units="m", axis_direction=QVector3D(2, 2, 1), height=0.7, radius=0.1
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
                Rotation(name="rotate", axis=QVector3D(-1, 0, -1.5), angle=0.0),
                Translation(name="translate", vector=QVector3D(1, 2, 3)),
            ],
            geometry=CylindricalGeometry(units="m"),
            pixel_data=SinglePixelId(42),
        ),
        Component(
            component_type=ComponentType.SOURCE,
            name="Uranium chunk #742",
            description="A lump of radiation emitting material",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -20)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.SLIT,
            name="Slit One",
            description="A hole in a thing",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -5)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.MODERATOR,
            name="My Moderator",
            description="Some sort of moderator I guess",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -17)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type=ComponentType.DISK_CHOPPER,
            name="Spinny thing",
            description="A spinning disk with some holes in it",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -10)),
                Translation(name="translate2", vector=QVector3D(0, 0, -10)),
            ],
            geometry=CylindricalGeometry(
                axis_direction=QVector3D(0, 0, 1), height=0.3, radius=1.5, units="m"
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

    file = (
        "{\n"
        '"$schema": "http://json-schema.org/draft-04/schema#",\n'
        '"$id": "https://raw.githubusercontent.com/ess-dmsc/nexus-constructor/master/Instrument.schema.json",\n'
        '"title": "Instrument",\n'
        '"description": "An experimental setup of an instrument on a beamline, containing a sample and set of components based on the NeXus data format",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"components": {\n'
        '"description": "The components that make up the instrument",\n'
        '"type": "array",\n'
        '"items": {\n'
        '"oneOf": [\n'
        '{"$ref": "#/definitions/sample"},\n'
        '{"$ref": "#/definitions/detector"},\n'
        '{"$ref": "#/definitions/monitor"},\n'
        '{"$ref": "#/definitions/source"},\n'
        '{"$ref": "#/definitions/slit"},\n'
        '{"$ref": "#/definitions/moderator"},\n'
        '{"$ref": "#/definitions/diskChopper"}\n'
        "]\n"
        "}\n"
        "}\n"
        "},\n"
        '"required": ["components"],\n'
        '"definitions": {\n'
        '"3D": {\n'
        '"description": "XYZ values representing a direction or point in 3D space",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"x": {\n'
        '"type": "number"\n'
        "},\n"
        '"y": {\n'
        '"type": "number"\n'
        "},\n"
        '"z": {\n'
        '"type": "number"\n'
        "}\n"
        "},\n"
        '"required": ["x", "y", "z"]\n'
        "},\n"
        '"component": {\n'
        '"description": "A component in an instrument",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"name": {\n'
        '"type": "string"\n'
        "},\n"
        '"description": {\n'
        '"type": "string"\n'
        "},\n"
        '"type": {\n'
        '"type": "string"\n'
        "},\n"
        '"transform_id": {\n'
        '"type": "integer"\n'
        "},\n"
        '"transform_parent_id": {\n'
        '"type": "integer"\n'
        "},\n"
        '"parent_transform_index": {\n'
        '"type": "integer"\n'
        "},\n"
        '"transforms": {\n'
        '"type": "array",\n'
        '"items": {\n'
        '"$ref": "#/definitions/transform"\n'
        "}\n"
        "},\n"
        '"geometry": {\n'
        '"$ref": "#/definitions/geometry"\n'
        "}\n"
        "},\n"
        '"required": ["name", "description", "type", "transform_id", "transforms"]\n'
        "},\n"
        '"sample": {\n'
        '"description": "The sample in an instrument",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Sample"]\n'
        "}\n"
        "},\n"
        '"required": ["type"]\n'
        "},\n"
        '"detector": {\n'
        '"description": "Detector components of an instrument",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Detector"]\n'
        "}\n"
        "},\n"
        '"oneOf": [\n'
        '{"$ref": "#/definitions/pixelMappedDetectorProperties"},\n'
        '{"$ref": "#/definitions/repeatedPixelDetectorProperties"}\n'
        "]\n"
        "},\n"
        '"monitor": {\n'
        '"description": "Monitor components of an instrument",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Monitor"]\n'
        "}\n"
        "},\n"
        '"oneOf": [\n'
        '{"$ref": "#/definitions/singlePixelIdProperty"}\n'
        "]\n"
        "},\n"
        '"source": {\n'
        '"description": "The neutron or x-ray storage ring/facility an instrument is connected to",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Source"]\n'
        "}\n"
        "}\n"
        "},\n"
        '"slit": {\n'
        '"description": "A diffraction slit",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Slit"]\n'
        "}\n"
        "}\n"
        "},\n"
        '"moderator": {\n'
        '"description": "A neutron moderator",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Moderator"]\n'
        "}\n"
        "}\n"
        "},\n"
        '"diskChopper": {\n'
        '"description": "A disk chopper",\n'
        '"allOf": [\n'
        '{"$ref": "#/definitions/component"}\n'
        "],\n"
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Disk Chopper"]\n'
        "}\n"
        "}\n"
        "},\n"
        '"pixelMappedDetectorProperties": {\n'
        '"description": "Properties for a detector with a pixelmapping, meaning it must have an OFF geometry",\n'
        '"properties": {\n'
        '"geometry": {\n'
        '"$ref": "#/definitions/offGeometry"\n'
        "},\n"
        '"pixel_mapping": {\n'
        '"$ref": "#/definitions/pixelMapping"\n'
        "}\n"
        "},\n"
        '"required": ["geometry", "pixel_mapping"]\n'
        "},\n"
        '"repeatedPixelDetectorProperties": {\n'
        '"description": "Properties for a detector with a repeated pixel geometry. Unlike a pixel mapping, no further geometry restrictions are needed",\n'
        '"properties": {\n'
        '"pixel_grid": {\n'
        '"$ref": "#/definitions/pixelGrid"\n'
        "}\n"
        "},\n"
        '"required": ["pixel_grid"]\n'
        "},\n"
        '"singlePixelIdProperty": {\n'
        '"description": "The pixel id for a monitor component",\n'
        '"properties": {\n'
        '"pixel_id": {\n'
        '"type": "integer"\n'
        "}\n"
        "},\n"
        '"required": ["pixel_id"]\n'
        "},\n"
        '"transform": {\n'
        '"description": "A transformation to position an object in 3D space",\n'
        '"oneOf": [\n'
        '{"$ref": "#/definitions/rotate"},\n'
        '{"$ref": "#/definitions/translate"}\n'
        "]\n"
        "},\n"
        '"rotate": {\n'
        '"description": "A transformation in 3D space by rotating about an axis",\n'
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["rotate"]\n'
        "},\n"
        '"name": {\n'
        '"type": "string"\n'
        "},\n"
        '"axis": {\n'
        '"$ref": "#/definitions/3D"\n'
        "},\n"
        '"angle": {\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"unit": {\n'
        '"enum": ["degrees"]\n'
        "},\n"
        '"value": {\n'
        '"type": "number"\n'
        "}\n"
        "},\n"
        '"required": ["unit", "value"]\n'
        "}\n"
        "},\n"
        '"required": ["type", "axis", "angle"]\n'
        "},\n"
        '"translate": {\n'
        '"description": "A transformation in 3D space by translating along a vector",\n'
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["translate"]\n'
        "},\n"
        '"name": {\n'
        '"type": "string"\n'
        "},\n"
        '"vector": {\n'
        '"$ref": "#/definitions/3D"\n'
        "},\n"
        '"unit": {\n'
        '"enum": ["m"]\n'
        "}\n"
        "},\n"
        '"required": ["type", "vector", "unit"]\n'
        "},\n"
        '"geometry": {\n'
        '"description": "The 3D geometry of a component in the instrument",\n'
        '"oneOf": [\n'
        '{"$ref": "#/definitions/offGeometry"},\n'
        '{"$ref": "#/definitions/cylindricalGeometry"}\n'
        "]\n"
        "},\n"
        '"offGeometry": {\n'
        '"description": "A geometry of arbitrary polygons based on the NXoff_geometry class",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["OFF"]\n'
        "},\n"
        '"vertices": {\n'
        '"type": "array",\n'
        '"items": {\n'
        '"type": "array",\n'
        '"minItems": 3,\n'
        '"maxItems": 3,\n'
        '"items": {\n'
        '"type": "number"\n'
        "}\n"
        "}\n"
        "},\n"
        '"winding_order": {\n'
        '"type": "array",\n'
        '"items": {\n'
        '"type": "integer",\n'
        '"minimum": 0\n'
        "}\n"
        "},\n"
        '"faces": {\n'
        '"type": "array",\n'
        '"items": {\n'
        '"type": "integer",\n'
        '"minimum": 0\n'
        "}\n"
        "}\n"
        "},\n"
        '"required": ["type", "vertices", "winding_order", "faces"]\n'
        "},\n"
        '"cylindricalGeometry": {\n'
        '"description": "A geometry to model a cylinder with center of its base at the origin of its local coordinate system",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"type": {\n'
        '"enum": ["Cylinder"]\n'
        "},\n"
        '"axis_direction": {\n'
        '"$ref": "#/definitions/3D"\n'
        "},\n"
        '"height": {\n'
        '"type": "number",\n'
        '"minimum": 0,\n'
        '"exclusiveMinimum": true\n'
        "},\n"
        '"radius": {\n'
        '"type": "number",\n'
        '"minimum": 0,\n'
        '"exclusiveMinimum": true\n'
        "},\n"
        '"base_center": {\n'
        '"$ref": "#/definitions/3D"\n'
        "},\n"
        '"base_edge": {\n'
        '"$ref": "#/definitions/3D"\n'
        "},\n"
        '"top_center": {\n'
        '"$ref": "#/definitions/3D"\n'
        "}\n"
        "},\n"
        '"required": ["type", "axis_direction", "height", "radius", "base_center", "base_edge", "top_center"]\n'
        "},\n"
        '"pixelGrid": {\n'
        '"description": "A regular grid of pixels, starting in the bottom left corner, which is the local coordinate origin",\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"rows": {\n'
        '"type": "integer",\n'
        '"minimum": 1\n'
        "},\n"
        '"columns": {\n'
        '"type": "integer",\n'
        '"minimum": 1\n'
        "},\n"
        '"row_height": {\n'
        '"type": "number"\n'
        "},\n"
        '"column_width": {\n'
        '"type": "number"\n'
        "},\n"
        '"first_id": {\n'
        '"type": "integer"\n'
        "},\n"
        '"count_direction": {\n'
        '"$ref": "#/definitions/countDirection"\n'
        "},\n"
        '"starting_corner": {\n'
        '"$ref": "#/definitions/corner"\n'
        "}\n"
        "},\n"
        '"required": ["rows", "columns", "row_height", "column_width", "first_id", "count_direction",\n'
        '"starting_corner"]\n'
        "},\n"
        '"pixelMapping": {\n'
        '"description": "A mapping of off geometry face numbers to detector ids, mirroring the detector_faces property of the NXoff_geometry class",\n'
        '"type": "array",\n'
        '"items": {\n'
        '"type": "object",\n'
        '"properties": {\n'
        '"face": {\n'
        '"type": "integer",\n'
        '"minimum": 0\n'
        "},\n"
        '"pixel_id": {\n'
        '"type": "integer"\n'
        "}\n"
        "},\n"
        '"required": ["face", "pixel_id"]\n'
        "}\n"
        "},\n"
        '"countDirection": {\n'
        '"description": "The direction a pixelGrid should increment its detector IDs along first",\n'
        '"enum": ["ROW", "COLUMN"]\n'
        "},\n"
        '"corner": {\n'
        '"description": "A corner of a 2D grid",\n'
        '"enum": ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]\n'
        "}\n"
        "}\n"
        "}\n"
    )

    schema = json.load(StringIO(file))

    model = build_sample_model()
    model_json = gc_json.generate_json(model)
    model_data = json.loads(model_json)

    jsonschema.validate(model_data, schema)
