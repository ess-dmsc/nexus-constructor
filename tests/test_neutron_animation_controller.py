from PySide2.QtGui import QMatrix4x4
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


def test_GIVEN_nothing_WHEN_calling_get_distance_THEN_distance_returned():

    neutron_animation_controller = NeutronAnimationController(0, 0, None)
    new_distance = 6
    neutron_animation_controller._distance = new_distance

    assert neutron_animation_controller.get_distance() == new_distance


def test_given_offset_and_distance_WHEN_updating_matrix_THEN_correct_matrix_created():

    x_offset = 2
    y_offset = 2
    distance = 2

    expected_matrix = QMatrix4x4(0.1, 0, 0, 2, 0, 0.1, 0, 2, 0, 0, 0.1, 2, 0, 0, 0, 1)

    neutron_animation_controller = NeutronAnimationController(x_offset, y_offset, None)
    neutron_animation_controller._distance = distance

    neutron_animation_controller.update_matrix()

    assert neutron_animation_controller._matrix == expected_matrix
