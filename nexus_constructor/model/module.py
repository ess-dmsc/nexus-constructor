from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Union

import attr
import h5py
import numpy as np

from nexus_constructor.common_attrs import CommonKeys, NodeType
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.helpers import get_absolute_path

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
    F144 = "f144"
    EV42 = "ev42"
    EV44 = "ev44"
    TDCTIME = "tdct"
    NS10 = "ns10"
    HS01 = "hs01"
    SE00 = "se00"
    SENV = "senv"
    LINK = "link"
    DATASET = "dataset"
    ADAR = "ADAr"


class StreamModules(Enum):
    F142 = "f142"
    F144 = "f144"
    EV42 = "ev42"
    EV44 = "ev44"
    TDCTIME = "tdct"
    NS10 = "ns10"
    SE00 = "se00"
    SENV = "senv"
    ADAR = "ADAr"
    HS01 = "hs01"


@attr.s
class FileWriterModule(ABC):
    attributes = attr.ib(type=Attributes, factory=Attributes, init=False)
    writer_module = attr.ib(type=str, init=False)
    parent_node = attr.ib(type="Group")

    def as_dict(self, error_collector: List[str]):
        raise NotImplementedError()

    def as_nexus(self, nexus_node, error_collector: List[str]):
        pass

    @property
    def absolute_path(self):
        return get_absolute_path(self)


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
class SE00Stream(StreamModule):
    writer_module = attr.ib(type=str, default=WriterModules.SE00.value, init=False)


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
class EV44Stream(EV42Stream):
    writer_module = attr.ib(type=str, default=WriterModules.EV44.value, init=False)


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
class F144Stream(F142Stream):
    writer_module = attr.ib(type=str, default=WriterModules.F144.value, init=False)


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

    def as_nexus(self, nexus_node, error_collector: List[str]):
        if self.source and self.name:
            nexus_node[self.name] = h5py.SoftLink(self.source)


@attr.s
class Dataset(FileWriterModule):
    name = attr.ib(type=str)
    values = attr.ib(type=Union[List[ValueType], ValueType])
    type = attr.ib(type=str, default=None)
    writer_module = attr.ib(type=str, default=WriterModules.DATASET.value, init=False)

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

    def as_nexus(self, nexus_node, error_collector: List[str]):
        nexus_dataset = nexus_node.create_dataset(self.name, data=self.values)
        for attribute in self.attributes:
            nexus_dataset.attrs[attribute.name] = attribute.values

    def _cast_to_type(self, data):
        return JsonSerialisableType.from_type(self.type)(data)


@attr.s
class ADARStream(StreamModule):
    array_size = attr.ib(type=list, init=False)
    writer_module = attr.ib(type=str, default=WriterModules.ADAR.value, init=False)

    def as_dict(self, error_collector: List[str]):
        module_dict = StreamModule.as_dict(self, error_collector)
        if self.array_size:
            module_dict[NodeType.CONFIG][ARRAY_SIZE] = self.array_size
        return module_dict


HS01TYPES = ["uint32", "uint64", "float", "double"]
ERROR_TYPE = "error_type"
EDGE_TYPE = "edge_type"
SHAPE = "shape"
SIZE = "size"
LABEL = "label"
UNIT = "unit"
EDGES = "edges"
DATASET_NAME = "dataset_name"


@attr.s
class HS01Shape:
    size = attr.ib(type=int)
    label = attr.ib(type=str)
    unit = attr.ib(type=str)
    edges = attr.ib(type=List[int])
    dataset_name = attr.ib(type=str)

    def as_dict(self, error_collector: List[str]):
        return {
            SIZE: self.size,
            LABEL: self.label,
            UNIT: self.unit,
            EDGES: self.edges,
            DATASET_NAME: self.dataset_name,
        }


@attr.s
class HS01Stream(StreamModule):
    type = attr.ib(type=str, default=None)
    error_type = attr.ib(type=str, default=None)
    edge_type = attr.ib(type=str, default=None)
    shape = attr.ib(type=List[HS01Shape], default=[])
    writer_module = attr.ib(type=str, default=WriterModules.HS01.value, init=False)

    def as_dict(self, error_collector: List[str]):
        module_dict = StreamModule.as_dict(self, error_collector)
        if self.error_type:
            module_dict[NodeType.CONFIG][ERROR_TYPE] = self.error_type
        if self.edge_type:
            module_dict[NodeType.CONFIG][EDGE_TYPE] = self.edge_type
        if self.shape:
            shape_dicts = []
            for item in self.shape:
                shape_dicts.append(item.as_dict(error_collector))
            module_dict[NodeType.CONFIG][SHAPE] = shape_dicts
        if self.type:
            module_dict[NodeType.CONFIG][CommonKeys.TYPE] = self.type
        return module_dict


class WriterModuleClasses(Enum):
    F142 = F142Stream
    F144 = F144Stream
    EV42 = EV42Stream
    EV44 = EV44Stream
    TDCTIME = TDCTStream
    NS10 = NS10Stream
    HS01 = HS01Stream
    SE00 = SE00Stream
    SENV = SENVStream
    LINK = Link
    DATASET = Dataset
    ADAR = ADARStream


module_class_dict = dict(
    zip([x.value for x in WriterModules], [x.value for x in WriterModuleClasses])
)


def create_hs01_shape(shape: List[Dict]) -> List[HS01Shape]:
    shape_list = []
    for item in shape:
        shape_list.append(
            HS01Shape(
                item[SIZE], item[LABEL], item[UNIT], item[EDGES], item[DATASET_NAME]
            )
        )
    return shape_list


def create_fw_module_object(mod_type, configuration, parent_node):
    fw_mod_class = module_class_dict[mod_type]
    if mod_type in [
        WriterModules.NS10.value,
        WriterModules.SE00.value,
        WriterModules.SENV.value,
        WriterModules.SE00.value,
        WriterModules.TDCTIME.value,
        WriterModules.EV42.value,
        WriterModules.EV44.value,
        WriterModules.ADAR.value,
        WriterModules.HS01.value,
    ]:
        fw_mod_obj = fw_mod_class(
            topic=configuration[TOPIC],
            source=configuration[SOURCE],
            parent_node=parent_node,
        )
    elif mod_type in [WriterModules.F142.value, WriterModules.F144.value]:
        schema_type = None
        if CommonKeys.TYPE in configuration:
            schema_type = configuration[CommonKeys.TYPE]
        elif CommonKeys.DATA_TYPE in configuration:
            schema_type = configuration[CommonKeys.DATA_TYPE]
        fw_mod_obj = fw_mod_class(
            topic=configuration[TOPIC],
            source=configuration[SOURCE],
            parent_node=parent_node,
            type=schema_type,
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
        if CommonKeys.DATA_TYPE in configuration:
            dtype = configuration[CommonKeys.DATA_TYPE]
        elif CommonKeys.TYPE in configuration:
            dtype = configuration[CommonKeys.TYPE]
        else:
            dtype = "string"
        fw_mod_obj = fw_mod_class(
            name=configuration[CommonKeys.NAME],
            values=configuration[CommonKeys.VALUES],
            parent_node=parent_node,
            type=dtype,
        )

    if mod_type in [
        WriterModules.F142.value,
        WriterModules.F144.value,
        WriterModules.EV42.value,
        WriterModules.EV44.value,
    ]:
        if CUE_INTERVAL in configuration:
            fw_mod_obj.cue_interval = configuration[CUE_INTERVAL]
        if CHUNK_SIZE in configuration:
            fw_mod_obj.chunk_size = configuration[CHUNK_SIZE]
        if mod_type in [WriterModules.EV42.value, WriterModules.EV44.value]:
            if ADC_PULSE_DEBUG in configuration:
                fw_mod_obj.adc_pulse_debug = configuration[ADC_PULSE_DEBUG]
    elif mod_type == WriterModules.ADAR.value:
        fw_mod_obj.array_size = configuration[ARRAY_SIZE]
    elif mod_type == WriterModules.HS01.value:
        if ERROR_TYPE in configuration:
            fw_mod_obj.error_type = configuration[ERROR_TYPE]
        if EDGE_TYPE in configuration:
            fw_mod_obj.edge_type = configuration[EDGE_TYPE]
        if CommonKeys.TYPE in configuration:
            fw_mod_obj.type = configuration[CommonKeys.TYPE]
        if SHAPE in configuration:
            fw_mod_obj.shape = create_hs01_shape(configuration[SHAPE])

    return fw_mod_obj


Stream = StreamModule
