from typing import Any, Dict, List, Optional, Union

from nexus_constructor.common_attrs import (
    GEOMETRY_GROUP_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
)

DEPENDS_ON_IGNORE = [None, "."]


def _find_shape_information(children: List[Dict]) -> Union[Dict, None]:
    """
    Tries to get the shape information from a component.
    :param children: The list of dictionaries.
    :return: The shape attribute if it could be found, otherwise None.
    """
    value = None
    for item in children:
        try:
            if item[CommonKeys.NAME] in [
                SHAPE_GROUP_NAME,
                PIXEL_SHAPE_GROUP_NAME,
                GEOMETRY_GROUP_NAME,
            ]:
                value = item
        except KeyError:
            pass
    return value


def _find_depends_on_path(items: List[Dict], name: str) -> Optional[str]:
    if not isinstance(items, list):
        raise RuntimeError(
            f'List of children in node with the name "{name}" is not a list.'
        )
    for item in items:
        try:
            config = item[NodeType.CONFIG]
            if config[CommonKeys.NAME] != CommonAttrs.DEPENDS_ON:
                continue
            return config[CommonKeys.VALUES]
        except KeyError:
            pass  # Not all items has a config node, ignore those that do not.
    return None


def _find_attribute_from_dict(attribute_name: str, entry: dict) -> Any:
    """
    Attempts to fing an attribute in a dictionary by looking for the value associated with the attribute key,
    or by looking for the "values" fields.
    :param entry: The dictionary containing the information.
    :return: The attribute value if it could be found, otherwise None.
    """
    if entry.get(CommonKeys.NAME) == attribute_name:
        return entry.get(CommonKeys.VALUES)
    if entry.get(attribute_name):
        return entry.get(attribute_name)
    return None


def _find_attribute_from_list_or_dict(
    attribute_name: str,
    entry: Union[list, dict],
) -> Any:
    """
    Attempts to determine the value of an attribute in a dictionary or a list of dictionaries.
    :param entry: A dictionary of list of a dictionaries.
    :return: The attribute value if it can be found, otherwise None.
    """
    if isinstance(entry, list):
        for item in entry:
            attribute = _find_attribute_from_dict(attribute_name, item)
            if attribute:
                return attribute
        return None
    elif isinstance(entry, dict):
        return _find_attribute_from_dict(attribute_name, entry)


def _find_nx_class(entry: Union[list, dict]) -> str:
    """
    Tries to find the NX class value from a dictionary or a list of dictionaries.
    :param entry: A dictionary or list of dictionaries.
    :return: The NXclass if it could be found, otherwise an empty string is returned.
    """
    nx_class = _find_attribute_from_list_or_dict(CommonAttrs.NX_CLASS, entry)
    return nx_class if nx_class is not None else ""
