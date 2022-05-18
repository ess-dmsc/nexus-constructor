from typing import Any, Dict, List, Optional, Tuple, Union

from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import (
    NX_TRANSFORMATIONS,
    CommonAttrs,
    CommonKeys,
    NodeType,
    TransformationType,
)
from nexus_constructor.json.json_warnings import (
    InvalidTransformation,
    JsonWarningsContainer,
    TransformDependencyMissing,
)
from nexus_constructor.json.load_from_json_utils import (
    DEPENDS_ON_IGNORE,
    _find_attribute_from_list_or_dict,
    _find_nx_class,
)
from nexus_constructor.json.transform_id import TransformId
from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.model.module import (
    DATASET,
    Dataset,
    StreamModule,
    WriterModules,
    create_fw_module_object,
)
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP

TRANSFORMATION_MAP = {
    "translation": TransformationType.TRANSLATION,
    "rotation": TransformationType.ROTATION,
}


def _is_transformation_group(child_item: dict) -> bool:
    """
    Determines if a component contains transformations.
    :param child_item: The component's JSON dictionary.
    :return: True if the component has transformations, False otherwise.
    """
    try:
        return NX_TRANSFORMATIONS == _find_nx_class(child_item[CommonKeys.ATTRIBUTES])
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
        parent_node=None,
        name=name,
        type=dtype,
        values=angle_or_magnitude,
    )


def _create_transformation_datastream_group(
    data: Dict, parent_node: Optional[Group] = None
) -> StreamModule:
    return create_fw_module_object(
        data[CommonKeys.MODULE], data[NodeType.CONFIG], parent_node
    )


def get_component_and_transform_name(depends_on_string: str):
    # The following extraction of the component name and transformation name makes the assumption
    # that the transformation lives in a component and nowhere else in the file, this is safe assuming
    # the JSON was created by the NeXus Constructor
    depends_on_path = depends_on_string.split("/")
    dependency_component_name = depends_on_path[-3]
    # [-2] is the NXtransformations group (which we don't need)
    dependency_transformation_name = depends_on_path[-1]
    return dependency_component_name, dependency_transformation_name


class TransformationReader:
    def __init__(
        self,
        parent_component: Component,
        children: list,
        transforms_with_dependencies: Dict[
            TransformId, Tuple[Transformation, Optional[TransformId]]
        ],
    ):
        """
        Reads transformations from a JSON dictionary
        :param parent_component: The parent component that the transformations should be added to
        :param children: The children of the component entry
        :param transforms_with_dependencies: TransformationReader appends transforms and depends_on details to
         this dictionary so that depends_on can be set to the correct Transformation object after all
         transformations have been loaded
        """
        self.parent_component = parent_component
        self.children = children
        self.warnings = JsonWarningsContainer()
        self._transforms_with_dependencies = transforms_with_dependencies

    def add_transformations_to_component(self):
        """
        Attempts to construct Transformation objects using information from the JSON dictionary and then add them to the
        parent component.
        """
        for item in self.children:
            if _is_transformation_group(item):
                try:
                    self._create_transformations(item[CommonKeys.CHILDREN])
                except KeyError as e:
                    print("Error:", e)
                    continue

    def _get_transformation_attribute(
        self,
        attribute_name: Union[str, List[str]],
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
            if isinstance(attribute_name, str):
                return json_transformation[attribute_name]
            else:
                for key in attribute_name:
                    if key in json_transformation:
                        return json_transformation[key]
                raise KeyError
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
            self.warnings.append(TransformDependencyMissing(msg))
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
                TransformDependencyMissing(
                    f"Unable to find {attribute_name} attribute in transformation"
                    f" {transformation_name} from component {self.parent_component.name}"
                )
            )
            return failure_value
        return attribute

    def _parse_dtype(self, dtype: str, transformation_name: str) -> str:
        """
        Sees if the type value from the JSON matches the types on the value type dictionary.
        :param dtype: The type value obtained from the JSON.
        :return: The corresponding type from the dictionary if it exists, otherwise an empty string is returned.
        """
        for key in VALUE_TYPE_TO_NP.keys():
            if dtype.lower() == key.lower():
                return key
        self.warnings.append(
            InvalidTransformation(
                f"Could not recognise dtype {dtype} from transformation"
                f" {transformation_name} in component {self.parent_component.name}."
            )
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
            return TRANSFORMATION_MAP[transformation_type.lower()]
        except KeyError:
            self.warnings.append(
                InvalidTransformation(
                    f"Could not recognise transformation type {transformation_type} of"
                    f" transformation {transformation_name} in component"
                    f" {self.parent_component.name}."
                )
            )
            return ""

    def _create_transformations(self, json_transformations: list):
        """
        Uses the information contained in the JSON dictionary to construct a list of Transformations.
        :param json_transformations: A list of JSON transformation entries.
        """
        for json_transformation in json_transformations:
            is_nx_log = (
                CommonKeys.TYPE in json_transformation
                and json_transformation[CommonKeys.TYPE] == NodeType.GROUP
            )
            if is_nx_log:
                tmp = json_transformation[CommonKeys.CHILDREN][0]
                if CommonKeys.ATTRIBUTES in tmp:
                    tmp[CommonKeys.ATTRIBUTES] += json_transformation[
                        CommonKeys.ATTRIBUTES
                    ]
                else:
                    tmp[CommonKeys.ATTRIBUTES] = json_transformation[
                        CommonKeys.ATTRIBUTES
                    ]
                tmp[NodeType.CONFIG][CommonKeys.NAME] = json_transformation[
                    CommonKeys.NAME
                ]
                json_transformation = tmp
            config = self._get_transformation_attribute(
                NodeType.CONFIG, json_transformation
            )
            if not config:
                continue

            module = self._get_transformation_attribute(
                CommonKeys.MODULE, json_transformation
            )
            if not module:
                continue

            name = self._get_transformation_attribute(CommonKeys.NAME, config)
            dtype = self._get_transformation_attribute(
                [CommonKeys.DATA_TYPE, CommonKeys.TYPE],
                config,
                name,
            )
            if not dtype:
                continue
            dtype = self._parse_dtype(dtype, name)
            if not dtype:
                continue

            attributes = self._get_transformation_attribute(
                CommonKeys.ATTRIBUTES, json_transformation, name
            )
            if not attributes:
                continue

            units = self._find_attribute_in_list(CommonAttrs.UNITS, name, attributes)
            if not units:
                continue

            transformation_type = self._find_attribute_in_list(
                CommonAttrs.TRANSFORMATION_TYPE,
                name,
                attributes,
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
            # This attribute is allowed to be missing, missing is equivalent to the value "." which means
            # depends on origin (end of dependency chain)
            depends_on = _find_attribute_from_list_or_dict(
                CommonAttrs.DEPENDS_ON, attributes
            )
            if module == DATASET:
                values = self._get_transformation_attribute(
                    CommonKeys.VALUES, config, name
                )
                if values is None:
                    continue
                angle_or_magnitude = values
                values = _create_transformation_dataset(angle_or_magnitude, dtype, name)
            elif module in [writer_mod.value for writer_mod in WriterModules]:
                values = _create_transformation_datastream_group(json_transformation)
                angle_or_magnitude = 0.0
            else:
                continue
            temp_depends_on = None

            transform = self.parent_component._create_and_add_transform(
                name=name,
                transformation_type=transformation_type,
                angle_or_magnitude=angle_or_magnitude,
                units=units,
                vector=QVector3D(*vector),
                depends_on=temp_depends_on,
                values=values,
            )
            if depends_on not in DEPENDS_ON_IGNORE:
                depends_on_id = TransformId(
                    *get_component_and_transform_name(depends_on)
                )
                self._transforms_with_dependencies[
                    TransformId(self.parent_component.name, name)
                ] = (transform, depends_on_id)
            else:
                self._transforms_with_dependencies[
                    TransformId(self.parent_component.name, name)
                ] = (transform, None)
