import attr

from nexus_constructor.writer_modules import WriterModules


@attr.s
class Stream:
    topic = attr.ib(str)
    source = attr.ib(str)
    writer_module = attr.ib(
        str, validator=attr.validators.in_([e.value for e in WriterModules])
    )


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
    type = attr.ib()
    value_units = attr.ib()
    array_size = attr.ib(default=None)


HS00TYPES = ["uint32", "uint64", "float", "double"]


class HS00Stream(Stream):
    writer_module = WriterModules.HS00.value
    data_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    error_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    edge_type = attr.ib(type=str, validator=attr.validators.in_(HS00TYPES))
    shape = attr.ib(default=NotImplemented)
