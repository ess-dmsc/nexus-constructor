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


PYTHON_TO_HDF5 = {
    DatasetType.byte.value: np.byte,
    DatasetType.ubyte.value: np.ubyte,
    DatasetType.short.value: np.short,
    DatasetType.ushort.value: np.ushort,
    DatasetType.int.value: np.intc,
    DatasetType.uint.value: np.uintc,
    DatasetType.long.value: np.int_,
    DatasetType.ulong.value: np.uint,
    DatasetType.float.value: np.single,
    DatasetType.double.value: np.double,
    DatasetType.string.value: object,
}
