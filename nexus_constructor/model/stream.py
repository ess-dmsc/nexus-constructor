from enum import Enum

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
class StreamGroup(Group):
    type = attr.ib(init=False, default="stream", type=str)

    def __setitem__(self, key, value):
        self.children.append(value)

    def __getitem__(self, item):
        """This is not simple as they do not have a name - we could do this by using a private member"""
        raise NotImplementedError


@attr.s
class NS10Stream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.NS10.value, init=False)


@attr.s
class SENVStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.SENV.value, init=False)


@attr.s
class TDCTStream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(type=str, default=WriterModules.TDCTIME.value, init=False)


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


HS00TYPES = ["uint32", "uint64", "float", "double"]


@attr.s
class HS00Stream:
    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    data_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    error_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    edge_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    shape = attr.ib()
    writer_module = attr.ib(type=str, default=WriterModules.HS00.value, init=False)
