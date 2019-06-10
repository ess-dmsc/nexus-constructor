from nexus_constructor.geometry_types import CylindricalGeometry
from nexus_constructor.off_renderer import QtOFFGeometry
from nexus_constructor.qml_models.geometry_models import (
    NoShapeModel,
    NoShapeGeometry,
    OFFGeometry,
)
from nexus_constructor.transformations import Translation, Rotation
from nexus_constructor.qml_models.instrument_model import (
    InstrumentModel,
    generate_mesh,
    determine_pixel_state,
    Component,
    change_value,
)
from nexus_constructor.pixel_data import PixelMapping, PixelGrid
from PySide2.QtGui import QMatrix4x4, QVector3D


def test_GIVEN_different_attribute_WHEN_change_value_called_THEN_changes_attribute_to_new_value():
    item = Component("Sample", name="test")
    change_value(item, "name", "hello")
    assert item.name == "hello"


def test_GIVEN_same_value_WHEN_change_value_called_THEN_does_not_change_attribute():
    item = Component("Sample", name="test")
    change_value(item, "name", "test")
    assert item.name == "test"


def test_GIVEN_nonexistent_attr_WHEN_change_value_called_THEN_does_nothing():
    item = Component("Sample", name="test")
    attribute_that_shouldnt_exist = "somethingthatdoesntexist"
    change_value(item, attribute_that_shouldnt_exist, "test")
    try:
        getattr(item, attribute_that_shouldnt_exist)
        assert False
    except AttributeError:
        assert True


def test_GIVEN_nothing_WHEN_initialising_model_THEN_sample_exists_as_first_component():
    model = InstrumentModel()
    assert model.rowCount() == 1
    assert model.components[0].nx_class == "NXsample"


def test_add_component():
    model = InstrumentModel()
    model.add_component("NXdetector", "MyDetector", geometry_model=NoShapeModel())
    assert model.rowCount() == 2
    assert model.components[1].nx_class == "NXdetector"
    assert model.components[1].name == "MyDetector"


def test_remove_component():
    model = InstrumentModel()
    model.add_component("Detector", "My Detector", geometry_model=NoShapeModel())
    model.remove_component(len(model.components) - 1)
    assert model.rowCount() == 1
    assert not model.components[0].nx_class == "Detector"


def test_replace_contents():
    model = InstrumentModel()
    replacement_data = [
        Component(nx_class="Sample", name="Replacement sample"),
        Component(
            nx_class="Sample", name="Replacement Detector", geometry=CylindricalGeometry
        ),
    ]
    model.replace_contents(replacement_data)
    assert model.rowCount() == 2
    assert model.components == replacement_data


def test_generate_component_name():
    model = InstrumentModel()
    model.components = [
        Component(nx_class="Sample", name="Sample"),
        Component(nx_class="Sample", name="Detector"),
        Component(nx_class="Sample", name="Detector3"),
        Component(nx_class="Sample", name="Magnet2"),
    ]
    assert model.generate_component_name("Sample") == "Sample1"
    assert model.generate_component_name("Detector") == "Detector4"
    assert model.generate_component_name("Magnet") == "Magnet"
    assert model.generate_component_name("BeamGuide") == "BeamGuide"


def test_is_removable():
    model = InstrumentModel()
    model.components = [Component(nx_class="Sample", name=str(i)) for i in range(4)]
    model.components[0].transform_parent = model.components[0]
    model.components[1].transform_parent = model.components[0]
    model.components[2].transform_parent = model.components[1]
    model.components[3].transform_parent = model.components[3]

    assert not model.is_removable(0)
    assert not model.is_removable(1)
    assert model.is_removable(2)
    assert model.is_removable(3)


def build_model_with_sample_transforms():
    instrument = InstrumentModel()
    instrument.components.append(
        Component(
            nx_class="Detector",
            name="detector1",
            transform_parent=instrument.components[0],
            transforms=[
                Rotation(name="rotate", axis=QVector3D(4, 5, 6), angle=90),
                Translation(name="translate", vector=QVector3D(1, 2, 3)),
            ],
        )
    )
    instrument.components.append(
        Component(
            nx_class="Detector",
            name="detector2",
            transform_parent=instrument.components[1],
            dependent_transform=instrument.components[1].transforms[0],
            transforms=[
                Translation(name="translate", vector=QVector3D(1, 2, 3)),
                Rotation(name="rotate", axis=QVector3D(4, 5, 6), angle=90),
            ],
        )
    )
    instrument.components.append(
        Component(
            nx_class="Detector",
            name="detector3",
            transform_parent=instrument.components[1],
            transforms=[
                Rotation(name="rotate", axis=QVector3D(4, 5, 6), angle=90),
                Translation(name="translate", vector=QVector3D(1, 2, 3)),
                Translation(name="translate2", vector=QVector3D(1, 2, 3)),
            ],
        )
    )
    # Use replace_contents to build the required transform models
    instrument.replace_contents(instrument.components)
    return instrument


def test_generate_matrix_combines_dependent_transforms():
    instrument = build_model_with_sample_transforms()

    def rotate_matrix(matrix: QMatrix4x4, rotate: Rotation):
        matrix.rotate(rotate.angle, rotate.axis)

    def translate_matrix(matrix: QMatrix4x4, translate: Translation):
        matrix.translate(translate.vector)

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
    component = Component("Monitor", "")
    component.geometry = NoShapeGeometry()
    actual_output = generate_mesh(component)

    assert actual_output.geometry().vertex_count == 36


def test_GIVEN_off_with_no_geometry_WHEN_generating_mesh_THEN_returns_nothing():
    component = Component("Monitor", "")

    component.geometry = OFFGeometry()
    actual_output = generate_mesh(component)

    assert actual_output.geometry().vertex_count == 0


def test_GIVEN_off_with_geometry_WHEN_generating_mesh_THEN_returns_off_mesh():
    component = Component("Monitor", "")
    component.geometry = OFFGeometry()
    assert isinstance(generate_mesh(component).geometry(), QtOFFGeometry)


def test_GIVEN_component_with_cylinder_geometry_WHEN_generating_mesh_THEN_returns_off_mesh():
    component = Component("Monitor", "")
    component.geometry = CylindricalGeometry()
    assert isinstance(generate_mesh(component).geometry(), QtOFFGeometry)


def test_GIVEN_component_with_detector_type_WHEN_generating_mesh_THEN_contains_pixel_data():
    component = Component("Detector", "")
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
    component = Component("Monitor", "")
    assert determine_pixel_state(component) == "SinglePixel"


def test_GIVEN_detector_with_PixelGrid_WHEN_determine_pixel_state_THEN_returns_Grid():
    component = Component("Detector", "")
    component.pixel_data = PixelGrid()
    assert determine_pixel_state(component) == "Grid"


def test_GIVEN_detector_with_PixelMapping_WHEN_determine_pixel_state_THEN_returns_Mapping():
    component = Component("Detector", "")
    component.pixel_data = PixelMapping([])
    assert determine_pixel_state(component) == "Mapping"


def test_GIVEN_slit_WHEN_determine_pixel_state_THEN_returns_empty_string():
    component = Component("Slit", "")
    assert determine_pixel_state(component) == ""
