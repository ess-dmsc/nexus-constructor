from typing import Any, Union

from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset, DatasetMetadata
from nexus_constructor.model.value_type import VALUE_TYPE
from nexus_constructor.transformation_types import TransformationType
from nexus_constructor.json.load_from_json_utils import (
    _find_attribute_from_list_or_dict,
    _find_nx_class,
    DEPENDS_ON_IGNORE,
)

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
        return NX_TRANSFORMATION in _find_nx_class(entry["attributes"])
    except KeyError:
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
        """
        Reads transformations from a JSON dictionary.
        :param parent_component: The parent component that the transformations should be added to.
        :param entry: The children of the component entry.
        """
        self.parent_component = parent_component
        self.entry = entry
        self.warnings = []
        self.depends_on_paths = dict()

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

    def _get_transformation_attribute(
        self,
        attribute_name: str,
        json_transformation: dict,
        transform_name: str = None,
        failure_value: Any = None,
    ) -> Any:
        """
        Tries to find a certain attribute of a transformation from dictionary.
        :param attribute_name: The name of the attribute fields.
        :param json_transformation: The dictionary to look for the attribute in.
        :param transform_name: The name of the transformation (if known).
        :param failure_value: The value to return if the attribute cannot be found.
        :return: Returns the attribute or converted attribute if this exists in the dictionary, if the attribute is not
        found in the dictionary then the failure_value is returned.
        """
        try:
            return json_transformation[attribute_name]
        except KeyError:
            if transform_name:
                msg = (
                    f"Cannot find {attribute_name} for transformation in component"
                    f" {transform_name}"
                )
                f" {self.parent_component.name}."
            else:
                msg = f"Cannot find {attribute_name} for transformation in component"
                f" {self.parent_component.name}."
            self.warnings.append(msg)
            return failure_value

    def _find_attribute_in_list(
        self,
        attribute_name: str,
        transformation_name: str,
        attributes_list: list,
        failure_value: Any = None,
    ) -> Any:
        """
        Searches the dictionaries in a list to see if one of them has a given attribute.
        :param attribute_name: The name of the attribute that is being looked for.
        :param transformation_name: The name of the transformation that is being constructed.
        :param attributes_list: The list of dictionaries.
        :param failure_value: The value to return if the attribute is not contained in any of the dictionaries.
        :return: The value of the attribute if is is found in the list, otherwise the failure value is returned.
        """
        attribute = _find_attribute_from_list_or_dict(attribute_name, attributes_list)
        if not attribute:
            self.warnings.append(
                f"Unable to find {attribute_name} attribute in transformation"
                f" {transformation_name} from component {self.parent_component.name}"
            )
            return failure_value
        return attribute

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

            name = self._get_transformation_attribute("name", json_transformation)

            values = self._get_transformation_attribute(
                "values", json_transformation, name
            )
            if values is None:
                continue

            dataset = self._get_transformation_attribute(
                "dataset", json_transformation, name
            )
            if not dataset:
                continue
            dtype = self._get_transformation_attribute("type", dataset, name,)
            if not dtype:
                continue
            dtype = self._parse_dtype(dtype, name)
            if not dtype:
                continue

            attributes = self._get_transformation_attribute(
                "attributes", json_transformation, name
            )
            if not attributes:
                continue

            units = self._find_attribute_in_list(CommonAttrs.UNITS, name, attributes)
            if not units:
                continue

            transformation_type = self._find_attribute_in_list(
                "transformation_type", name, attributes,
            )
            if not transformation_type:
                continue
            transformation_type = self._parse_transformation_type(
                transformation_type, name
            )
            if not transformation_type:
                continue

            vector = self._find_attribute_in_list(
                CommonAttrs.VECTOR, name, attributes, [0.0, 0.0, 0.0]
            )

            depends_on = self._find_attribute_in_list(
                CommonAttrs.DEPENDS_ON, name, attributes
            )

            temp_depends_on = None
            angle_or_magnitude = values
            values = _create_transformation_dataset(angle_or_magnitude, dtype, name)

            self.parent_component._create_and_add_transform(
                name,
                transformation_type,
                angle_or_magnitude,
                units,
                QVector3D(*vector),
                temp_depends_on,
                values,
            )

            if depends_on not in DEPENDS_ON_IGNORE:
                self.depends_on_paths[name] = depends_on
