from nexus_constructor.NeutronAnimationController import NeutronAnimationController
from mock import Mock


def test_GIVEN_target_WHEN_setting_target_THEN_target_changed_to_new_value():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    mock_target = Mock()
    neutron_animation_controller.set_target(mock_target)

    assert neutron_animation_controller._target is mock_target


def test_GIVEN_nothing_WHEN_calling_get_target_THEN_target_returned():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    mock_target = Mock()
    neutron_animation_controller._target = mock_target

    assert neutron_animation_controller.get_target() is mock_target


def test_GIVEN_distance_WHEN_calling_set_distance_THEN_distance_changed_to_new_value():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    new_distance = 6
    neutron_animation_controller.set_distance(new_distance)

    assert neutron_animation_controller._distance == new_distance


def test_GIVEN_distance_WHEN_calling_set_distance_THEN_update_matrix_is_called():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    neutron_animation_controller.update_matrix = Mock()
    new_distance = 6
    neutron_animation_controller.set_distance(new_distance)

    neutron_animation_controller.update_matrix.assert_called_once()

def test_GIVEN_distance_WHEN_calling_set_distance_THEN_distance_changed_signal_emitted():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    neutron_animation_controller.distance_changed = Mock()
    neutron_animation_controller.distance_changed.emit = Mock()
    new_distance = 6
    neutron_animation_controller.set_distance(new_distance)

    neutron_animation_controller.distance_changed.emit.assert_called_once()