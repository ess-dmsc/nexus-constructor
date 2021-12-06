from typing import Union

import numpy as np


class ValueTypes:
    BYTE = "byte"
    UBYTE = "ubyte"
    SHORT = "int16"
    USHORT = "uint16"
    INT = "int32"
    UINT = "uint32"
    LONG = "int64"
    ULONG = "uint64"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"


# Allowed types for dataset and attribute values
VALUE_TYPE_TO_NP = {
    ValueTypes.BYTE: np.byte,
    ValueTypes.UBYTE: np.ubyte,
    ValueTypes.SHORT: np.short,
    ValueTypes.USHORT: np.ushort,
    ValueTypes.INT: np.intc,
    ValueTypes.UINT: np.uintc,
    ValueTypes.LONG: np.int_,
    ValueTypes.ULONG: np.uint,
    ValueTypes.FLOAT: np.single,
    ValueTypes.DOUBLE: np.double,
    ValueTypes.STRING: str,
}


# For use in type hints
ValueType = Union[np.ndarray, str]


INT_TYPES = [
    ValueTypes.INT,
    ValueTypes.UINT,
    ValueTypes.LONG,
    ValueTypes.ULONG,
    ValueTypes.USHORT,
    ValueTypes.SHORT,
]
FLOAT_TYPES = [ValueTypes.FLOAT, ValueTypes.DOUBLE]


cast_to_json_serialisable_type = (
    lambda dtype: int
    if dtype in INT_TYPES
    else (
        float
        if dtype in FLOAT_TYPES
        else (str if dtype == ValueTypes.STRING else lambda y: y)  # type: ignore
    )
)
