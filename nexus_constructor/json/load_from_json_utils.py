from typing import Union

NX_CLASS = "NX_class"


def _find_nx_class(entry: dict) -> str:
    """
    Attempts to find the NXclass of a component in the dictionary.
    :param entry: The dictionary containing the NXclass information for a given component.
    :return: The NXclass if it was able to find it, otherwise an empty string is returned.
    """
    if entry.get("name") == NX_CLASS:
        return entry.get("values")
    if entry.get(NX_CLASS):
        return entry.get(NX_CLASS)
    return ""


def _read_nx_class(entry: Union[list, dict]) -> str:
    """
    Attempts to determine the NXclass of a component in a list/dictionary.
    :param entry: A dictionary of list of a dictionary containing NXclass information.
    :return: The NXclass if it can be found, otherwise an emtpy string is returned.
    """
    if isinstance(entry, list):
        for item in entry:
            return _find_nx_class(item)
    elif isinstance(entry, dict):
        return _find_nx_class(entry)
