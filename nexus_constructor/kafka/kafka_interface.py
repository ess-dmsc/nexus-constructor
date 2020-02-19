import threading
from abc import ABC
from copy import copy


class KafkaInterface(ABC):
    lock = threading.Lock()

    @property
    def connected(self):
        self.lock.acquire()
        return_status = copy(self.connected)
        self.lock.release()
        return return_status

    @connected.setter
    def connected(self, is_connected):
        self.lock.acquire()
        self.connected = is_connected
        self.lock.release()
