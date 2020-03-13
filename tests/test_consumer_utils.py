import attr

from nexus_constructor.kafka.consumer_utils import handle_consumer_message


@attr.s
class MockMessage:
    ts = attr.ib(type=int, default=0)

    def timestamp(self):
        return 0, self.ts


def test_handle_consumer_message_returns_list_of_files_and_filewriters_with_correct_values():
    file_name = "test.nxs"
    job_id = "asdfgh1jk23"
    start_time = 12345678
    stop_time = 87654321
    service_id = "nfj2-2jfn-f142-ev42"
    message = {
        "service_id": service_id,
        "file_being_written": file_name,
        "job_id": job_id,
        "start_time": start_time,
        "stop_time": stop_time,
        "update_interval": 2000,
    }

    last_seen = 23458789
    kafka_message = MockMessage(last_seen)

    files = {}
    writers = {}
    known_writers, known_files = handle_consumer_message(
        files, writers, kafka_message, message
    )

    assert file_name in known_files.keys()
    file = known_files[file_name]

    assert file.name == file_name
    assert file.last_time == last_seen
    assert file.start_time == start_time
    assert file.stop_time == stop_time
    assert file.writer_id == service_id
    assert file.row == 0

    assert service_id in known_writers.keys()
    writer = known_writers[service_id]
    assert writer.name == service_id
    assert writer.last_time == last_seen
    assert writer.row == 0
