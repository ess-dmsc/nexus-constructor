from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING, List, Union

import attr
import numpy as np

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.attributes import Attributes

if TYPE_CHECKING:
    from nexus_constructor.model.group import Group  # noqa: F401

from nexus_constructor.model.value_type import JsonSerialisableType, ValueType

ARRAY_SIZE = "array_size"
VALUE_UNITS = "value_units"
CHUNK_SIZE = "chunk_size"
CUE_INTERVAL = "cue_interval"
ADC_PULSE_DEBUG = "adc_pulse_debug"
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


class StreamModules(Enum):
    F142 = "f142"
    EV42 = "ev42"
    TDCTIME = "tdct"
    NS10 = "ns10"
    SENV = "senv"
    ADAR = "ADAr"


@attr.s(eq=False)
class FileWriterModule(ABC):
    attributes = attr.ib(type=Attributes, factory=Attributes, init=False)
    writer_module = attr.ib(type=str, init=False)
    parent_node = attr.ib(type="Group")

    def as_dict(self, error_collector: List[str]):
        raise NotImplementedError

    def get_name(self) -> str:
        return self.writer_module


@attr.s
class StreamModule(FileWriterModule):
    source = attr.ib(type=str)
    topic = attr.ib(type=str)

    def as_dict(self, error_collector: List[str]):
        return_dict = {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {SOURCE: self.source, TOPIC: self.topic},
        }
        if self.attributes:
            return_dict[CommonKeys.ATTRIBUTES] = self.attributes.as_dict(
                error_collector
            )
        return return_dict


@attr.s
class NS10Stream(StreamModule):
    writer_module = attr.ib(type=str, default=WriterModules.NS10.value, init=False)


@attr.s
class SENVStream(StreamModule):
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)


@attr.s
class TDCTStream(StreamModule):
    writer_module = attr.ib(type=str, default=WriterModules.TDCTIME.value, init=False)


@attr.s
class EV42Stream(StreamModule):
    writer_module = attr.ib(type=str, default=WriterModules.EV42.value, init=False)
    adc_pulse_debug = attr.ib(type=bool, default=None)
    cue_interval = attr.ib(type=int, default=None)
    chunk_size = attr.ib(type=int, default=None)

    def as_dict(self, error_collector: List[str]):
        module_dict = StreamModule.as_dict(self, error_collector)
        if self.adc_pulse_debug:
            module_dict[NodeType.CONFIG][ADC_PULSE_DEBUG] = self.adc_pulse_debug
        if self.chunk_size:
            module_dict[NodeType.CONFIG][CHUNK_SIZE] = self.chunk_size
        if self.cue_interval:
            module_dict[NodeType.CONFIG][CUE_INTERVAL] = self.cue_interval
        return module_dict


@attr.s
class F142Stream(StreamModule):
    type = attr.ib(type=str)
    cue_interval = attr.ib(type=int, default=None)
    chunk_size = attr.ib(type=int, default=None)
    value_units = attr.ib(type=str, default=None)
    array_size = attr.ib(type=list, default=None)
    writer_module = attr.ib(type=str, default=WriterModules.F142.value, init=False)

    def as_dict(self, error_collector: List[str]):
        module_dict = StreamModule.as_dict(self, error_collector)
        if self.type:
            module_dict[NodeType.CONFIG][CommonKeys.DATA_TYPE] = self.type
        if self.value_units:
            module_dict[NodeType.CONFIG][VALUE_UNITS] = self.value_units
        if self.array_size:
            module_dict[NodeType.CONFIG][ARRAY_SIZE] = self.array_size
        if self.chunk_size:
            module_dict[NodeType.CONFIG][CHUNK_SIZE] = self.chunk_size
        if self.cue_interval:
            module_dict[NodeType.CONFIG][CUE_INTERVAL] = self.cue_interval
        return module_dict


@attr.s
class Link(FileWriterModule):
    name = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.LINK.value, init=False)
    values = None

    def as_dict(self, error_collector: List[str]):
        return {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {CommonKeys.NAME: self.name, SOURCE: self.source},
        }


@attr.s(eq=False)
class Dataset(FileWriterModule):
    name = attr.ib(type=str)
    values = attr.ib(type=Union[List[ValueType], ValueType])
    type = attr.ib(type=str, default=None)
    writer_module = attr.ib(type=str, default=WriterModules.DATASET.value, init=False)

    def __str__(self) -> str:
        return f'Dataset(name="{self.name}", parent="{self.parent_node.name}", type={self.type})'

    def as_dict(self, error_collector: List[str]):
        values = self.values
        if np.isscalar(values):
            try:
                values = self._cast_to_type(values)
            except ValueError as e:
                error_collector.append(
                    f'Error when casting the string "{self.values}" to type "{self.type}". The exception message was: {e}'
                )
                return {}
        elif isinstance(values, np.ndarray):
            values = values.tolist()

        return_dict = {
            CommonKeys.MODULE: self.writer_module,
            NodeType.CONFIG: {CommonKeys.NAME: self.name, CommonKeys.VALUES: values},
        }

        if self.type:
            return_dict[NodeType.CONFIG][CommonKeys.TYPE] = self.type  # type: ignore
        if self.attributes:
            return_dict[CommonKeys.ATTRIBUTES] = self.attributes.as_dict(
                error_collector
            )
        return return_dict

    def _cast_to_type(self, data):
        return JsonSerialisableType.from_type(self.type)(data)

    def get_name(self) -> str:
        return self.name


@attr.s
class ADARStream(StreamModule):
    array_size = attr.ib(type=list, init=False)
    writer_module = attr.ib(type=str, default=WriterModules.ADAR.value, init=False)

    def as_dict(self, error_collector: List[str]):
        module_dict = StreamModule.as_dict(self, error_collector)
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


def create_fw_module_object(mod_type, configuration, parent_node):
    fw_mod_class = module_class_dict[mod_type]
    if mod_type in [
        WriterModules.NS10.value,
        WriterModules.SENV.value,
        WriterModules.TDCTIME.value,
        WriterModules.EV42.value,
        WriterModules.ADAR.value,
    ]:
        fw_mod_obj = fw_mod_class(
            topic=configuration[TOPIC],
            source=configuration[SOURCE],
            parent_node=parent_node,
        )
    elif mod_type == WriterModules.F142.value:
        f142_type = None
        if CommonKeys.TYPE in configuration:
            f142_type = configuration[CommonKeys.TYPE]
        fw_mod_obj = fw_mod_class(
            topic=configuration[TOPIC],
            source=configuration[SOURCE],
            parent_node=parent_node,
            type=f142_type,
        )
        if ARRAY_SIZE in configuration:
            fw_mod_obj.array_size = configuration[ARRAY_SIZE]
        if VALUE_UNITS in configuration:
            fw_mod_obj.value_units = configuration[VALUE_UNITS]
    elif mod_type == WriterModules.LINK.value:
        fw_mod_obj = fw_mod_class(
            name=configuration[CommonKeys.NAME],
            source=configuration[SOURCE],
            parent_node=parent_node,
        )
    elif mod_type == WriterModules.DATASET.value:
        fw_mod_obj = fw_mod_class(
            name=configuration[CommonKeys.NAME],
            values=configuration[CommonKeys.VALUES],
            parent_node=parent_node,
        )

    if mod_type in [WriterModules.F142.value, WriterModules.EV42.value]:
        if CUE_INTERVAL in configuration:
            fw_mod_obj.cue_interval = configuration[CUE_INTERVAL]
        if CHUNK_SIZE in configuration:
            fw_mod_obj.chunk_size = configuration[CHUNK_SIZE]

    if mod_type == WriterModules.EV42.value:
        if ADC_PULSE_DEBUG in configuration:
            fw_mod_obj.adc_pulse_debug = configuration[ADC_PULSE_DEBUG]

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

    def as_dict(self, error_collector: List[str]):
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


Stream = StreamModule
