from kafka import KafkaProducer, TopicPartition
from kafka.errors import NoBrokersAvailable
import threading
import time
from queue import Queue
from copy import copy

class CommandProducer:
    def __init__(self, address, topic):
        self.address = address
        self.topic = topic
        self.run_thread = True
        self.connected = False
        self.command_lock = threading.Lock()
        self.thread = threading.Thread(target=self.produce_thread)
        self.msg_queue = Queue()
        self.thread.start()

    def __del__(self):
        self.run_thread = False
        self.thread.join()

    def hasUnsentMessages(self):
        return not self.msg_queue.empty()

    def isConnected(self):
        self.command_lock.acquire()
        return_status = copy(self.connected)
        self.command_lock.release()
        return return_status

    def sendCommand(self, message):
        self.msg_queue.put(message, block = True)

    def _setConnected(self, is_connected):
        self.command_lock.acquire()
        self.connected = is_connected
        self.command_lock.release()

    def produce_thread(self):
        producer = None
        while True:
            if not self.run_thread:
                return
            try:
                producer = KafkaProducer(bootstrap_servers = self.address, max_request_size = 100_000_000)
            except NoBrokersAvailable:
                time.sleep(2)
                continue
            break

        while not producer.bootstrap_connected():
            time.sleep(0.5)
            if not self.run_thread:
                return
        self._setConnected(True)
        while self.run_thread:
            if not self.msg_queue.empty():
                send_msg = self.msg_queue.get(block = False)
                producer.send(self.topic, send_msg)
            else:
                time.sleep(0.2)