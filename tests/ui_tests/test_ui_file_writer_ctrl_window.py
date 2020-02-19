from nexus_constructor.file_writer_ctrl_window import FileWriterCtrl
from nexus_constructor.validators import BrokerAndTopicValidator


def test_UI_GIVEN_nothing_WHEN_creating_filewriter_control_window_THEN_broker_field_defaults_are_set_correctly(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)

    qtbot.addWidget(window)

    assert not window.command_broker_edit.text()
    assert window.command_broker_led.is_off()
    assert not window.command_broker_change_timer.isActive()

    assert not window.status_broker_edit.text()
    assert window.status_broker_led.is_off()
    assert not window.status_broker_change_timer.isActive()


def test_UI_GIVEN_nothing_WHEN_creating_filewriter_control_window_THEN_broker_validators_are_set_correctly(
    qtbot, instrument
):
    window = FileWriterCtrl(instrument)

    qtbot.addWidget(window)

    assert isinstance(window.status_broker_edit.validator(), BrokerAndTopicValidator)
    assert isinstance(window.command_broker_edit.validator(), BrokerAndTopicValidator)
    assert (
        window.command_broker_edit.validator() != window.status_broker_edit.validator()
    )  # make sure they are different objects so that both edits are validated independently from each other.
