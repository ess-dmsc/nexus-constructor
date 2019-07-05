from mock import Mock, call

from nexus_constructor.qentity_utils import (
    set_material_properties,
    add_qcomponents_to_entity,
)


def test_GIVEN_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():

    ambient = Mock()
    diffuse = Mock()

    mock_material = Mock()

    set_material_properties(mock_material, ambient, diffuse)

    mock_material.setAmbient.assert_called_once_with(ambient)
    mock_material.setDiffuse.assert_called_once_with(diffuse)
    mock_material.setAlpha.assert_not_called()
    mock_material.setShininess.assert_not_called()


def test_GIVEN_alpha_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():

    ambient = Mock()
    diffuse = Mock()
    alpha = 0.5

    mock_alpha_material = Mock()
    set_material_properties(mock_alpha_material, ambient, diffuse, alpha)

    mock_alpha_material.setAmbient.assert_called_once_with(ambient)
    mock_alpha_material.setDiffuse.assert_called_once_with(diffuse)
    mock_alpha_material.setAlpha.assert_called_once_with(alpha)
    mock_alpha_material.setShininess.assert_not_called()


def test_GIVEN_shininess_argument_WHEN_calling_set_material_properties_THEN_shininess_set_to_zero():

    ambient = Mock()
    diffuse = Mock()

    mock_material = Mock()

    set_material_properties(mock_material, ambient, diffuse, remove_shininess=True)

    mock_material.setAmbient.assert_called_once_with(ambient)
    mock_material.setDiffuse.assert_called_once_with(diffuse)
    mock_material.setAlpha.assert_not_called()
    mock_material.setShininess.assert_called_once_with(0)


def test_GIVEN_components_WHEN_calling_add_components_to_entity_THEN_components_added():

    mock_entity = Mock()
    mock_components = [Mock() for _ in range(4)]
    calls = [call(mock_component) for mock_component in mock_components]

    add_qcomponents_to_entity(mock_entity, mock_components)

    mock_entity.addComponent.assert_has_calls(calls)
