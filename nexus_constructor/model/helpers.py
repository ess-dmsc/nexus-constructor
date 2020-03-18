from typing import Any, List


def find_item_index(list_to_look_in: List[Any], item_name: str):
    """
    Returns the index of the first item in the list that matches the given name.
    :param list_to_look_in:
    :param item_name:
    :return: The index of the object if any are found.
    """

    found = [x for x in list_to_look_in if x.name == item_name]
    return list_to_look_in.index(found[0]) if found else None


def get_item(list_to_look_in: List[Any], item_name: str) -> Any:
    return list_to_look_in[find_item_index(list_to_look_in, item_name)]


def remove_item(list_to_remove_from: List[Any], item_name: str):
    list_to_remove_from.pop(find_item_index(list_to_remove_from, item_name))


def set_item(list_to_look_in: List[Any], item_name: str, new_value: Any):
    index = find_item_index(list_to_look_in, item_name)
    if index is not None:
        list_to_look_in[index] = new_value
    else:
        list_to_look_in.append(new_value)
