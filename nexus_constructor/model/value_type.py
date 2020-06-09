from typing import Union
import numpy as np

# Allowed types for dataset and attribute values
VALUE_TYPE = {
    "Byte": np.byte,
    "UByte": np.ubyte,
    "Short": np.short,
    "UShort": np.ushort,
    "Integer": np.intc,
    "UInteger": np.uintc,
    "Long": np.int_,
    "ULong": np.uint,
    "Float": np.single,
    "Double": np.double,
    "String": str,
}

# For use in type hints
ValueType = Union[np.ndarray, str]
