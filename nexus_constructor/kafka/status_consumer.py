from copy import copy
import time
import json
import logging
from typing import Dict

import confluent_kafka
from uuid import uuid1


from nexus_constructor.kafka.kafka_interface import KafkaInterface, FileWriter, File


def handle_consumer_message(
    known_files: Dict[str, File],
    known_writers: Dict[str, FileWriter],
    msg: confluent_kafka.Message,
    msg_obj: Dict[str, str],
):
    timestamp = msg.timestamp()[1]

    writer_id = _construct_filewriter(known_writers, msg_obj, timestamp)
    _construct_file(known_files, msg_obj, timestamp, writer_id)
    return known_writers, known_files


def _construct_file(
    known_files: Dict[str, File],
    msg_obj: Dict[str, str],
    timestamp: str,
    writer_id: str,
):
    file_name = (
        msg_obj["file_being_written"] if "file_being_written" in msg_obj else None
    )
    if file_name is not None:
        if file_name not in known_files:
            start_time = msg_obj["start_time"]
            stop_time = msg_obj["stop_time"]
            job_id = msg_obj["job_id"]
            known_files[file_name] = File(file_name, start_time, stop_time, job_id,)
            if writer_id is not None:
                known_files[file_name].writer_id = writer_id
        known_files[file_name].last_time = timestamp


def _construct_filewriter(
    known_writers: Dict[str, FileWriter], msg_obj: Dict[str, str], timestamp: str
):
    writer_id = msg_obj["service_id"] if "service_id" in msg_obj else None
    if writer_id is not None:
        if writer_id not in known_writers:
            known_writers[writer_id] = FileWriter(writer_id, 0)
        # msg.timestamp()[0] is the timestamp type
        known_writers[writer_id].last_time = timestamp
    return writer_id


class StatusConsumer(KafkaInterface):
    def __init__(self, address, topic):
        super().__init__()
        self._topic = topic
        configs = {
            "bootstrap.servers": address,
            "message.max.bytes": "100000000",
            "group.id": str(uuid1),
        }
        self._consumer = confluent_kafka.Consumer(configs)
        self._file_writers = {}
        self._files = {}
        self._poll_thread.start()

    @property
    def file_writers(self):
        with self._lock:
            return_filewriters = copy(self._file_writers)
        return return_filewriters

    @file_writers.setter
    def file_writers(self, updated_map):
        with self._lock:
            self._file_writers = copy(updated_map)

    @property
    def files(self):
        with self._lock:
            return_files = copy(self._files)
        return return_files

    @files.setter
    def files(self, updated_map):
        with self._lock:
            self._files = copy(updated_map)

    def _poll_loop(self):
        try:
            metadata = self._consumer.list_topics()
        except confluent_kafka.KafkaException:
            self.connected = False
            return

        while self._topic not in metadata.topics.keys():
            metadata = self._consumer.list_topics()
            time.sleep(0.5)
            if self._cancelled:
                return

        self._consumer.subscribe([self._topic])
        self.connected = True

        known_writers = {}
        known_files = {}
        while not self._cancelled:
            try:
                msg = self._consumer.poll(0.5)
            except RuntimeError:
                self.connected = False
                break
            if msg is None:
                continue
            if msg.error():
                logging.error(msg.error())
            else:
                msg_obj = json.loads(msg.value())
                self.file_writers, self.files = handle_consumer_message(
                    known_files, known_writers, msg, msg_obj
                )

    def close(self):
        self._cancelled = True
        self._consumer.close()
        self._poll_thread.join()
