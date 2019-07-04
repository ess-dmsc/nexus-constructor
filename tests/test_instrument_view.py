from mock import Mock, call

from nexus_constructor.instrument_view import InstrumentView


def test_GIVEN_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():

    ambient = Mock()
    diffuse = Mock()

    mock_material = Mock()
    mock_material.setAmbient = Mock()
    mock_material.setDiffuse = Mock()

    # This method doesn't exist for QPhongMaterial but is mocked all the same to make sure that it isn't called when an
    # alpha argument isn't given
    mock_material.setAlpha = Mock()

    InstrumentView.set_material_properties(mock_material, ambient, diffuse)

    mock_material.setAmbient.assert_called_once_with(ambient)
    mock_material.setDiffuse.assert_called_once_with(diffuse)
    mock_material.setAlpha.assert_not_called()


def test_GIVEN_alpha_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():

    ambient = Mock()
    diffuse = Mock()
    alpha = 0.5

    mock_alpha_material = Mock()
    mock_alpha_material.setAmbient = Mock()
    mock_alpha_material.setDiffuse = Mock()
    mock_alpha_material.setAmbient = Mock()

    InstrumentView.set_material_properties(mock_alpha_material, ambient, diffuse, alpha)

    mock_alpha_material.setAmbient.assert_called_once_with(ambient)
    mock_alpha_material.setDiffuse.assert_called_once_with(diffuse)
    mock_alpha_material.setAlpha.assert_called_once_with(alpha)


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


def test_GIVEN_components_WHEN_calling_add_components_to_entity_THEN_components_added():

    mock_entity = Mock()
    mock_entity.addComponent = Mock()
    mock_components = [Mock() for _ in range(4)]
    calls = [call(mock_component) for mock_component in mock_components]

    InstrumentView.add_qcomponents_to_entity(mock_entity, mock_components)

    mock_entity.addComponent.assert_has_calls(calls)
