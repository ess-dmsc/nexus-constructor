from enum import Enum
import numpy as np


class FieldType(Enum):
    scalar_dataset = "Scalar dataset"
    array_dataset = "Array dataset"
    kafka_stream = "Kafka stream"
    link = "Link"
    nx_class = "NX class/group"


class DatasetType(Enum):
    byte = "Byte"
    ubyte = "Unsigned Byte"
    short = "Short"
    ushort = "Unsigned Short"
    int = "Integer"
    uint = "Unsigned Integer"
    long = "Long"
    ulong = "Unsigned Long"
    float = "Float"
    double = "Double"
    string = "String"


python_to_hdf5_scalar = {
    DatasetType.byte: np.byte,
    DatasetType.ubyte: np.ubyte,
    DatasetType.short: np.short,
    DatasetType.ushort: np.ushort,
    DatasetType.int: np.intc,
    DatasetType.uint: np.uintc,
    DatasetType.long: np.int_,
    DatasetType.ulong: np.uint,
    DatasetType.float: np.single,
    DatasetType.double: np.double,
    DatasetType.string: object,
}
