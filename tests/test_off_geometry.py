import pytest
from mock import patch
from numpy import array_equal, array

from nexus_constructor.geometry import (
    OFFGeometryNoNexus,
    OFFGeometryNexus,
    record_faces_in_file,
)
from PySide2.QtGui import QVector3D

from nexus_constructor.pixel_data import PixelMapping
from .helpers import add_component_to_file
from pytest import approx


@pytest.fixture
def nx_geometry_group(nexus_wrapper):
    return nexus_wrapper.create_nx_group(
        "test_geometry", "NXoff_geometry", nexus_wrapper.entry
    )


def test_GIVEN_nothing_WHEN_constructing_OFFGeometry_THEN_geometry_str_is_OFF():
    geom = OFFGeometryNoNexus()
    assert geom.geometry_str == "OFF"


UNIT = "m"
AXIS_DIRECTION = QVector3D(1, 2, 3)
HEIGHT = 2.0
RADIUS = 1.0


def test_GIVEN_faces_WHEN_calling_winding_order_on_OFF_THEN_order_is_correct():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]

    geom = OFFGeometryNoNexus(vertices, faces)
    expected = [point for face in faces for point in face]

    assert expected == geom.winding_order


def test_GIVEN_faces_WHEN_calling_winding_order_indices_on_OFF_THEN_order_is_correct():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]

    geom = OFFGeometryNoNexus(vertices, faces)

    expected = [0]  # only one face

    assert expected == geom.winding_order_indices


def test_GIVEN_off_geometry_WHEN_calling_off_geometry_on_offGeometry_THEN_original_geometry_is_returned():
    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(0, 1, 1),
    ]

    faces = [[0, 1, 2, 3]]
    geom = OFFGeometryNoNexus(vertices, faces)

    assert geom.faces == faces
    assert geom.vertices == vertices
    assert geom.off_geometry == geom


def test_can_get_off_geometry_properties(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper)

    vertex_3_x = 0.0
    vertex_3_y = 1.0
    vertex_3_z = 1.0

    vertices = [
        QVector3D(0, 0, 1),
        QVector3D(0, 1, 0),
        QVector3D(0, 0, 0),
        QVector3D(vertex_3_x, vertex_3_y, vertex_3_z),
    ]

    faces = [[0, 1, 2, 3]]

    shape = OFFGeometryNoNexus(vertices, faces)

    component.set_off_shape(shape)

    nexus_shape, _ = component.shape
    assert isinstance(nexus_shape, OFFGeometryNexus)
    assert nexus_shape.faces == faces
    assert nexus_shape.vertices[3].x() == approx(vertex_3_x)
    assert nexus_shape.vertices[3].y() == approx(vertex_3_y)
    assert nexus_shape.vertices[3].z() == approx(vertex_3_z)


def test_can_set_off_geometry_properties(nexus_wrapper):
    component = add_component_to_file(nexus_wrapper)

    vertices = [
        QVector3D(0.0, 0.0, 1.0),
        QVector3D(0.0, 1.0, 0.0),
        QVector3D(0.0, 0.0, 0.0),
        QVector3D(0.0, 1.0, 1.0),
    ]

    faces = [[0, 1, 2, 3]]

    shape = OFFGeometryNoNexus(vertices, faces)

    component.set_off_shape(shape)

    nexus_shape, _ = component.shape

    vertex_2_x = 0.5
    vertex_2_y = -0.5
    vertex_2_z = 0
    new_vertices = [
        QVector3D(-0.5, -0.5, 0),
        QVector3D(0, 0.5, 0),
        QVector3D(vertex_2_x, vertex_2_y, vertex_2_z),
    ]
    triangle = [0, 1, 2]
    new_faces = [triangle]
    nexus_shape.vertices = new_vertices
    nexus_shape.faces = new_faces

    assert nexus_shape.faces == new_faces
    assert nexus_shape.vertices[2].x() == approx(vertex_2_x)
    assert nexus_shape.vertices[2].y() == approx(vertex_2_y)
    assert nexus_shape.vertices[2].z() == approx(vertex_2_z)


def test_can_record_list_of_vertices_for_each_face(nexus_wrapper):
    # Reverse process of test_can_retrieve_list_of_vertices_for_each_face
    component = add_component_to_file(nexus_wrapper)

    shape = OFFGeometryNoNexus(
        [QVector3D(0.0, 0.0, 1.0), QVector3D(0.0, 1.0, 0.0), QVector3D(0.0, 0.0, 0.0)],
        [[0, 1, 2]],
    )

    component.set_off_shape(shape)
    nexus_shape, _ = component.shape

    test_input_vertex_indices_split_by_face = [
        [0, 1, 2],
        [3, 4, 5, 6],
        [7, 8, 9, 10, 11],
    ]

    record_faces_in_file(
        nexus_wrapper, nexus_shape.group, test_input_vertex_indices_split_by_face
    )

    expected_output_flat_list_of_vertex_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    expected_output_start_index_of_each_face = [0, 3, 7]

    flat_list_of_vertex_indices = nexus_shape.group["winding_order"][...].tolist()
    start_index_of_each_face = nexus_shape.group["faces"][...].tolist()

    assert flat_list_of_vertex_indices == expected_output_flat_list_of_vertex_indices
    assert start_index_of_each_face == expected_output_start_index_of_each_face


def test_can_retrieve_list_of_vertices_for_each_face(nexus_wrapper):
    # Reverse process of test_can_record_list_of_vertices_for_each_face

    component = add_component_to_file(nexus_wrapper)

    shape = OFFGeometryNoNexus(
        [QVector3D(0.0, 0.0, 1.0), QVector3D(0.0, 1.0, 0.0), QVector3D(0.0, 0.0, 0.0)],
        [[0, 1, 2]],
    )

    component.set_off_shape(shape)

    test_input_flat_list_of_vertex_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    # Define there are three faces, the difference in starting index indicates there are three vertices
    # in the first face (triangle), four in the second (square), and five in the third face (pentagon)
    test_input_start_index_of_each_face = [0, 3, 7]

    expected_output_vertex_indices_split_by_face = [
        [0, 1, 2],
        [3, 4, 5, 6],
        [7, 8, 9, 10, 11],
    ]

    nexus_shape, _ = component.shape

    nexus_wrapper.set_field_value(
        nexus_shape.group, "winding_order", test_input_flat_list_of_vertex_indices
    )
    nexus_wrapper.set_field_value(
        nexus_shape.group, "faces", test_input_start_index_of_each_face
    )

    assert nexus_shape.faces == expected_output_vertex_indices_split_by_face


def test_GIVEN_pixel_mapping_WHEN_initialising_off_geometry_THEN_mapping_in_nexus_file_matches_mapping_in_pixel_data_object(
    nexus_wrapper, nx_geometry_group
):
    num_detectors = 6
    ids = [i for i in range(num_detectors)]
    pixel_mapping = PixelMapping(ids)
    expected_dataset = [(id, id) for id in ids]

    # Patch the validation method so that it doesn't mind information being absent from the NeXus group
    with patch(
        "nexus_constructor.geometry.off_geometry.OFFGeometryNexus._verify_in_file"
    ):
        off_geometry = OFFGeometryNexus(
            nexus_wrapper, nx_geometry_group, "m", "path", pixel_mapping
        )

    actual_dataset = off_geometry.detector_faces

    assert array_equal(array(expected_dataset), actual_dataset)
