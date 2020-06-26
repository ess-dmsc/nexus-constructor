import json
from typing import Union, Any, Callable

from PySide2.QtGui import QVector3D
from PySide2.QtWidgets import QWidget

from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset, DatasetMetadata
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.value_type import VALUE_TYPE
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


def _create_transformation_dataset(
    angle_or_magnitude: float, dtype: str, name: str
) -> Dataset:
    """
    Creates the transformation dataset using the angle/magnitude, name, and dtype of the transformation.
    :param angle_or_magnitude: The angle or magnitude.
    :param dtype: The data type.
    :param name: The transformation name.
    :return: A dataset containing the above information.
    """
    return Dataset(
        name, dataset=DatasetMetadata(size=[1], type=dtype), values=angle_or_magnitude,
    )


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
                try:
                    self._create_transformations(item["children"])
                except KeyError:
                    continue

    def _get_transformation_property(
        self,
        property_name: str,
        json_transformation: dict,
        transform_name: str = None,
        failure_value: Any = None,
        parse_result_func: Callable = None,
    ) -> Any:
        """
        Tries to find a certain property of a transformation from dictionary.
        :param property_name: The name of the property fields.
        :param json_transformation: The dictionary to look for the property in.
        :param transform_name: The name of the transformation (if known).
        :param failure_value: The value to return if the property cannot be found.
        :param parse_result_func: A function that should be called on the dictionary value if it is found.
        :return: Returns the property or converted property if this exists in the dictionary, if the property is not
        found in the dictionary then the failure_value is returned.
        """
        try:
            if not parse_result_func:
                return json_transformation[property_name]
            else:
                return parse_result_func(json_transformation[property_name])
        except KeyError:
            if transform_name:
                msg = (
                    f"Cannot find {property_name} for transformation in component"
                    f" {transform_name}"
                )
                f" {self.parent_component.name}."
            else:
                msg = f"Cannot find {property_name} for transformation in component"
                f" {self.parent_component.name}."
            self.warnings.append(msg)
            return failure_value

    def _find_property_in_list(
        self,
        property_name: str,
        transformation_name: str,
        attributes_list: list,
        failure_value: Any = None,
        parse_result_func: Callable = None,
    ) -> Any:
        """
        Searches the dictionaries in a list to see if one of them has a given property.
        :param property_name: The name of the property that is being looked for.
        :param transformation_name: The name of the transformation that is being constructed.
        :param attributes_list: The list of dictionaries.
        :param failure_value: The value to return if the property is not contained in any of the dictionaries.
        :param parse_result_func: todo: description
        :return: The value of the property if is is found in the list, otherwise the failure value is returned.
        """
        for attribute in attributes_list:
            try:
                if attribute["name"] == property_name:
                    if parse_result_func:
                        return parse_result_func(attribute["values"])
                    else:
                        return attribute["values"]
            except KeyError:
                continue
        self.warnings.append(
            f"Unable to find {property_name} property in transformation"
            f" {transformation_name} from component {self.parent_component.name}"
        )
        return failure_value

    def _parse_dtype(self, dtype: str, transformation_name: str) -> str:
        """
        Sees if the type value from the JSON matches the types on the value type dictionary.
        :param dtype: The type value obtained from the JSON.
        :return: The corresponding type from the dictionary if it exists, otherwise an empty string is returned.
        """
        for key in VALUE_TYPE.keys():
            if dtype.lower() == key.lower():
                return key
        self.warnings.append(
            f"Could not recognise dtype {dtype} from transformation"
            f" {transformation_name} in component {self.parent_component.name}."
        )
        return ""

    def _parse_transformation_type(
        self, transformation_type: str, transformation_name: str
    ) -> Union[TransformationType, str]:
        """
        Converts the transformation type in the JSON to one recognised by the NeXus Constructor.
        :param transformation_type: The transformation type from the JSON.
        :param transformation_name: The name of the transformation that is being processed.
        :return: The matching TransformationType class value.
        """
        try:
            return TRANSFORMATION_MAP[transformation_type]
        except KeyError:
            self.warnings.append(
                f"Could not recognise transformation type {transformation_type} of"
                f" transformation {transformation_name} in component"
                f" {self.parent_component.name}."
            )
            return ""

    def _create_transformations(self, json_transformations: list):
        """
        Uses the information contained in the JSON dictionary to construct a list of Transformations.
        :param json_transformations: A list of JSON transformation entries.
        """
        for json_transformation in json_transformations:

            name = self._get_transformation_property("name", json_transformation)

            values = self._get_transformation_property(
                "values", json_transformation, name
            )
            if values is None:
                continue

            dataset = self._get_transformation_property(
                "dataset", json_transformation, name
            )
            if not dataset:
                continue

            dtype = self._get_transformation_property(
                "type",
                dataset,
                name,
                parse_result_func=lambda datatype: self._parse_dtype(
                    dtype=datatype, transformation_name=name
                ),
            )
            if not dtype:
                continue

            attributes = self._get_transformation_property(
                "attributes", json_transformation, name
            )
            if not attributes:
                continue

            units = self._find_property_in_list("units", name, attributes)
            if not units:
                continue

            transformation_type = self._find_property_in_list(
                "transformation_type",
                name,
                attributes,
                parse_result_func=lambda transform_type: self._parse_transformation_type(
                    transformation_type=transform_type, transformation_name=name
                ),
            )
            if not transformation_type:
                continue

            vector = self._find_property_in_list(
                "vector", name, attributes, [0.0, 0.0, 0.0]
            )

            depends_on = None

            angle_or_magnitude = values
            values = _create_transformation_dataset(angle_or_magnitude, dtype, name)

            transform = self.parent_component._create_and_add_transform(
                name,
                transformation_type,
                angle_or_magnitude,
                units,
                QVector3D(*vector),
                depends_on,
                values,
            )
            self.parent_component.depends_on = transform


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
