import attr
import uuid
from nexus_constructor.writer_modules import WriterModules


@attr.s
class Stream:
    """Base class for all stream objects"""

    topic = attr.ib(type=str)
    source = attr.ib(type=str)
    writer_module = attr.ib(
        type=str, validator=attr.validators.in_([e.value for e in WriterModules])
    )
    name = attr.ib(type=str, default=str(uuid.uuid4()))


class EV42Stream(Stream):
    writer_module = WriterModules.EV42.value


class NS10Stream(Stream):
    writer_module = WriterModules.NS10.value


class SENVStream(Stream):
    writer_module = WriterModules.SENV.value


class TDCTStream(Stream):
    writer_module = WriterModules.TDCTIME.value


# TODO: optional fields
class F142Stream(Stream):
    writer_module = WriterModules.F142.value
    type = attr.ib(type=str)
    value_units = attr.ib(type=str)
    array_size = attr.ib(type=float, default=None)


HS00TYPES = ["uint32", "uint64", "float", "double"]


class HS00Stream(Stream):
    writer_module = WriterModules.HS00.value
    data_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    error_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    edge_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    shape = attr.ib(default=NotImplemented)
