import numpy as np


def handle_non_std_types(value):
    if type(value) is np.bool_:
        return bool(value)
    elif type(value) is np.ndarray:
        return list(value)
    elif type(value) is np.int8 or type(value) is np.int64:
        return int(value)
    try:
        return int(value)
    except ValueError:
        pass
    raise (TypeError("Unknown type: {}".format(type(value))))
