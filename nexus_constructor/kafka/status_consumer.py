import json
import logging
import time
from copy import copy
from uuid import uuid1

import confluent_kafka

from nexus_constructor.kafka.kafka_interface import KafkaInterface


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
                if "service_id" in msg_obj:
                    writer_id = msg_obj["service_id"]
                    if writer_id not in known_writers:
                        known_writers[writer_id] = {"last_seen": 0}
                    known_writers[writer_id]["last_seen"] = msg.timestamp()[1]
                    # msg.timestamp()[0] is the timestamp type
                if "file_being_written" in msg_obj:
                    file_name = msg_obj["file_being_written"]
                    if file_name is not None and file_name not in known_files:
                        known_files[file_name] = {
                            "file_name": file_name,
                            "last_seen": 0,
                        }
                    known_files[file_name]["last_seen"] = msg.timestamp()[1]
                    self.file_writers = known_writers
                    self.files = known_files

    def close(self):
        self._cancelled = True
        self._consumer.close()
        self._poll_thread.join()
