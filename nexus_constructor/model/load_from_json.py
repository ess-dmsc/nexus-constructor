import json
from typing import Union

from PySide2.QtWidgets import QWidget

from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.ui_utils import show_warning_dialog

NX_CLASS = "NX_class"
NX_INSTRUMENT = "NXInstrument"
NX_SAMPLE = "NXsample"


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


def _retrieve_children_list(json_dict: dict) -> list:
    """
    Attempts to retrieve the children from the JSON dictionary.
    :param json_dict: The JSON dictionary loaded by the user.
    :return: The children value is returned if it was found, otherwise an empty list is returned.
    """
    try:
        return json_dict["nexus_structure"]["children"][0]["children"]
    except (KeyError, IndexError, TypeError):
        return []


class JSONReader:
    def __init__(self, parent: QWidget):

        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.parent = parent
        self.warnings = []

    def load_model_from_json(self, filename: str) -> bool:
        """
        Tries to load a model from a JSON file.
        :param filename: The filename of the JSON file.
        :return: True if the model was loaded without problems, False otherwise.
        """
        with open(filename, "r") as json_file:

            json_data = json_file.read()

            try:
                json_dict = json.loads(json_data)
            except ValueError as exception:
                show_warning_dialog(
                    "Provided file not recognised as valid JSON",
                    "Invalid JSON",
                    f"{exception}",
                    self.parent,
                )
                return False

            children_list = _retrieve_children_list(json_dict)

            if not children_list:
                show_warning_dialog(
                    "Provided file not recognised as valid Instrument",
                    "Invalid JSON",
                    parent=self.parent,
                )
                return False

            for child in children_list:
                self._read_json_object(child)

            if self.warnings:
                show_warning_dialog(
                    "\n".join(self.warnings), "Invalid JSON", parent=self.parent,
                )
                return False

            return True

    def _read_json_object(self, json_object: dict):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object:  A component from the JSON dictionary.
        """
        name = json_object.get("name")

        if name:

            nx_class = _read_nx_class(json_object.get("attributes"))

            if nx_class == NX_INSTRUMENT:
                return

            if not self._validate_nx_class(name, nx_class):
                return

            if nx_class == NX_SAMPLE:
                component = self.entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                self.entry.instrument.add_component(component)
        else:
            self.warnings.append("Unable to find object name.")

    def _validate_nx_class(self, name: str, nx_class: str) -> bool:
        """
        Validates the NXclass by checking if it was found, and if it matches known NXclasses.
        :param nx_class: The NXclass string obtained from the dictionary.
        :return: True if the NXclass is valid, False otherwise.
        """
        if not nx_class:
            self.warnings.append(f"Unable to determine NXclass of component {name}.")
            return False

        if nx_class not in COMPONENT_TYPES:
            self.warnings.append(
                f"NXclass value {nx_class} for component {name} does not match any known classes."
            )
            return False

        return True
