from enum import Enum
from typing import Union

import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.group import Group

CHUNK_CHUNK_KB = "nexus.chunk.chunk_kb"
CHUNK_CHUNK_MB = "nexus.chunk.chunk_mb"
INDEX_EVERY_KB = "nexus.indices.index_every_kb"
INDEX_EVERY_MB = "nexus.indices.index_every_mb"
ADC_PULSE_DEBUG = "adc_pulse_debug"
STORE_LATEST_INTO = "store_latest_into"
WRITER_MODULE = "writer_module"
SOURCE = "source"
TOPIC = "topic"


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
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
            },
        }


@attr.s
class SENVStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)

    def as_dict(self):
        return {
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
            },
        }


@attr.s
class TDCTStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.TDCTIME.value, init=False)

    def as_dict(self):
        return {
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
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
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
                ADC_PULSE_DEBUG: self.adc_pulse_debug if not None else {},
                INDEX_EVERY_MB: self.nexus_indices_index_every_mb if not None else {},
                INDEX_EVERY_KB: self.nexus_indices_index_every_kb if not None else {},
                CHUNK_CHUNK_MB: self.nexus_chunk_chunk_mb if not None else {},
                CHUNK_CHUNK_KB: self.nexus_chunk_chunk_kb if not None else {},
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
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
                "value_units": self.value_units,
                CommonKeys.TYPE: self.type if not None else {},
                "array_size": self.array_size if not None else {},
                INDEX_EVERY_MB: self.nexus_indices_index_every_mb if not None else {},
                INDEX_EVERY_KB: self.nexus_indices_index_every_kb if not None else {},
                STORE_LATEST_INTO: self.store_latest_into if not None else {},
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
            CommonKeys.TYPE: NodeType.STREAM,
            NodeType.STREAM: {
                WRITER_MODULE: self.writer_module,
                SOURCE: self.source,
                TOPIC: self.topic,
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
