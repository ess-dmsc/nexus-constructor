import json
import logging

from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.ui_utils import show_warning_dialog

IGNORE = ["entry", "instrument", "transformations", "NX_class"]


def _read_nx_class(entry: list):

    for item in entry:
        if item.get("name") == "NX_class":
            return item.get("values")

    return None


def _read_transformations(entry: list):

    for item in entry:
        if item.get("name") == "transformations":
            return item.get("children")

    return None


class JSONReader:
    def __init__(self, parent):

        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.parent = parent

    def load_model_from_json(self, filename: str):

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

            try:
                children_list = json_dict["nexus_structure"]["children"][0]["children"]
            except KeyError:
                return False

            return all(self._read_json_object(child) for child in children_list)

    def _read_json_object(self, json_entry: dict):

        name = json_entry.get("name")

        if name == "instrument":
            return True

        elif name and name not in IGNORE:

            nx_class = _read_nx_class(json_entry.get("attributes"))

            if nx_class is None:
                logging.warning("Unable to determine NXclass.")
                return False

            elif nx_class == "NX_sample":
                component = self.entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                self.entry.instrument.add_component(component)

            transformations = _read_transformations(json_entry.get("children"))

            if transformations is None:
                logging.warning("Unable to find transformations entry for component.")
                return False
            else:
                for transformation in transformations:
                    # todo: transformation reading
                    pass

            return True

        return False
