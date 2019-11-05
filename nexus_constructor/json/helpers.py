import json
import numpy as np


def handle_non_std_types(Value):
    if type(Value) is np.bool_:
        return bool(Value)
    elif type(Value) is np.ndarray:
        return list(Value)
    raise (TypeError("Unknown type: {}".format(type(Value))))


def object_to_json_file(tree_dict, file):
    """
    Create a JSON file describing the NeXus file
    WARNING, output files can easily be 10 times the size of input NeXus file

    :param tree_dict: Root node of the tree.
    :param file: File object to store the tree in.
    """

    json.dump(tree_dict, file, indent=2, sort_keys=False, default=handle_non_std_types)
