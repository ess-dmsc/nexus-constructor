from enum import Enum
from typing import List, Union

import attr

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.group import Group

ARRAY_SIZE = "array_size"
VALUE_UNITS = "value_units"
CHUNK_CHUNK_KB = "nexus.chunk.chunk_kb"
CHUNK_CHUNK_MB = "nexus.chunk.chunk_mb"
CHUNK_SIZE = "chunk_size"
CUE_INTERVAL = "cue_interval"
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
    LINK = "link"
    DATASET = "dataset"
    ADAR = "ADAr"


class FileWriterModule:
    attributes = attr.ib(type=Attributes, factory=Attributes, init=False)
    name = attr.ib(type=str, default=None)
    parent_node = attr.ib(type="Group", default=None)
    source = attr.ib(type=str)
    topic = attr.ib(type=str, default=None)
    writer_module = attr.ib(type=str, init=False)

    def as_dict(self):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {SOURCE: self.source, TOPIC: self.topic},
        }


@attr.s
class NS10Stream(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.NS10.value, init=False)


@attr.s
class SENVStream(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)


@attr.s
class TDCTStream(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)


@attr.s
class EV42Stream(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.EV42.value, init=False)
    adc_pulse_debug = attr.ib(type=bool, default=None, init=False)
    cue_interval = attr.ib(type=int, default=None, init=False)
    chunk_size = attr.ib(type=int, default=None, init=False)

    def as_dict(self):
        module_dict = FileWriterModule.as_dict(self)
        if self.adc_pulse_debug:
            module_dict[NodeType.CONFIG][ADC_PULSE_DEBUG] = self.adc_pulse_debug
        if self.chunk_size:
            module_dict[NodeType.CONFIG][CHUNK_SIZE] = self.chunk_size
        if self.cue_interval:
            module_dict[NodeType.CONFIG][CUE_INTERVAL] = self.cue_interval
        return module_dict


@attr.s
class F142Stream(EV42Stream):
    writer_module = attr.ib(type=str, default=WriterModules.EV42.value, init=False)


@attr.s
class Link(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.LINK.value, init=False)
    values = None

    def as_dict(self):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {CommonKeys.NAME: self.name, SOURCE: self.source},
        }


@attr.s
class Dataset(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.DATASET.value, init=False)
    values = None

    def as_dict(self):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {
                CommonKeys.NAME: self.name,
                CommonKeys.VALUES: self.values,
            },
        }


@attr.s
class ADARStream(FileWriterModule):
    writer_module = attr.ib(type=str, default=WriterModules.ADAR.value, init=False)
    array_size = attr.ib(type=list, default=None, init=False)

    def as_dict(self):
        module_dict = FileWriterModule.as_dict(self)
        if self.array_size:
            module_dict[NodeType.CONFIG][ARRAY_SIZE] = self.array_size
        return module_dict


class WriterModuleClasses(Enum):
    F142 = F142Stream
    EV42 = EV42Stream
    TDCTIME = TDCTStream
    NS10 = NS10Stream
    HS00 = FileWriterModule
    SENV = SENVStream
    LINK = Link
    DATASET = Dataset
    ADAR = ADARStream


module_class_dict = dict(
    zip([x.value for x in WriterModules], [x.value for x in WriterModuleClasses])
)


def create_fw_module_object(mod_type, configuration):
    fw_mod_obj = module_class_dict[mod_type]()
    if mod_type in [
        WriterModules.NS10.value,
        WriterModules.SENV.value,
        WriterModules.TDCTIME.value,
        WriterModules.F142.value,
        WriterModules.EV42.value,
        WriterModules.ADAR.value,
    ]:
        fw_mod_obj.topic = configuration[TOPIC]
        fw_mod_obj.source = configuration[SOURCE]
    elif mod_type == WriterModules.LINK.value:
        fw_mod_obj.name = configuration[CommonKeys.NAME]
        fw_mod_obj.source = configuration[SOURCE]
    elif mod_type == WriterModules.DATASET.value:
        fw_mod_obj.name = configuration[CommonKeys.NAME]
        fw_mod_obj.values = configuration[CommonKeys.VALUES]

    if mod_type in [WriterModules.F142.value, WriterModules.EV42.value]:
        if ADC_PULSE_DEBUG in configuration:
            fw_mod_obj.adc_pulse_debug = configuration[ADC_PULSE_DEBUG]
        if CUE_INTERVAL in configuration:
            fw_mod_obj.cue_interval = configuration[CUE_INTERVAL]
        if CHUNK_SIZE in configuration:
            fw_mod_obj.chunk_size = configuration[CHUNK_SIZE]

    if mod_type == WriterModules.ADAR.value:
        fw_mod_obj.array_size = configuration[ARRAY_SIZE]
    return fw_mod_obj


HS00TYPES = ["uint32", "uint64", "float", "double"]

DATA_TYPE = "data_type"
ERROR_TYPE = "error_type"
EDGE_TYPE = "edge_type"
SHAPE = "shape"


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
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {
                SOURCE: self.source,
                TOPIC: self.topic,
                DATA_TYPE: self.data_type,
                ERROR_TYPE: self.error_type,
                EDGE_TYPE: self.edge_type,
                SHAPE: self.shape,
            },
        }


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
