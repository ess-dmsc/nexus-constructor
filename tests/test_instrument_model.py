from nexus_constructor import data_model
from nexus_constructor.data_model import CylindricalGeometry
from nexus_constructor.off_renderer import QtOFFGeometry
from nexus_constructor.qml_models.geometry_models import (
    NoShapeModel,
    OFFModel,
    OFFGeometry,
)
from nexus_constructor.qml_models.instrument_model import (
    InstrumentModel,
    generate_mesh,
    determine_pixel_state,
    Component,
    ComponentType,
    PixelGrid,
    PixelMapping,
)
from PySide2.QtGui import QMatrix4x4, QVector3D


def test_initialise_model():
    model = InstrumentModel()
    assert model.rowCount() == 1
    assert model.components[0].component_type == data_model.ComponentType.SAMPLE


def test_add_component():
    model = InstrumentModel()
    model.add_component("Detector", "My Detector", geometry_model=NoShapeModel())
    assert model.rowCount() == 2
    assert model.components[1].component_type == data_model.ComponentType.DETECTOR
    assert model.components[1].name == "My Detector"


def test_remove_component():
    model = InstrumentModel()
    model.add_component("Detector", "My Detector", geometry_model=NoShapeModel())
    model.remove_component(1)
    assert model.rowCount() == 1
    assert not model.components[0].component_type == data_model.ComponentType.DETECTOR
    # The sample at index 0 shouldn't be removable
    model.remove_component(0)
    assert model.rowCount() == 1
    assert model.components[0].component_type == data_model.ComponentType.SAMPLE


def test_replace_contents():
    model = InstrumentModel()
    replacement_data = [
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name="Replacement sample"
        ),
        data_model.Component(
            component_type=data_model.ComponentType.DETECTOR,
            name="Replacement Detector",
            geometry=data_model.OFFGeometry(),
        ),
    ]
    model.replace_contents(replacement_data)
    assert model.rowCount() == 2
    assert model.components == replacement_data


def test_generate_component_name():
    model = InstrumentModel()
    model.components = [
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name="Sample"
        ),
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name="Detector"
        ),
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name="Detector3"
        ),
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name="Magnet2"
        ),
    ]
    assert model.generate_component_name("Sample") == "Sample1"
    assert model.generate_component_name("Detector") == "Detector4"
    assert model.generate_component_name("Magnet") == "Magnet"
    assert model.generate_component_name("BeamGuide") == "BeamGuide"


def test_is_removable():
    model = InstrumentModel()
    model.components = [
        data_model.Component(
            component_type=data_model.ComponentType.SAMPLE, name=str(i)
        )
        for i in range(4)
    ]
    model.components[0].transform_parent = model.components[0]
    model.components[1].transform_parent = model.components[0]
    model.components[2].transform_parent = model.components[1]
    model.components[3].transform_parent = model.components[3]

    assert not model.is_removable(0)
    assert not model.is_removable(1)
    assert model.is_removable(2)
    assert model.is_removable(3)


def test_determine_pixel_state_produces_expected_strings():
    for component_type in data_model.ComponentType:
        component = data_model.Component(component_type=component_type, name="")
        if component_type == data_model.ComponentType.DETECTOR:
            expected_states = ["Mapping", "Grid"]
            pixel_options = [data_model.PixelMapping([]), data_model.PixelGrid()]
        elif component_type == data_model.ComponentType.MONITOR:
            expected_states = ["SinglePixel"]
            pixel_options = [data_model.SinglePixelId(42)]
        else:
            expected_states = [""]
            pixel_options = [None]

        assert len(expected_states) == len(pixel_options)
        for i in range(len(pixel_options)):
            component.pixel_data = pixel_options[i]
            assert determine_pixel_state(component) == expected_states[i]


def build_model_with_sample_transforms():
    instrument = InstrumentModel()
    instrument.components.append(
        data_model.Component(
            component_type=data_model.ComponentType.DETECTOR,
            name="detector1",
            transform_parent=instrument.components[0],
            transforms=[
                data_model.Rotation(
                    name="rotate", axis=data_model.Vector(4, 5, 6), angle=90
                ),
                data_model.Translation(
                    name="translate", vector=data_model.Vector(1, 2, 3)
                ),
            ],
        )
    )
    instrument.components.append(
        data_model.Component(
            component_type=data_model.ComponentType.DETECTOR,
            name="detector2",
            transform_parent=instrument.components[1],
            dependent_transform=instrument.components[1].transforms[0],
            transforms=[
                data_model.Translation(
                    name="translate", vector=data_model.Vector(1, 2, 3)
                ),
                data_model.Rotation(
                    name="rotate", axis=data_model.Vector(4, 5, 6), angle=90
                ),
            ],
        )
    )
    instrument.components.append(
        data_model.Component(
            component_type=data_model.ComponentType.DETECTOR,
            name="detector3",
            transform_parent=instrument.components[1],
            transforms=[
                data_model.Rotation(
                    name="rotate", axis=data_model.Vector(4, 5, 6), angle=90
                ),
                data_model.Translation(
                    name="translate", vector=data_model.Vector(1, 2, 3)
                ),
                data_model.Translation(
                    name="translate2", vector=data_model.Vector(1, 2, 3)
                ),
            ],
        )
    )
    # Use replace_contents to build the required transform models
    instrument.replace_contents(instrument.components)
    return instrument


def test_generate_matrix_combines_dependent_transforms():
    instrument = build_model_with_sample_transforms()

    def rotate_matrix(matrix: QMatrix4x4, rotate: data_model.Rotation):
        matrix.rotate(
            rotate.angle, QVector3D(rotate.axis.x, rotate.axis.y, rotate.axis.z)
        )

    def translate_matrix(matrix: QMatrix4x4, translate: data_model.Translation):
        matrix.translate(translate.vector.x, translate.vector.y, translate.vector.z)

    target_matrix = QMatrix4x4()
    assert instrument.generate_matrix(instrument.components[0]) == target_matrix

    target_matrix = QMatrix4x4()
    rotate_matrix(target_matrix, instrument.components[1].transforms[0])
    translate_matrix(target_matrix, instrument.components[1].transforms[1])
    assert instrument.generate_matrix(instrument.components[1]) == target_matrix

    target_matrix = QMatrix4x4()
    rotate_matrix(target_matrix, instrument.components[1].transforms[0])
    translate_matrix(target_matrix, instrument.components[2].transforms[0])
    rotate_matrix(target_matrix, instrument.components[2].transforms[1])
    assert instrument.generate_matrix(instrument.components[2]) == target_matrix

    target_matrix = QMatrix4x4()
    rotate_matrix(target_matrix, instrument.components[1].transforms[0])
    translate_matrix(target_matrix, instrument.components[1].transforms[1])
    rotate_matrix(target_matrix, instrument.components[3].transforms[0])
    translate_matrix(target_matrix, instrument.components[3].transforms[1])
    translate_matrix(target_matrix, instrument.components[3].transforms[2])
    assert instrument.generate_matrix(instrument.components[3]) == target_matrix


def test_transforms_deletable_set():
    instrument = build_model_with_sample_transforms()

    assert instrument.transform_models[0].deletable == []
    assert instrument.transform_models[1].deletable == [False, True]
    assert instrument.transform_models[2].deletable == [True, True]
    assert instrument.transform_models[3].deletable == [True, True, True]


def test_GIVEN_no_geometry_WHEN_generating_mesh_THEN_square_off_mesh_is_created():
    component = NoShapeModel()
    actual_output = generate_mesh(component)

    assert actual_output.geometry().vertex_count == 36


def test_GIVEN_off_with_no_geometry_WHEN_generating_mesh_THEN_returns_nothing():
    component = OFFModel()
    component.geometry = False
    assert not generate_mesh(component)


def test_GIVEN_off_with_geometry_WHEN_generating_mesh_THEN_returns_off_mesh():
    component = Component(ComponentType.MONITOR, "")
    component.geometry = OFFGeometry()
    assert isinstance(generate_mesh(component).geometry(), QtOFFGeometry)


def test_GIVEN_component_with_cylinder_geometry_WHEN_generating_mesh_THEN_returns_off_mesh():
    component = Component(ComponentType.MONITOR, "")
    component.geometry = CylindricalGeometry()
    assert isinstance(generate_mesh(component).geometry(), QtOFFGeometry)


def test_GIVEN_component_with_detector_type_WHEN_generating_mesh_THEN_contains_pixel_data():
    component = Component(ComponentType.DETECTOR, "")
    ROWS = 2
    COLUMNS = 1

    component.pixel_data = PixelGrid(rows=2, columns=1)
    component.geometry = OFFGeometry(
        vertices=[QVector3D(0, 0, 0), QVector3D(0, 1, 0), QVector3D(1, 0, 0)],
        faces=[[0, 1, 2]],
    )
    generated = generate_mesh(component)
    assert isinstance(generated.geometry(), QtOFFGeometry)
    assert generated.vertexCount() == 3 * ROWS * COLUMNS


def test_GIVEN_none_WHEN_determine_pixel_state_THEN_returns_empty_string():
    component = Component(False, "")
    assert determine_pixel_state(component) == ""


def test_GIVEN_monitor_WHEN_determine_pixel_state_THEN_returns_SinglePixel():
    component = Component(ComponentType.MONITOR, "")
    assert determine_pixel_state(component) == "SinglePixel"


def test_GIVEN_detector_with_PixelGrid_WHEN_determine_pixel_state_THEN_returns_Grid():
    component = Component(ComponentType.DETECTOR, "")
    component.pixel_data = PixelGrid()
    assert determine_pixel_state(component) == "Grid"


def test_GIVEN_detector_with_PixelMapping_WHEN_determine_pixel_state_THEN_returns_Mapping():
    component = Component(ComponentType.DETECTOR, "")
    component.pixel_data = PixelMapping([])
    assert determine_pixel_state(component) == "Mapping"


def test_GIVEN_slit_WHEN_determine_pixel_state_THEN_returns_empty_string():
    component = Component(ComponentType.SLIT, "")
    assert determine_pixel_state(component) == ""
