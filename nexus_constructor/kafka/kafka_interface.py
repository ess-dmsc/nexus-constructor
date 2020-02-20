import threading
from abc import ABC, abstractmethod
from copy import copy


class KafkaInterface(ABC):
    lock = threading.Lock()
    run_thread = False
    _connected = False

    def __init__(self):
        self.thread = threading.Thread(target=self.thread_target)

    @abstractmethod
    def thread_target(self):
        pass

    @property
    def connected(self):
        self.lock.acquire()
        return_status = copy(self._connected)
        self.lock.release()
        return return_status

    @connected.setter
    def connected(self, is_connected):
        self.lock.acquire()
        self._connected = is_connected
        self.lock.release()

    def __del__(self):
        self.run_thread = False
        self.thread.join()
