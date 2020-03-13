from typing import Dict

import confluent_kafka

from nexus_constructor.kafka.kafka_interface import File, FileWriter


def handle_consumer_message(
    known_files: Dict[str, File],
    known_writers: Dict[str, FileWriter],
    kafka_message: confluent_kafka.Message,
    msg_obj: Dict[str, str],
):
    timestamp = kafka_message.timestamp()[1]

    writer_id = _construct_filewriter(known_writers, msg_obj, timestamp)
    _construct_file(known_files, msg_obj, timestamp, writer_id)
    return known_writers, known_files


def _construct_file(
    known_files: Dict[str, File],
    msg_obj: Dict[str, str],
    timestamp: int,
    writer_id: str,
):
    file_name = (
        msg_obj["file_being_written"] if "file_being_written" in msg_obj else None
    )
    if file_name not in [None, ""]:
        if file_name not in known_files:
            start_time = msg_obj["start_time"]
            stop_time = msg_obj["stop_time"]
            job_id = msg_obj["job_id"]
            known_files[file_name] = File(file_name, 0, start_time, stop_time, job_id)
            if writer_id is not None:
                known_files[file_name].writer_id = writer_id
        known_files[file_name].last_time = timestamp


def _construct_filewriter(
    known_writers: Dict[str, FileWriter], msg_obj: Dict[str, str], timestamp: int
):
    writer_id = msg_obj["service_id"] if "service_id" in msg_obj else None
    if writer_id is not None:
        if writer_id not in known_writers:
            known_writers[writer_id] = FileWriter(writer_id, 0)
        # msg.timestamp()[0] is the timestamp type
        known_writers[writer_id].last_time = timestamp
    return writer_id
