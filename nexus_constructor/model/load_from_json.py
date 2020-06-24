import json
from typing import Union, Any

from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QWidget

from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.ui_utils import show_warning_dialog

NX_CLASS = "NX_class"
NX_INSTRUMENT = "NXinstrument"
NX_SAMPLE = "NXsample"
NX_TRANSFORMATION = "NXtransformation"

TRANSFORMATION_MAP = {
    "translation": TransformationType.TRANSLATION,
    "rotation": TransformationType.ROTATION,
}


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


def _contains_transformations(entry: dict) -> bool:
    """
    Determines if a component contains transformations.
    :param entry: The component's JSON dictionary.
    :return: True if the component has transformations, False otherwise.
    """
    try:
        for attribute in entry["attributes"]:
            if NX_TRANSFORMATION in _read_nx_class(attribute):
                return True
    except KeyError:
        return False
    return False


def _retrieve_children_list(json_dict: dict) -> list:
    """
    Attempts to retrieve the children from the JSON dictionary.
    :param json_dict: The JSON dictionary loaded by the user.
    :return: The children value is returned if it was found, otherwise an empty list is returned.
    """
    try:
        entry = json_dict["nexus_structure"]["children"][0]
        return entry["children"]
    except (KeyError, IndexError, TypeError):
        return []


class TransformationReader:
    def __init__(self, parent_component: Component, entry: list):
        self.parent_component = parent_component
        self.entry = entry
        self.warnings = []

    def add_transformations_to_component(self):
        """
        Attempts to construct Transformation objects using information from the JSON dictionary and then add them to the
        parent component.
        """
        for item in self.entry:
            if _contains_transformations(item):
                self._create_transformations(item.get("children"))

    def _get_transformation_property(
        self, property_name: str, json_transformation: dict, failure_value: Any = None
    ):
        """
        Tries to find a certain property of a transformation from dictionary.
        :param property_name: The name of the property fields.
        :param json_transformation: The dictionary to look for the property in.
        :param failure_value: The value to return if the property cannot be found.
        :return: Returns json_transformation[property_name] if this exists in the dictionary, otherwise failure_value is
        returned.
        """
        try:
            return json_transformation[property_name]
        except KeyError:
            self.warnings.append(
                f"Cannot find {property_name} for transformation in component"
                f" {self.parent_component.name}."
            )
            return failure_value

    def _find_property_in_list(
        self,
        property_name: str,
        transformation_name: str,
        attributes_list: list,
        failure_value: Any = None,
    ):
        """
        Searches the dictionaries in a list to see if one of them has a given property.
        :param property_name: The name of the property that is being looked for.
        :param transformation_name: The name of the transformation that is being constructed.
        :param attributes_list: The list of dictionaries.
        :param failure_value: The value to return if the property is not contained in any of the dictionaries.
        :return: The value of the property if is is found in the list, otherwise the failure value is returned.
        """
        for attribute in attributes_list:
            try:
                if attribute["name"] == property_name:
                    return attribute["values"]
            except KeyError:
                continue
        self.warnings.append(
            f"Unable to find {property_name} property in transformation"
            f" {transformation_name} from component {self.parent_component.name}"
        )
        return failure_value

    def _create_transformations(self, json_transformations: list):
        """
        Uses the information contained in the JSON dictionary to construct a list of Transformations.
        :param json_transformations:
        """
        if json_transformations:
            for json_transformation in json_transformations:
                name = self._get_transformation_property("name", json_transformation)
                values = self._get_transformation_property(
                    "values", json_transformation, 0.0
                )
                attributes = self._get_transformation_property(
                    "attributes", json_transformation
                )
                if not attributes:
                    continue
                units = self._find_property_in_list("units", name, attributes)
                transformation_type = TRANSFORMATION_MAP[
                    self._find_property_in_list("transformation_type", name, attributes)
                ]
                if not (transformation_type and units):
                    continue
                vector = self._find_property_in_list(
                    "vector", name, attributes, [0.0, 0.0, 0.0]
                )
                # depends_on = self._find_property_in_list("depends_on", name, attributes, None)
                depends_on = None
                self.parent_component._create_and_add_transform(
                    name,
                    transformation_type,
                    values,
                    units,
                    QVector3D(*vector),
                    depends_on,
                    values,
                )


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
                self._read_json_object(
                    child, json_dict["nexus_structure"]["children"][0].get("name")
                )

            if self.warnings:
                show_warning_dialog(
                    "\n".join(self.warnings),
                    "Warnings encountered loading JSON",
                    parent=self.parent,
                )
                return True

            return True

    def _read_json_object(self, json_object: dict, parent_name: str = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object:  A component from the JSON dictionary.
        """
        name = json_object.get("name")

        if name:

            nx_class = _read_nx_class(json_object.get("attributes"))

            if nx_class == NX_INSTRUMENT:
                return all(
                    [
                        self._read_json_object(child, name)
                        for child in json_object.get("children")
                    ]
                )

            if not self._validate_nx_class(name, nx_class):
                return

            if nx_class == NX_SAMPLE:
                component = self.entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                component.nx_class = nx_class
                self.entry.instrument.add_component(component)

            try:
                TransformationReader(
                    component, json_object["children"]
                ).add_transformations_to_component()
            except KeyError:
                pass

        else:
            self.warnings.append(
                f"Unable to find object name for child of {parent_name}."
            )

    def _validate_nx_class(self, name: str, nx_class: str) -> bool:
        """
        Validates the NXclass by checking if it was found, and if it matches known NXclasses for components.
        :param nx_class: The NXclass string obtained from the dictionary.
        :return: True if the NXclass is valid, False otherwise.
        """
        if not nx_class:
            self.warnings.append(f"Unable to determine NXclass of component {name}.")
            return False

        if nx_class not in COMPONENT_TYPES:
            return False

        return True
