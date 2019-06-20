from enum import Enum


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
