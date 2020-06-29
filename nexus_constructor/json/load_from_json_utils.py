from typing import Union, Any

NX_CLASS = "NX_class"


def _find_attribute_from_dict(attribute_name: str, entry: dict) -> Any:
    """
    Attempts to find the NXclass of a component in the dictionary. todo: update docstring
    :param entry: The dictionary containing the NXclass information for a given component.
    :return: The NXclass if it was able to find it, otherwise an empty string is returned.
    """
    if entry.get("name") == attribute_name:
        return entry.get("values")
    if entry.get(attribute_name):
        return entry.get(attribute_name)
    return ""


def _find_attribute_from_list_or_dict(
    attribute_name: str, entry: Union[list, dict],
) -> Any:
    """
    Attempts to determine the NXclass of a component in a list/dictionary. todo: update docstring
    :param entry: A dictionary of list of a dictionary containing NXclass information.
    :return: The NXclass if it can be found, otherwise an emtpy string is returned.
    """
    if isinstance(entry, list):
        for item in entry:
            return _find_attribute_from_dict(attribute_name, item)
    elif isinstance(entry, dict):
        return _find_attribute_from_dict(attribute_name, entry)


def _find_nx_class(entry: Union[list, dict]) -> str:
    return _find_attribute_from_list_or_dict(NX_CLASS, entry)
