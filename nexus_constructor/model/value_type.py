from typing import Union
import numpy as np


class ValueTypes:
    BYTE = "Byte"
    UBYTE = "UByte"
    SHORT = "Short"
    USHORT = "UShort"
    INT = "Integer"
    UINT = "UInteger"
    LONG = "Long"
    ULONG = "ULong"
    FLOAT = "Float"
    DOUBLE = "Double"
    STRING = "String"


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
