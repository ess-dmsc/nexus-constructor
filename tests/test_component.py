from mock import patch
from nexus_constructor.component.component import (
    DependencyError,
    Component,
    SHAPE_GROUP_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    CYLINDRICAL_GEOMETRY_NEXUS_NAME,
    OFF_GEOMETRY_NEXUS_NAME,
)
from cmath import isclose
from PySide2.QtGui import QVector3D
import pytest
from pytest import approx
import numpy as np

from nexus_constructor.pixel_data import PixelGrid, CountDirection, Corner, PixelMapping
from nexus_constructor.pixel_data_to_nexus_utils import (
    get_x_offsets_from_pixel_grid,
    get_y_offsets_from_pixel_grid,
    get_z_offsets_from_pixel_grid,
    get_detector_ids_from_pixel_grid,
)
from .helpers import add_component_to_file
from nexus_constructor.geometry import (
    CylindricalGeometry,
    OFFGeometryNexus,
    OFFGeometryNoNexus,
    NoShapeGeometry,
)


@pytest.fixture(scope="function")
def component_group(nexus_wrapper):
    return nexus_wrapper.nexus_file.create_group("ComponentName")


@pytest.fixture(scope="function")
def component(nexus_wrapper, component_group):
    return Component(nexus_wrapper, component_group)


def test_can_create_and_read_from_field_in_component(nexus_wrapper):
    field_name = "some_field"
    field_value = 42
    component = add_component_to_file(nexus_wrapper, field_name, field_value)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == field_value
    ), "Expected to get same value back from field as it was created with"


def test_nameerror_raised_if_requested_field_does_not_exist(nexus_wrapper):
    field_name = "some_field"
    field_value = 42
    component = add_component_to_file(nexus_wrapper, field_name, field_value)
    try:
        component.get_field("nonexistent_field")
    except NameError:
        pass  # as expected


def test_created_component_has_specified_name(nexus_wrapper):
    name = "component_name"
    field_name = "some_field"
    field_value = 42
    component = add_component_to_file(nexus_wrapper, field_name, field_value, name)
    assert component.name == name


def test_component_can_be_renamed(nexus_wrapper):
    initial_name = "component_name"
    field_name = "some_field"
    field_value = 42
    component = add_component_to_file(
        nexus_wrapper, field_name, field_value, initial_name
    )
    assert component.name == initial_name
    new_name = "new_name"
    component.name = new_name
    assert component.name == new_name


def test_value_of_field_can_be_changed(nexus_wrapper):
    name = "component_name"
    field_name = "some_field"
    initial_value = 42
    component = add_component_to_file(nexus_wrapper, field_name, initial_value, name)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == initial_value
    ), "Expected to get same value back from field as it was created with"
    new_value = 13
    component.set_field("some_field", new_value, dtype=int)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == new_value
    ), "Expected to get same value back from field as it was changed to"


def test_type_of_field_can_be_changed(nexus_wrapper):
    """
    This is important to test because the implementation is very different to just changing the value.
    When the type changes the dataset has to be deleted and recreated with the new type
    """

    name = "component_name"
    field_name = "some_field"
    initial_value = 42
    component = add_component_to_file(nexus_wrapper, field_name, initial_value, name)
    returned_value = component.get_field(field_name)
    assert (
        returned_value == initial_value
    ), "Expected to get same value back from field as it was created with"

    new_value = 17.3
    component.set_field("some_field", new_value, dtype=float)
    returned_value = component.get_field(field_name)
    assert isclose(
        returned_value, new_value
    ), "Expected to get same value back from field as it was changed to"


def test_GIVEN_new_component_WHEN_get_transforms_for_component_THEN_transforms_list_is_empty(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")
    assert (
        len(component.transforms_full_chain) == 0
    ), "expected there to be no transformations in the newly created component"


def test_GIVEN_component_with_a_transform_added_WHEN_get_transforms_for_component_THEN_transforms_list_contains_transform(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    transform = component.add_translation(QVector3D(1.0, 0.0, 0.0))
    component.depends_on = transform

    assert (
        len(component.transforms_full_chain) == 1
    ), "expected there to be a transformation in the component"


def test_GIVEN_component_with_a_transform_added_WHEN_transform_is_deleted_THEN_transforms_list_is_empty(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)

    component.remove_transformation(transform)

    assert (
        len(component.transforms_full_chain) == 0
    ), "expected there to be no transforms in the component"


def test_GIVEN_a_component_with_a_transform_dependency_WHEN_get_depends_on_THEN_transform_dependency_is_returned(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    input_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component.depends_on = input_transform

    returned_transform = component.depends_on

    assert returned_transform.dataset.name == input_transform.dataset.name


def test_deleting_a_transformation_from_a_different_component_is_not_allowed(
    nexus_wrapper
):
    first_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    second_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)

    with pytest.raises(PermissionError):
        assert second_component.remove_transformation(
            transform
        ), "Expected not to be allowed to delete the transform as it belongs to a different component"


def test_deleting_a_transformation_which_the_component_directly_depends_on_is_not_allowed(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")
    transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    component.depends_on = transform

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            transform
        ), "Expected not to be allowed to delete the transform as the component directly depends on it"


def test_deleting_a_transformation_which_the_component_indirectly_depends_on_is_not_allowed(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")
    first_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = component.add_translation(
        QVector3D(1.0, 0.0, 0.0), depends_on=first_transform
    )
    component.depends_on = second_transform

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as the component indirectly depends on it"


def test_transforms_contains_only_local_transforms_not_full_depends_on_chain(
    nexus_wrapper
):
    first_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    second_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    assert len(
        second_component.transforms
    ), "Expect transforms list to contain only the 1 transform local to this component"


def test_transforms_contains_only_local_transforms_alt(nexus_wrapper):
    component1 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component2 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    transform1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform2 = component1.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=transform1
    )
    transform3 = component2.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=transform2
    )
    component1.depends_on = transform2
    component2.depends_on = transform3

    assert (
        len(component1.transforms) == 2
    ), "Expect transforms list to contain only the 2 transforms local to this component"
    assert (
        len(component2.transforms) == 1
    ), "Expect transforms list to contain only the 1 transform local to this component"


def test_transforms_has_link(nexus_wrapper):
    component1 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component2 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    transform1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform1.depends_on = transform2

    component1.depends_on = transform1
    component2.depends_on = transform2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.has_link


def test_transforms_link_is_correct(nexus_wrapper):
    component1 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component2 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    transform1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform1.depends_on = transform2

    component1.depends_on = transform1
    component2.depends_on = transform2

    new_component = Component(component1.file, component1.group)
    assert new_component.transforms.link.linked_component == component2


def test_transforms_has_no_link(nexus_wrapper):
    component1 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    component2 = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    transform1 = component1.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    transform2 = component2.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)

    component1.depends_on = transform1
    component2.depends_on = transform2

    new_component = Component(component1.file, component1.group)
    assert not new_component.transforms.has_link


def test_removing_transformation_which_has_a_dependent_transform_in_another_component_is_not_allowed(
    nexus_wrapper
):
    first_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    second_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    with pytest.raises(DependencyError):
        assert first_component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as a transform in another component depends on it"


def test_removing_transformation_which_no_longer_has_a_dependent_transform_in_another_component_is_allowed(
    nexus_wrapper
):
    first_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "component_name"
    )
    second_component = add_component_to_file(
        nexus_wrapper, "some_field", 42, "other_component_name"
    )

    first_transform = first_component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    second_transform = second_component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    second_component.depends_on = second_transform

    # Make second transform no longer depend on the first
    second_transform.depends_on = None

    try:
        first_component.remove_transformation(first_transform)
    except Exception:
        pytest.fail(
            "Expected to be able to remove transformation which is no longer a dependee"
        )


def test_removing_transformation_which_still_has_one_dependent_transform_is_not_allowed(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    first_transform = component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0)
    # second_transform
    component.add_rotation(QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform)
    third_transform = component.add_rotation(
        QVector3D(1.0, 0.0, 0.0), 90.0, depends_on=first_transform
    )

    # Make third transform no longer depend on the first one
    third_transform.depends_on = None

    with pytest.raises(DependencyError):
        assert component.remove_transformation(
            first_transform
        ), "Expected not to be allowed to delete the transform as the second transform still depends on it"


def test_can_add_cylinder_shape_to_and_component_and_get_the_same_shape_back(
    nexus_wrapper
):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    axis_x = 1.0
    axis_y = 0.0
    axis_z = 0.0
    axis = QVector3D(axis_x, axis_y, axis_z)
    height = 42.0
    radius = 37.0
    component.set_cylinder_shape(axis, height, radius)

    cylinder, _ = component.shape
    assert isinstance(cylinder, CylindricalGeometry)
    assert cylinder.height == approx(height)
    assert cylinder.radius == approx(radius)
    assert cylinder.axis_direction.x() == approx(axis_x)
    assert cylinder.axis_direction.y() == approx(axis_y)
    assert cylinder.axis_direction.z() == approx(axis_z)


def test_can_add_mesh_shape_to_and_component_and_get_the_same_shape_back(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    # Our test input mesh is a single triangle
    vertex_2_x = 0.5
    vertex_2_y = -0.5
    vertex_2_z = 0
    vertices = [
        QVector3D(-0.5, -0.5, 0),
        QVector3D(0, 0.5, 0),
        QVector3D(vertex_2_x, vertex_2_y, vertex_2_z),
    ]
    triangle = [0, 1, 2]
    faces = [triangle]
    input_mesh = OFFGeometryNoNexus(vertices, faces)
    component.set_off_shape(input_mesh)

    output_mesh, _ = component.shape
    assert isinstance(output_mesh, OFFGeometryNexus)
    assert output_mesh.faces[0] == triangle
    assert output_mesh.vertices[2].x() == approx(vertex_2_x)
    assert output_mesh.vertices[2].y() == approx(vertex_2_y)
    assert output_mesh.vertices[2].z() == approx(vertex_2_z)


def test_can_override_existing_shape(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper, "some_field", 42, "component_name")

    component.set_cylinder_shape()
    cylinder, _ = component.shape
    assert isinstance(
        cylinder, CylindricalGeometry
    ), "Expect shape to initially be a cylinder"

    vertices = [QVector3D(-0.5, -0.5, 0), QVector3D(0, 0.5, 0), QVector3D(0.5, -0.5, 0)]
    faces = [[0, 1, 2]]
    input_mesh = OFFGeometryNoNexus(vertices, faces)
    component.set_off_shape(input_mesh)
    output_mesh, _ = component.shape
    assert isinstance(output_mesh, OFFGeometryNexus), "Expect shape to now be a mesh"


def test_GIVEN_pixel_grid_WHEN_recording_pixel_data_to_nxdetector_THEN_pixel_data_in_nexus_file_matches_pixel_data_in_pixel_grid_object(
    component
):
    pixel_grid = PixelGrid(
        rows=5,
        columns=6,
        row_height=0.7,
        col_width=0.5,
        first_id=0,
        count_direction=CountDirection.COLUMN,
        initial_count_corner=Corner.BOTTOM_RIGHT,
    )

    component.record_pixel_grid(pixel_grid)

    assert np.array_equal(
        component.get_field("x_pixel_offset"), get_x_offsets_from_pixel_grid(pixel_grid)
    )
    assert np.array_equal(
        component.get_field("y_pixel_offset"), get_y_offsets_from_pixel_grid(pixel_grid)
    )
    assert np.array_equal(
        component.get_field("z_pixel_offset"), get_z_offsets_from_pixel_grid(pixel_grid)
    )
    assert np.array_equal(
        component.get_field("detector_number"),
        get_detector_ids_from_pixel_grid(pixel_grid),
    )


def test_GIVEN_pixel_mapping_WHEN_recording_pixel_data_to_nxdetector_THEN_pixel_ids_in_nexus_file_match_pixel_ids_in_mapping_object(
    component
):
    pixel_id_list = [i for i in range(5)]
    pixel_mapping = PixelMapping(pixel_id_list)
    component.record_pixel_mapping(pixel_mapping)

    assert np.array_equal(
        component.get_field("detector_number"), np.array(pixel_id_list)
    )


def test_GIVEN_pixel_mapping_WHEN_setting_cylinder_shape_THEN_cylindrical_geometry_is_called_with_pixel_data(
    component
):
    pixel_mapping = PixelMapping()

    with patch(
        "nexus_constructor.component.component.CylindricalGeometry"
    ) as mock_cylindrical_geometry_constructor:
        component.set_cylinder_shape(pixel_data=pixel_mapping)
        mock_cylindrical_geometry_constructor.assert_called_once_with(
            component.file, component.group[SHAPE_GROUP_NAME], pixel_mapping
        )


def test_GIVEN_pixel_mapping_WHEN_setting_off_geometry_shape_THEN_off_geometry_is_called_with_pixel_data(
    component
):
    pixel_mapping = PixelMapping()
    off_geometry = OFFGeometryNoNexus(vertices=[], faces=[])
    units = "m"
    filename = "somefile.off"

    with patch(
        "nexus_constructor.component.component.OFFGeometryNexus"
    ) as mock_off_geometry_constructor:

        component.set_off_shape(
            loaded_geometry=off_geometry,
            units=units,
            filename=filename,
            pixel_data=pixel_mapping,
        )
        mock_off_geometry_constructor.assert_called_once_with(
            component.file,
            component.group[SHAPE_GROUP_NAME],
            units,
            filename,
            pixel_mapping,
        )


def test_GIVEN_no_pixel_data_WHEN_setting_cylinder_shape_THEN_shape_group_has_name_shape(
    component
):
    with patch(
        "nexus_constructor.component.component.CylindricalGeometry"
    ) as mock_cylindrical_geometry_constructor:
        component.set_cylinder_shape(pixel_data=None)
        mock_cylindrical_geometry_constructor.assert_called_once_with(
            component.file, component.group[SHAPE_GROUP_NAME], None
        )


def test_GIVEN_no_pixel_data_WHEN_setting_off_geometry_shape_THEN_shape_group_has_name_shape(
    component
):
    off_geometry = OFFGeometryNoNexus(vertices=[], faces=[])
    units = "m"
    filename = "somefile.off"

    with patch(
        "nexus_constructor.component.component.OFFGeometryNexus"
    ) as mock_off_geometry_constructor:

        component.set_off_shape(
            loaded_geometry=off_geometry,
            units=units,
            filename=filename,
            pixel_data=None,
        )
        mock_off_geometry_constructor.assert_called_once_with(
            component.file, component.group[SHAPE_GROUP_NAME], units, filename, None
        )


def test_GIVEN_pixel_grid_WHEN_setting_cylinder_shape_THEN_cylindrical_geometry_is_not_called_with_pixel_data(
    component
):
    pixel_grid = PixelGrid()

    with patch(
        "nexus_constructor.component.component.CylindricalGeometry"
    ) as mock_cylindrical_geometry_constructor:
        component.set_cylinder_shape(pixel_data=pixel_grid)
        mock_cylindrical_geometry_constructor.assert_called_once_with(
            component.file, component.group[PIXEL_SHAPE_GROUP_NAME], None
        )


def test_GIVEN_pixel_grid_WHEN_setting_off_geometry_shape_THEN_off_geometry_is_not_called_with_pixel_data(
    component
):
    pixel_grid = PixelGrid()
    off_geometry = OFFGeometryNoNexus(vertices=[], faces=[])
    units = "m"
    filename = "somefile.off"

    with patch(
        "nexus_constructor.component.component.OFFGeometryNexus"
    ) as mock_off_geometry_constructor:

        component.set_off_shape(
            loaded_geometry=off_geometry,
            units=units,
            filename=filename,
            pixel_data=pixel_grid,
        )
        mock_off_geometry_constructor.assert_called_once_with(
            component.file,
            component.group[PIXEL_SHAPE_GROUP_NAME],
            units,
            filename,
            None,
        )


def test_GIVEN_cylinder_properties_WHEN_setting_cylindrical_geometry_shape_THEN_shape_group_has_class_nxcylindrical_geometry(
    component
):
    component.set_cylinder_shape()
    assert (
        component.group[SHAPE_GROUP_NAME].attrs["NX_class"]
        == CYLINDRICAL_GEOMETRY_NEXUS_NAME
    )


def test_GIVEN_off_properties_WHEN_setting_off_geometry_shape_THEN_shape_group_has_class_nxoff_geometry(
    component
):
    off_geometry = OFFGeometryNoNexus(vertices=[], faces=[])

    with patch("nexus_constructor.component.component.OFFGeometryNexus"):
        component.set_off_shape(loaded_geometry=off_geometry)

    assert (
        component.group[SHAPE_GROUP_NAME].attrs["NX_class"] == OFF_GEOMETRY_NEXUS_NAME
    )


def test_GIVEN_component_with_no_shape_information_WHEN_shape_is_requested_THEN_returns_NoShapeGeometry(
    component
):
    assert isinstance(component.shape[0], NoShapeGeometry)


def test_GIVEN_component_with_no_depends_on_field_WHEN_get_transformation_THEN_returns_identity_matrix(
    component
):
    assert component.transform.matrix().isIdentity()


def test_GIVEN_component_with_single_translation_WHEN_get_transformation_THEN_returns_the_translation(
    component
):
    translation_vector = QVector3D(0.42, -0.17, 3.0)
    translation = component.add_translation(translation_vector, "test_translation")
    component.depends_on = translation

    expected_matrix = np.array(
        (
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            translation_vector.x(),
            translation_vector.y(),
            translation_vector.z(),
            1,
        )
    )
    assert np.allclose(expected_matrix, np.array(component.transform.matrix().data()))


def test_GIVEN_component_with_two_translations_WHEN_get_transformation_THEN_returns_composite_translation(
    component
):
    first_translation_vector = QVector3D(0.42, -0.17, 3.0)
    first_translation = component.add_translation(
        first_translation_vector, "first_test_translation"
    )
    second_translation_vector = QVector3D(0.42, -0.17, 3.0)
    second_translation = component.add_translation(
        second_translation_vector, "second_test_translation", first_translation
    )
    component.depends_on = second_translation
    # component depends on second_translation which depends on first_translation

    expected_matrix = np.array(
        (
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            1,
            0,
            first_translation_vector.x() + second_translation_vector.x(),
            first_translation_vector.y() + second_translation_vector.y(),
            first_translation_vector.z() + second_translation_vector.z(),
            1,
        )
    )
    assert np.allclose(expected_matrix, np.array(component.transform.matrix().data()))


def test_GIVEN_component_with_pixel_mapping_WHEN_removing_pixel_data_THEN_pixel_mapping_is_cleared(
    component
):

    pixel_mapping = PixelMapping([i for i in range(6)])
    component.record_pixel_mapping(pixel_mapping)

    component.clear_pixel_data()
    assert component.get_field("detector_number") is None


def test_GIVEN_component_with_pixel_grid_WHEN_removing_pixel_data_THEN_pixel_grid_is_cleared(
    component
):

    pixel_grid = PixelGrid()
    component.record_pixel_grid(pixel_grid)

    component.clear_pixel_data()
    assert component.get_field("detector_number") is None
    assert component.get_field("x_pixel_offset") is None
    assert component.get_field("y_pixel_offset") is None
    assert component.get_field("z_pixel_offset") is None
