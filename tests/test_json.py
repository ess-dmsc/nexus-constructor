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
)
from nexus_constructor.geometry_loader import load_geometry_from_file_object
from nexus_constructor.nexus_constructor_json import writer, loader
from nexus_constructor.transformations import Translation, Rotation
from nexus_constructor.geometry_types import CylindricalGeometry
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtGui import QVector3D
from io import StringIO


def build_sample_model():
    model = InstrumentModel()

    offmodel = OFFModel()
    offmodel.setData(1, "m", OFFModel.UnitsRole)

    off_file = (
        "OFF\n"
        "#  cube.off\n"
        "#  A cube\n"
        "8 6 0\n"
        "-0.500000 -0.500000 0.500000\n"
        "0.500000 -0.500000 0.500000\n"
        "-0.500000 0.500000 0.500000\n"
        "0.500000 0.500000 0.500000\n"
        "-0.500000 0.500000 -0.500000\n"
        "0.500000 0.500000 -0.500000\n"
        "-0.500000 -0.500000 -0.500000\n"
        "0.500000 -0.500000 -0.500000\n"
        "4 0 1 3 2\n"
        "4 2 3 5 4\n"
        "4 4 5 7 6\n"
        "4 6 7 1 0\n"
        "4 1 7 5 3\n"
        "4 6 0 2 4\n"
    )

    load_geometry_from_file_object(StringIO(off_file), ".off", offmodel.units, offmodel.geometry)


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

    json_string = writer.generate_json(model)

    loaded_model = InstrumentModel()
    loader.load_json_object_into_instrument_model(json.loads(json_string), loaded_model)

    assert model.components == loaded_model.components


def test_json_schema_compliance():

    file = """{
            "$schema": "http://json-schema.org/draft-04/schema#",
            "$id": "https://raw.githubusercontent.com/ess-dmsc/nexus-constructor/master/Instrument.schema.json",
            "title": "Instrument",
            "description": "An experimental setup of an instrument on a beamline, containing a sample and set of components based on the NeXus data format",
            "type": "object",
            "properties": {
                "components": {
                    "description": "The components that make up the instrument",
                    "type": "array",
                    "items": {
                        "oneOf": [
                            {"$ref": "#/definitions/sample"},
                            {"$ref": "#/definitions/detector"},
                            {"$ref": "#/definitions/monitor"},
                            {"$ref": "#/definitions/source"},
                            {"$ref": "#/definitions/slit"},
                            {"$ref": "#/definitions/moderator"},
                            {"$ref": "#/definitions/diskChopper"}
                        ]
                    }
                }
            },
            "required": ["components"],
            "definitions": {
                "3D": {
                    "description": "XYZ values representing a direction or point in 3D space",
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number"
                        },
                        "y": {
                            "type": "number"
                        },
                        "z": {
                            "type": "number"
                        }
                    },
                    "required": ["x", "y", "z"]
                },
                "component": {
                    "description": "A component in an instrument",
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "type": {
                            "type": "string"
                        },
                        "transform_id": {
                            "type": "integer"
                        },
                        "transform_parent_id": {
                            "type": "integer"
                        },
                        "parent_transform_index": {
                            "type": "integer"
                        },
                        "transforms": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/transform"
                            }
                        },
                        "geometry": {
                            "$ref": "#/definitions/geometry"
                        }
                    },
                    "required": ["name", "description", "type", "transform_id", "transforms"]
                },
                "sample": {
                    "description": "The sample in an instrument",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Sample"]
                        }
                    },
                    "required": ["type"]
                },
                "detector": {
                    "description": "Detector components of an instrument",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Detector"]
                        }
                    },
                    "oneOf": [
                        {"$ref": "#/definitions/pixelMappedDetectorProperties"},
                        {"$ref": "#/definitions/repeatedPixelDetectorProperties"}
                    ]
                },
                "monitor": {
                    "description": "Monitor components of an instrument",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Monitor"]
                        }
                    },
                    "oneOf": [
                        {"$ref": "#/definitions/singlePixelIdProperty"}
                    ]
                },
                "source": {
                    "description": "The neutron or x-ray storage ring/facility an instrument is connected to",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Source"]
                        }
                    }
                },
                "slit": {
                    "description": "A diffraction slit",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Slit"]
                        }
                    }
                },
                "moderator": {
                    "description": "A neutron moderator",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Moderator"]
                        }
                    }
                },
                "diskChopper": {
                    "description": "A disk chopper",
                    "allOf": [
                        {"$ref": "#/definitions/component"}
                    ],
                    "properties": {
                        "type": {
                            "enum": ["Disk Chopper"]
                        }
                    }
                },
                "pixelMappedDetectorProperties": {
                    "description": "Properties for a detector with a pixelmapping, meaning it must have an OFF geometry",
                    "properties": {
                        "geometry": {
                            "$ref": "#/definitions/offGeometry"
                        },
                        "pixel_mapping": {
                            "$ref": "#/definitions/pixelMapping"
                        }
                    },
                    "required": ["geometry", "pixel_mapping"]
                },
                "repeatedPixelDetectorProperties": {
                    "description": "Properties for a detector with a repeated pixel geometry. Unlike a pixel mapping, no further geometry restrictions are needed",
                    "properties": {
                        "pixel_grid": {
                            "$ref": "#/definitions/pixelGrid"
                        }
                    },
                    "required": ["pixel_grid"]
                },
                "singlePixelIdProperty": {
                    "description": "The pixel id for a monitor component",
                    "properties": {
                        "pixel_id": {
                            "type": "integer"
                        }
                    },
                    "required": ["pixel_id"]
                },
                "transform": {
                    "description": "A transformation to position an object in 3D space",
                    "oneOf": [
                        {"$ref": "#/definitions/rotate"},
                        {"$ref": "#/definitions/translate"}
                    ]
                },
                "rotate": {
                    "description": "A transformation in 3D space by rotating about an axis",
                    "properties": {
                        "type": {
                            "enum": ["rotate"]
                        },
                        "name": {
                            "type": "string"
                        },
                        "axis": {
                            "$ref": "#/definitions/3D"
                        },
                        "angle": {
                            "type": "object",
                            "properties": {
                                "unit": {
                                    "enum": ["degrees"]
                                },
                                "value": {
                                    "type": "number"
                                }
                            },
                            "required": ["unit", "value"]
                        }
                    },
                    "required": ["type", "axis", "angle"]
                },
                "translate": {
                    "description": "A transformation in 3D space by translating along a vector",
                    "properties": {
                        "type": {
                            "enum": ["translate"]
                        },
                        "name": {
                            "type": "string"
                        },
                        "vector": {
                            "$ref": "#/definitions/3D"
                        },
                        "unit": {
                            "enum": ["m"]
                        }
                    },
                    "required": ["type", "vector", "unit"]
                },
                "geometry": {
                    "description": "The 3D geometry of a component in the instrument",
                    "oneOf": [
                        {"$ref": "#/definitions/offGeometry"},
                        {"$ref": "#/definitions/cylindricalGeometry"}
                    ]
                },
                "offGeometry": {
                    "description": "A geometry of arbitrary polygons based on the NXoff_geometry class",
                    "type": "object",
                    "properties": {
                        "type": {
                            "enum": ["OFF"]
                        },
                        "vertices": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "minItems": 3,
                                "maxItems": 3,
                                "items": {
                                    "type": "number"
                                }
                            }
                        },
                        "winding_order": {
                            "type": "array",
                            "items": {
                                "type": "integer",
                                "minimum": 0
                            }
                        },
                        "faces": {
                            "type": "array",
                            "items": {
                                "type": "integer",
                                "minimum": 0
                            }
                        }
                    },
                    "required": ["type", "vertices", "winding_order", "faces"]
                },
                "cylindricalGeometry": {
                    "description": "A geometry to model a cylinder with center of its base at the origin of its local coordinate system",
                    "type": "object",
                    "properties": {
                        "type": {
                            "enum": ["Cylinder"]
                        },
                        "axis_direction": {
                            "$ref": "#/definitions/3D"
                        },
                        "height": {
                            "type": "number",
                            "minimum": 0,
                            "exclusiveMinimum": true
                        },
                        "radius": {
                            "type": "number",
                            "minimum": 0,
                            "exclusiveMinimum": true
                        },
                        "base_center": {
                            "$ref": "#/definitions/3D"
                        },
                        "base_edge": {
                            "$ref": "#/definitions/3D"
                        },
                        "top_center": {
                            "$ref": "#/definitions/3D"
                        }
                    },
                    "required": ["type", "axis_direction", "height", "radius", "base_center", "base_edge", "top_center"]
                },
                "pixelGrid": {
                    "description": "A regular grid of pixels, starting in the bottom left corner, which is the local coordinate origin",
                    "type": "object",
                    "properties": {
                        "rows": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "columns": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "row_height": {
                            "type": "number"
                        },
                        "column_width": {
                            "type": "number"
                        },
                        "first_id": {
                            "type": "integer"
                        },
                        "count_direction": {
                            "$ref": "#/definitions/countDirection"
                        },
                        "starting_corner": {
                            "$ref": "#/definitions/corner"
                        }
                    },
                    "required": ["rows", "columns", "row_height", "column_width", "first_id", "count_direction",
                                 "starting_corner"]
                },
                "pixelMapping": {
                    "description": "A mapping of off geometry face numbers to detector id's, mirroring the detector_faces property of the NXoff_geometry class",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "face": {
                                "type": "integer",
                                "minimum": 0
                            },
                            "pixel_id": {
                                "type": "integer"
                            }
                        },
                        "required": ["face", "pixel_id"]
                    }
                },
                "countDirection": {
                    "description": "The direction a pixelGrid should increment its detector ID's along first",
                    "enum": ["ROW", "COLUMN"]
                },
                "corner": {
                    "description": "A corner of a 2D grid",
                    "enum": ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]
                }
            }
        }"""

    schema = json.load(StringIO(file))

    model = build_sample_model()
    model_json = writer.generate_json(model)
    model_data = json.loads(model_json)

    jsonschema.validate(model_data, schema)
