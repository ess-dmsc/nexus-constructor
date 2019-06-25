from nexus_constructor.pixel_data import (
    PixelMapping,
    PixelGrid,
    SinglePixelId,
    CountDirection,
    Corner,
)
from nexus_constructor.component import Component
from nexus_constructor.geometry_loader import load_geometry_from_file_object
from nexus_constructor.transformations import Translation, Rotation
from nexus_constructor.geometry_types import CylindricalGeometry
from nexus_constructor.qml_models.geometry_models import OFFModel
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtGui import QVector3D
from io import StringIO


def build_sample_model():
    model = InstrumentModel()

    model.components[0].component_group = None

    offmodel = OFFModel()

    offmodel.set_units("m")

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

    load_geometry_from_file_object(
        StringIO(off_file), ".off", offmodel.units, offmodel.geometry
    )

    off_geometry = offmodel.get_geometry()

    model.components += [
        Component(
            component_type="Detector",
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
            component_type="Detector",
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
            component_type="Monitor",
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
            component_type="Source",
            name="Uranium chunk #742",
            description="A lump of radiation emitting material",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -20)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type="Slit",
            name="Slit One",
            description="A hole in a thing",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -5)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type="Moderator",
            name="My Moderator",
            description="Some sort of moderator I guess",
            transforms=[
                Rotation(name="rotate", axis=QVector3D(0, 1, 0), angle=0.0),
                Translation(name="translate", vector=QVector3D(0, 0, -17)),
            ],
            geometry=CylindricalGeometry(units="m"),
        ),
        Component(
            component_type="Disk Chopper",
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
