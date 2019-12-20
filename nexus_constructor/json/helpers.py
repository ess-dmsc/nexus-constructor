import json
from typing import Dict, Any, List, Tuple

import h5py
import numpy as np


def handle_non_std_types(value):
    if type(value) is np.bool_:
        return bool(value)
    elif type(value) is np.ndarray:
        return list(value)
    elif type(value) is np.int8 or type(value) is np.int64:
        return int(value)
    raise (TypeError("Unknown type: {}".format(type(value))))


def object_to_json_file(tree_dict, file):
    """
    Create a JSON file describing the NeXus file
    WARNING, output files can easily be 10 times the size of input NeXus file

    :param tree_dict: Root node of the tree.
    :param file: File object to store the tree in.
    """

    json.dump(tree_dict, file, indent=2, sort_keys=False, default=handle_non_std_types)


def _separate_dot_field_group_hierarchy(
    item_dict: Dict[Any, Any],
    dots_in_field_name: List[str],
    item: Tuple[str, h5py.Group],
):
    previous_group = item_dict
    for subgroup in dots_in_field_name:
        # do not overwrite a group unless it doesn't yet exist
        if subgroup not in previous_group:
            previous_group[subgroup] = dict()
        if subgroup == dots_in_field_name[-1]:
            # set the value of the field to the last item in the list
            previous_group[subgroup] = item[...][()]
        previous_group = previous_group[subgroup]
