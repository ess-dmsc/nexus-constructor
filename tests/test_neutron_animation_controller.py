from nexus_constructor.NeutronAnimationController import NeutronAnimationController
from mock import Mock


def test_GIVEN_target_WHEN_setting_target_THEN_target_changed_to_new_value():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    mock_target = Mock()
    neutron_animation_controller.set_target(mock_target)

    assert neutron_animation_controller._target is mock_target
