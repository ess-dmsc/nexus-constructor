import pytest
from mock import Mock, call, patch

from nexus_constructor.instrument_view.qentity_utils import (
    create_material,
    create_qentity,
)


@pytest.mark.skip(reason="does not test the correct thing anymore")
def test_GIVEN_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():
    ambient = Mock()
    diffuse = Mock()

    mock_material, mock_hover_material = create_material("x_material", None)

    mock_material.setAmbient.assert_called_once_with(ambient)
    mock_material.setDiffuse.assert_called_once_with(diffuse)
    mock_material.setAlpha.assert_not_called()
    mock_material.setShininess.assert_not_called()


@pytest.mark.skip(reason="does not test the correct thing anymore")
def test_GIVEN_alpha_material_properties_WHEN_calling_set_material_properties_THEN_properties_set():
    ambient = Mock()
    diffuse = Mock()
    alpha = 0.5

    mock_alpha_material, mock_hover_material = create_material("beam_material", None)

    mock_alpha_material.setAmbient.assert_called_once_with(ambient)
    mock_alpha_material.setDiffuse.assert_called_once_with(diffuse)
    mock_alpha_material.setAlpha.assert_called_once_with(alpha)
    mock_alpha_material.setShininess.assert_not_called()


@pytest.mark.skip(reason="does not test the correct thing anymore")
def test_GIVEN_shininess_argument_WHEN_calling_set_material_properties_THEN_shininess_set_to_zero():
    ambient = Mock()
    diffuse = Mock()

    mock_material, mock_hover_material = create_material(
        "x_material", None, remove_shininess=True
    )

    mock_material.setAmbient.assert_called_once_with(ambient)
    mock_material.setDiffuse.assert_called_once_with(diffuse)
    mock_material.setAlpha.assert_not_called()
    mock_material.setShininess.assert_called_once_with(0)


@patch("nexus_constructor.instrument_view.qentity_utils.Entity", return_value=Mock())
def test_GIVEN_components_WHEN_calling_add_components_to_entity_THEN_components_added(
    mock,
):
    mock_parent = Mock()
    mock_components = [Mock() for _ in range(4)]
    calls = [call(mock_component) for mock_component in mock_components]

    mock_entity = create_qentity(mock_components, mock_parent)
    mock_entity.addComponent.assert_has_calls(calls)
