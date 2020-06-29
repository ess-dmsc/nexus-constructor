from typing import Any, Callable, Union

from PySide2.QtGui import QVector3D

from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset, DatasetMetadata
from nexus_constructor.model.value_type import VALUE_TYPE
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.json.load_from_json_utils import _read_nx_class

NX_TRANSFORMATION = "NXtransformation"

TRANSFORMATION_MAP = {
    "translation": TransformationType.TRANSLATION,
    "rotation": TransformationType.ROTATION,
}


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
                break
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
