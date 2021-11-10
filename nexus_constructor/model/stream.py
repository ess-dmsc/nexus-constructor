from enum import Enum
from typing import List, Union

import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.group import Group

ARRAY_SIZE = "array_size"
VALUE_UNITS = "value_units"
CHUNK_CHUNK_KB = "nexus.chunk.chunk_kb"
CHUNK_CHUNK_MB = "nexus.chunk.chunk_mb"
INDEX_EVERY_KB = "nexus.indices.index_every_kb"
INDEX_EVERY_MB = "nexus.indices.index_every_mb"
ADC_PULSE_DEBUG = "adc_pulse_debug"
STORE_LATEST_INTO = "store_latest_into"
SOURCE = "source"
TOPIC = "topic"
DATASET = "dataset"
LINK = "link"


class WriterModules(Enum):
    F142 = "f142"
    EV42 = "ev42"
    TDCTIME = "tdct"
    NS10 = "ns10"
    HS00 = "hs00"
    SENV = "senv"


@attr.s
class Link:
    name = attr.ib(type=str)
    target = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=LINK, init=False)
    values = None
    attributes = None
    parent_node = None

    def as_dict(self):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {CommonKeys.NAME: self.name, SOURCE: self.target},
        }


@attr.s
class DataSetStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default="", init=False)

    def as_dict(self):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {SOURCE: self.source, TOPIC: self.topic},
        }


@attr.s
class NS10Stream(DataSetStream):
    writer_module = attr.ib(type=str, default=WriterModules.NS10.value, init=False)


@attr.s
class SENVStream(DataSetStream):
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)


@attr.s
class TDCTStream(DataSetStream):
    writer_module = attr.ib(type=str, default=WriterModules.TDCTIME.value, init=False)


@attr.s
class EV42Stream(DataSetStream):
    writer_module = attr.ib(type=str, default=WriterModules.EV42.value, init=False)
    adc_pulse_debug = attr.ib(type=bool, default=None)
    nexus_indices_index_every_mb = attr.ib(type=str, default=None)
    nexus_indices_index_every_kb = attr.ib(type=str, default=None)
    nexus_chunk_chunk_mb = attr.ib(type=int, default=None)
    nexus_chunk_chunk_kb = attr.ib(type=int, default=None)

    def as_dict(self):
        config_dict: dict = super().as_dict()
        if self.adc_pulse_debug is not None:
            config_dict[NodeType.CONFIG][ADC_PULSE_DEBUG] = self.adc_pulse_debug
        if self.nexus_indices_index_every_mb is not None:
            config_dict[NodeType.CONFIG][
                INDEX_EVERY_MB
            ] = self.nexus_indices_index_every_mb
        if self.nexus_indices_index_every_kb is not None:
            config_dict[NodeType.CONFIG][
                INDEX_EVERY_KB
            ] = self.nexus_indices_index_every_kb
        if self.nexus_chunk_chunk_mb is not None:
            config_dict[NodeType.CONFIG][CHUNK_CHUNK_MB] = self.nexus_chunk_chunk_mb
        if self.nexus_chunk_chunk_kb is not None:
            config_dict[NodeType.CONFIG][CHUNK_CHUNK_KB] = self.nexus_chunk_chunk_kb
        return config_dict


@attr.s
class F142Stream(DataSetStream):
    type = attr.ib(type=str)
    size = attr.ib(type=str, default=None)
    value_units = attr.ib(type=str, default=None)
    array_size = attr.ib(type=float, default=None)
    writer_module = attr.ib(type=str, default=WriterModules.F142.value, init=False)
    nexus_indices_index_every_mb = attr.ib(type=str, default=None)
    nexus_indices_index_every_kb = attr.ib(type=str, default=None)
    store_latest_into = attr.ib(type=int, default=None)

    def as_dict(self):
        config_dict: dict = super().as_dict()
        config_dict[NodeType.CONFIG][CommonKeys.DATA_TYPE] = self.type
        if self.value_units is not None:
            config_dict[NodeType.CONFIG][VALUE_UNITS] = self.value_units
        if self.array_size is not None:
            config_dict[NodeType.CONFIG][ARRAY_SIZE] = self.array_size
        if self.nexus_indices_index_every_mb is not None:
            config_dict[NodeType.CONFIG][
                INDEX_EVERY_MB
            ] = self.nexus_indices_index_every_mb
        if self.nexus_indices_index_every_kb is not None:
            config_dict[NodeType.CONFIG][
                INDEX_EVERY_KB
            ] = self.nexus_indices_index_every_kb
        if self.store_latest_into is not None:
            config_dict[NodeType.CONFIG][STORE_LATEST_INTO] = self.store_latest_into
        return config_dict


HS00TYPES = ["uint32", "uint64", "float", "double"]

DATA_TYPE = "data_type"
ERROR_TYPE = "error_type"
EDGE_TYPE = "edge_type"
SHAPE = "shape"


@attr.s
class HS00Stream(DataSetStream):
    """Not currently supported yet"""

    data_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    error_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    edge_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    shape = attr.ib()
    writer_module = attr.ib(type=str, default=WriterModules.HS00.value, init=False)

    def as_dict(self):
        config_dict: dict = super().as_dict()
        config_dict[NodeType.CONFIG][CommonKeys.DATA_TYPE] = self.data_type
        config_dict[NodeType.CONFIG][ERROR_TYPE] = self.error_type
        config_dict[NodeType.CONFIG][EDGE_TYPE] = self.edge_type
        config_dict[NodeType.CONFIG][SHAPE] = self.shape
        return config_dict


Stream = Union[NS10Stream, SENVStream, TDCTStream, EV42Stream, F142Stream, HS00Stream]


@attr.s
class StreamGroup(Group):
    # As the inheritance is broken for this class, type check with mypy must be ignored.
    # Parent class Group has a different type hint for the list in the children attribute.
    children: List[Stream] = attr.ib(factory=list, init=False)  # type: ignore

    def __setitem__(  # type: ignore
        self,
        key: str,
        value: Stream,
    ):
        self.children.append(value)

    def __getitem__(self, item):
        """This is not simple as they do not have a name - we could do this by using a private member"""
        raise NotImplementedError
