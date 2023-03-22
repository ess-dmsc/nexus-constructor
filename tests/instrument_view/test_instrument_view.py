from mock import Mock

from nexus_constructor.instrument_view.instrument_view import InstrumentView


def test_GIVEN_cube_dimensions_WHEN_calling_set_cube_mesh_dimesions_THEN_dimensions_set():
    x = 1
    y = 1
    z = 1

    mock_cube_mesh = Mock()

    InstrumentView.set_cube_mesh_dimensions(mock_cube_mesh, x, y, z)

    mock_cube_mesh.setXExtent.assert_called_once_with(x)
    mock_cube_mesh.setYExtent.assert_called_once_with(y)
    mock_cube_mesh.setZExtent.assert_called_once_with(z)


def test_GIVEN_3D_view_and_gnomon_sizes_WHEN_calling_calculate_gnomon_rect_THEN_correct_ratios_returned():
    expected_width_ratio = 0.2
    expected_height_ratio = 0.25

    view_width = 1000
    view_height = 800

    gnomon_width = view_width * expected_width_ratio
    gnomon_height = view_height * expected_height_ratio

    # Use the ratio values and the width/height values of an imaginary 3D view to determine the width/height of an
    # imaginary gnomon (in this case the gnomon is 200x200). These same ratio values should then be returned when
    # calling calculate_gnomon_rect
    actual_width_ratio, actual_height_ratio = InstrumentView.calculate_gnomon_rect(
        view_width, view_height, gnomon_width, gnomon_height
    )

    assert expected_width_ratio == actual_width_ratio
    assert expected_height_ratio == actual_height_ratio


def test_GIVEN_entity_and_camera_WHEN_zooming_to_component_THEN_camera_zooms_to_component():
    mock_entity = Mock()
    mock_camera = Mock()

    InstrumentView.zoom_to_component(mock_entity, mock_camera)
    mock_camera.viewEntity.assert_called_once()
