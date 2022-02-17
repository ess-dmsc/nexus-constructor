from typing import TYPE_CHECKING, Any, List, Union

if TYPE_CHECKING:
    from nexus_constructor.model.attributes import Attributes
    from nexus_constructor.model.group import Group
    from nexus_constructor.model.module import FileWriterModule


def __find_item_index(list_to_look_in: List[Any], item_name: str):
    """
    Returns the index of the first item in the list that matches the given name.
    :param list_to_look_in: list of elements that contain name attributes
    :param item_name: the item name to actually search for
    :return: The index of the object if any are found.
    """
    for count, element in enumerate(list_to_look_in):
        try:
            if element.name == item_name:
                return count
        except AttributeError:
            continue
    return None


def _get_item(list_to_look_in: List[Any], item_name: str) -> Any:
    """
    Given an item name, search the given list and return the item if present. Otherwise return None.
    :param list_to_look_in: list containing elements that have a name attribute
    :param item_name: the name of the item
    :return: the item itself
    """
    index = __find_item_index(list_to_look_in, item_name)
    return list_to_look_in[index] if index is not None else None


def _remove_item(list_to_remove_from: List[Any], item_name: str):
    """
    Given an item name, remove it from the list if present.
    :param list_to_remove_from: list containing elements that have a name attribute
    :param item_name: the name of the item
    """
    try:
        list_to_remove_from.pop(__find_item_index(list_to_remove_from, item_name))
    except TypeError:
        pass


def _set_item(
    parent: Union["Attributes", "FileWriterModule", "Group"],  # noqa: F821
    list_to_look_in: List[Any],
    item_name: str,
    new_value: Any,
):
    """
    Given an item name, either overwrite the current entry or just append the item to the list.
    :param list_to_look_in: list containing elements that have a name attribute
    :param item_name: the name of the item
    :param new_value: the item
    """
    index = __find_item_index(list_to_look_in, item_name)
    if index is not None:
        list_to_look_in[index] = new_value
    else:
        list_to_look_in.append(new_value)
    if hasattr(new_value, "parent_node"):
        new_value.parent_node = parent


def get_absolute_path(node: Any):
    path = f"/{node.name}"
    while node.parent_node is not None:
        path = f"/{node.parent_node.name}{path}"
        node = node.parent_node
    return path


def _generate_incremental_name(base_name, transforms_list):
    number = 1
    while _get_item(transforms_list, f"{base_name}_{number}") is not None:
        number += 1
    return f"{base_name}_{number}"
