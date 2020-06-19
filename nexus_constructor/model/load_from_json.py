import json
import logging
from typing import Union

from PySide2.QtWidgets import QWidget

from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.ui_utils import show_warning_dialog

IGNORE = ["entry", "transformations", "NX_class"]


def _find_nx_class(entry: dict) -> str:
    if entry.get("name") == "NX_class":
        return entry.get("values")
    if entry.get("NX_class"):
        return entry.get("NX_class")
    return ""


def _read_nx_class(entry: Union[list, dict]) -> str:
    if isinstance(entry, list):
        for item in entry:
            return _find_nx_class(item)
    elif isinstance(entry, dict):
        return _find_nx_class(entry)


def _read_transformations(entry: list):
    for item in entry:
        if item.get("name") == "transformations":
            return item.get("children")

    return None


def _retrieve_children_list(json_dict: dict) -> list:
    try:
        return json_dict["nexus_structure"]["children"][0]["children"]
    except (KeyError, IndexError, TypeError):
        return []


def _validate_nx_class(nx_class: str) -> bool:

    if not nx_class:
        logging.warning("Unable to determine NXclass.")
        return False

    if nx_class not in COMPONENT_TYPES:
        logging.warning("NXclass does not match any known classes.")
        return False

    return True


class JSONReader:
    def __init__(self, parent: QWidget):

        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.parent = parent

    def load_model_from_json(self, filename: str) -> bool:

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
                logging.info("Unable to locate components in JSON file.")
                return False

            return all(self._read_json_object(child) for child in children_list)

    def _read_json_object(self, json_object: dict) -> bool:

        name = json_object.get("name")

        if name:

            nx_class = _read_nx_class(json_object.get("attributes"))

            if not _validate_nx_class(nx_class):
                return False

            if name == "NXinstrument":
                return True

            if nx_class == "NXsample":
                component = self.entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                self.entry.instrument.add_component(component)

            transformations = _read_transformations(json_object.get("children"))

            if not transformations:
                logging.info("Unable to find transformations entry for component.")
                return False

            for transformation in transformations:
                # todo: transformation reading
                pass

            return True

        return False
