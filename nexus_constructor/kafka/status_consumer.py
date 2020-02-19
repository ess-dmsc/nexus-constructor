from kafka import KafkaConsumer, TopicPartition
from copy import copy
import time
from kafka.errors import NoBrokersAvailable
import json

from nexus_constructor.kafka.kafka_interface import KafkaInterface


class StatusConsumer(KafkaInterface):
    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        self.filewriters = {}
        self.files = {}
        self.run_thread = True
        self.thread.start()

    @property
    def file_writers(self):
        self.lock.acquire()
        return_filewriters = copy(self.filewriters)
        self.lock.release()
        return return_filewriters

    @file_writers.setter
    def file_writers(self, updated_map):
        self.lock.acquire()
        self.filewriters = copy(updated_map)
        self.lock.release()

    @property
    def files(self):
        self.lock.acquire()
        return_files = copy(self.files)
        self.lock.release()
        return return_files

    @files.setter
    def files(self, updated_map):
        self.lock.acquire()
        self.files = copy(updated_map)
        self.lock.release()

    def thread_target(self):
        consumer = None
        while True:
            if not self.run_thread:
                return
            try:
                consumer = KafkaConsumer(bootstrap_servers=self.broker)
            except NoBrokersAvailable:
                time.sleep(2)
                continue
            break

        while not consumer.bootstrap_connected():
            time.sleep(0.5)
            if not self.run_thread:
                return
        available_topics = consumer.topics()
        while self.topic not in available_topics:
            time.sleep(0.5)
            available_topics = consumer.topics()
            if not self.run_thread:
                return
        topic = TopicPartition(self.topic, 0)
        consumer.assign([topic])
        consumer.seek_to_end(topic)
        self.connected = True
        known_writers = {}
        known_files = {}
        while self.run_thread:
            data = consumer.poll(500)
            had_updates = False
            for itm in data:
                had_updates = True
                for msg in data[itm]:
                    msg_obj = json.loads(msg.value)
                    if msg_obj["type"] == "filewriter_status_master":
                        writer_id = msg_obj["service_id"]
                        if writer_id not in known_writers:
                            known_writers[writer_id] = {"last_seen": 0}
                        known_writers[writer_id]["last_seen"] = msg.timestamp
                        for file_id in msg_obj["files"]:
                            file_name = msg_obj["files"][file_id]["filename"]
                            if file_name not in known_files:
                                known_files[file_name] = {
                                    "file_id": file_id,
                                    "file_name": file_name,
                                    "last_seen": 0,
                                    "writer_id": writer_id,
                                }
                            known_files[file_name]["last_seen"] = msg.timestamp
            if had_updates:
                self.file_writers = known_writers
                self.files = known_files
