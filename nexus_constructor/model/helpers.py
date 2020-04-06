from typing import Any, List

from nexus_constructor.model.attribute import FieldAttribute


def find_item_index(list_to_look_in: List[Any], item_name: str):
    """
    Returns the index of the first item in the list that matches the given name.
    :param list_to_look_in: list of elements that contain name attributes
    :param item_name: the item name to actually search for
    :return: The index of the object if any are found.
    """
    for count, element in enumerate(list_to_look_in):
        if element.name == item_name:
            return count


def get_item(list_to_look_in: List[Any], item_name: str) -> Any:
    """
    Given an item name, search the given list and return the item.
    :param list_to_look_in: list containing elements that have a name attribute
    :param item_name: the name of the item
    :return: the item itself
    """
    return list_to_look_in[find_item_index(list_to_look_in, item_name)]


def remove_item(list_to_remove_from: List[Any], item_name: str):
    """
    Given an item name, remove it from the list if present.
    :param list_to_remove_from: list containing elements that have a name attribute
    :param item_name: the name of the item
    """
    list_to_remove_from.pop(find_item_index(list_to_remove_from, item_name))


def set_item(list_to_look_in: List[Any], item_name: str, new_value: Any):
    """
    Given an item name, either overwrite the current entry or just append the item to the list.
    :param list_to_look_in: list containing elements that have a name attribute
    :param item_name: the name of the item
    :param new_value: the item
    """
    index = find_item_index(list_to_look_in, item_name)
    if index is not None:
        list_to_look_in[index] = new_value
    else:
        list_to_look_in.append(new_value)


def set_attribute_value(
    attributes_list: List[FieldAttribute], attribute_name: str, attribute_value: Any
):
    set_item(
        attributes_list, attribute_name, FieldAttribute(attribute_name, attribute_value)
    )


def get_attribute_value(attributes_list: List[FieldAttribute], attribute_name: str):
    return get_item(attributes_list, attribute_name).values
