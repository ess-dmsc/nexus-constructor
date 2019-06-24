from PySide2.QtGui import QMatrix4x4, QVector3D

from nexus_constructor.instrument_view import InstrumentView
from mock import Mock, call


def test_GIVEN_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():

    ambient = Mock()
    diffuse = Mock()

    mock_material = Mock()
    mock_material.setAmbient = Mock()
    mock_material.setDiffuse = Mock()

    """
    This method doesn't exist for QPhongMaterial but is mocked all the same to make sure that it isn't called when an
    alpha argument isn't given
    """
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


def test_GIVEN_cylinder_dimensions_WHEN_calling_set_cylinder_mesh_dimensions_THEN_dimensions_set():

    radius = 2
    length = 10
    rings = 2

    mock_cylinder = Mock()
    mock_cylinder.setRadius = Mock()
    mock_cylinder.setLength = Mock()
    mock_cylinder.setRings = Mock()

    InstrumentView.set_cylinder_mesh_dimensions(mock_cylinder, radius, length, rings)

    mock_cylinder.setRadius.assert_called_once_with(radius)
    mock_cylinder.setLength.assert_called_once_with(length)
    mock_cylinder.setRings.assert_called_once_with(rings)


def test_GIVEN_cylinder_transform_WHEN_calling_set_beam_transform_THEN_matrix_set():

    expected_matrix = QMatrix4x4()
    expected_matrix.rotate(270, QVector3D(1, 0, 0))
    expected_matrix.translate(QVector3D(0, 20, 0))

    mock_cylinder_transform = Mock()
    mock_cylinder_transform.setMatrix = Mock()

    InstrumentView.set_beam_transform(mock_cylinder_transform)

    assert mock_cylinder_transform.setMatrix.call_args[0][0] == expected_matrix


def test_GIVEN_radius_WHEN_calling_set_sphere_mesh_radius_THEN_radius_set():

    radius = 2
    mock_sphere_mesh = Mock()
    mock_sphere_mesh.setRadius = Mock()

    InstrumentView.set_sphere_mesh_radius(mock_sphere_mesh, radius)

    mock_sphere_mesh.setRadius.assert_called_once_with(radius)


def test_GIVEN_animation_parameters_WHEN_calling_set_neutron_animation_properties_THEN_properties_set():

    mock_neutron_animation_controller = Mock()
    animation_distance = 15
    time_span_offset = 5

    mock_neutron_animation = Mock()
    mock_neutron_animation.setTargetObject = Mock()
    mock_neutron_animation.setPropertyName = Mock()
    mock_neutron_animation.setStartValue = Mock()
    mock_neutron_animation.setEndValue = Mock()
    mock_neutron_animation.setDuration = Mock()
    mock_neutron_animation.setLoopCount = Mock()
    mock_neutron_animation.start = Mock()

    InstrumentView.set_neutron_animation_properties(
        mock_neutron_animation,
        mock_neutron_animation_controller,
        animation_distance,
        time_span_offset,
    )

    mock_neutron_animation.setTargetObject.assert_called_once_with(
        mock_neutron_animation_controller
    )
    mock_neutron_animation.setPropertyName.assert_called_once_with(b"distance")
    mock_neutron_animation.setStartValue.assert_called_once_with(animation_distance)
    mock_neutron_animation.setEndValue.assert_called_once_with(0)
    mock_neutron_animation.setDuration.assert_called_once_with(500 + time_span_offset)
    mock_neutron_animation.setLoopCount.assert_called_once_with(-1)
    mock_neutron_animation.start.assert_called_once()
