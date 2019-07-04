from mock import Mock

from nexus_constructor.instrument_view import InstrumentView


def test_GIVEN_cube_dimensions_WHEN_calling_set_cube_mesh_dimesions_THEN_dimensions_set():

    x = 1
    y = 1
    z = 1

    mock_cube_mesh = Mock()
    mock_cube_mesh.setXExtent = Mock()
    mock_cube_mesh.setYExtent = Mock()
    mock_cube_mesh.setZExtent = Mock()

    InstrumentView.set_cube_mesh_dimensions(mock_cube_mesh, x, y, z)

    mock_cube_mesh.setXExtent.assert_called_once_with(x)
    mock_cube_mesh.setYExtent.assert_called_once_with(y)
    mock_cube_mesh.setZExtent.assert_called_once_with(z)

