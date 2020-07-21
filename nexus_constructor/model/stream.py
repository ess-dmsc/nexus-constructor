from enum import Enum
from typing import Union

import attr

from nexus_constructor.model.group import Group


class WriterModules(Enum):
    F142 = "f142"
    EV42 = "ev42"
    TDCTIME = "TdcTime"
    NS10 = "ns10"
    HS00 = "hs00"
    SENV = "senv"


@attr.s
class NS10Stream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.NS10.value, init=False)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
            },
        }


@attr.s
class SENVStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
            },
        }


@attr.s
class TDCTStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.TDCTIME.value, init=False)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
            },
        }


@attr.s
class EV42Stream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.EV42.value, init=False)
    adc_pulse_debug = attr.ib(type=bool, default=None)
    nexus_indices_index_every_mb = attr.ib(type=int, default=None)
    nexus_indices_index_every_kb = attr.ib(type=int, default=None)
    nexus_chunk_chunk_mb = attr.ib(type=int, default=None)
    nexus_chunk_chunk_kb = attr.ib(type=int, default=None)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
                "adc_pulse_debug": self.adc_pulse_debug if not None else {},
                "nexus.indices.index_every_mb": self.nexus_indices_index_every_mb
                if not None
                else {},
                "nexus.indices.index_every_kb": self.nexus_indices_index_every_kb
                if not None
                else {},
                "nexus.chunk.chunk_mb": self.nexus_chunk_chunk_mb if not None else {},
                "nexus.chunk.chunk_kb": self.nexus_chunk_chunk_kb if not None else {},
            },
        }


@attr.s
class F142Stream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    type = attr.ib(type=str)
    value_units = attr.ib(type=str, default=None)
    array_size = attr.ib(type=float, default=None)
    writer_module = attr.ib(type=str, default=WriterModules.F142.value, init=False)
    nexus_indices_index_every_mb = attr.ib(type=int, default=None)
    nexus_indices_index_every_kb = attr.ib(type=int, default=None)
    store_latest_into = attr.ib(type=int, default=None)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
                "value_units": self.value_units,
                "type": self.type if not None else {},
                "array_size": self.array_size if not None else {},
                "nexus.indices.index_every_mb": self.nexus_indices_index_every_mb
                if not None
                else {},
                "nexus.indices.index_every_kb": self.nexus_indices_index_every_kb
                if not None
                else {},
                "store_latest_into": self.store_latest_into if not None else {},
            },
        }


HS00TYPES = ["uint32", "uint64", "float", "double"]


@attr.s
class HS00Stream:
    """Not currently supported yet"""

    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    data_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    error_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    edge_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    shape = attr.ib()
    writer_module = attr.ib(type=str, default=WriterModules.HS00.value, init=False)

    def as_dict(self):
        return {
            "type": "stream",
            "stream": {
                "writer_module": self.writer_module,
                "source": self.source,
                "topic": self.topic,
                "data_type": self.data_type,
                "error_type": self.error_type,
                "edge_type": self.edge_type,
                "shape": self.shape,
            },
        }


@attr.s
class StreamGroup(Group):
    def __setitem__(
        self,
        key: str,
        value: Union[
            NS10Stream, SENVStream, TDCTStream, EV42Stream, F142Stream, HS00Stream
        ],
    ):
        self.children.append(value)

    def __getitem__(self, item):
        """This is not simple as they do not have a name - we could do this by using a private member"""
        raise NotImplementedError
