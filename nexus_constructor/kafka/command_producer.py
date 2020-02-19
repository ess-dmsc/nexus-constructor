from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import threading
import time
from queue import Queue

from nexus_constructor.kafka.kafka_interface import KafkaInterface


class CommandProducer(KafkaInterface):
    def __init__(self, address, topic):
        self.address = address
        self.topic = topic
        self.run_thread = True
        self.connected = False
        self.thread = threading.Thread(target=self.produce_thread)
        self.msg_queue = Queue()
        self.thread.start()

    def __del__(self):
        self.run_thread = False
        self.thread.join()

    def send_command(self, message):
        self.msg_queue.put(message, block=True)

    def produce_thread(self):
        producer = None
        while True:
            if not self.run_thread:
                return
            try:
                producer = KafkaProducer(
                    bootstrap_servers=self.address, max_request_size=100_000_000
                )
            except NoBrokersAvailable:
                time.sleep(2)
                continue
            break

        while not producer.bootstrap_connected():
            time.sleep(0.5)
            if not self.run_thread:
                return
        self.connected = True
        while self.run_thread:
            if not self.msg_queue.empty():
                send_msg = self.msg_queue.get(block=False)
                if type(send_msg) == str:
                    send_msg = send_msg.encode("utf-8")
                producer.send(self.topic, send_msg)
            else:
                time.sleep(0.2)
