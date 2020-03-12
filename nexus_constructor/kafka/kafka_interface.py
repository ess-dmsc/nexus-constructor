from abc import ABC, abstractmethod
from copy import copy
import asyncio
import threading

import attr


class KafkaInterface(ABC):
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._cancelled = False
        self._poll_thread = threading.Thread(target=self._poll_loop)
        self._is_connected = False
        self._lock = threading.Lock()
        # Call self._poll_thread.start() in child constructor

    @abstractmethod
    def _poll_loop(self):
        pass

    @property
    def connected(self):
        with self._lock:
            return_status = copy(self._is_connected)
        return return_status

    @connected.setter
    def connected(self, is_connected):
        with self._lock:
            self._is_connected = is_connected

    def close(self):
        self._cancelled = True
        self._poll_thread.join()


@attr.s
class FileWriter:
    name = attr.ib(type=str)
    # row = attr.ib()
    last_time = attr.ib(default=0)


@attr.s
class File:
    name = attr.ib(type=str)
    # row = attr.ib()
    start_time = attr.ib(type=str)
    stop_time = attr.ib(type=str)
    job_id = attr.ib(type=str, default="Unknown")
    writer_id = attr.ib(type=str, default="Unknown")
    last_time = attr.ib(default=0)
