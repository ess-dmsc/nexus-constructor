import json
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from nexus_constructor.common_attrs import (
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.component_type import COMPONENT_TYPES
from nexus_constructor.json_utils.json_warnings import (
    InvalidJson,
    JsonWarningsContainer,
    NameFieldMissing,
    NXClassAttributeMissing,
    TransformDependencyMissing,
)
from nexus_constructor.json_utils.load_from_json_utils import _find_nx_class
from nexus_constructor.json_utils.transform_id import TransformId
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME, Group
from nexus_constructor.model.stream import (
    SOURCE,
    Link,
    Module,
    WriterModules,
    create_fw_module_object,
)
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP

"""
The current implementation makes a couple of assumptions that may not hold true for all valid JSON descriptions of
valid NeXus files, but are safe if the JSON was created by the NeXus Constructor:
1. All transformations exist in NXtransformations groups inside components.
2. All depends_on paths are absolute, not relative.
"""
NX_INSTRUMENT = "NXinstrument"
NX_SAMPLE = "NXsample"
CHILD_EXCLUDELIST = [
    SHAPE_GROUP_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    TRANSFORMS_GROUP_NAME,
    CommonAttrs.DEPENDS_ON,
]


def _retrieve_children_list(json_dict: Dict) -> List:
    """
    Attempts to retrieve the children from the JSON dictionary.
    :param json_dict: The JSON dictionary loaded by the user.
    :return: The children value is returned if it was found, otherwise an empty list is returned.
    """
    value = []
    try:
        entry = json_dict[CommonKeys.CHILDREN][0]
        value = entry[CommonKeys.CHILDREN]
    except (KeyError, IndexError, TypeError):
        pass
    return value


def _find_shape_information(children: List[Dict]) -> Union[Dict, None]:
    """
    Tries to get the shape information from a component.
    :param children: The list of dictionaries.
    :return: The shape attribute if it could be found, otherwise None.
    """
    value = None
    try:
        for item in children:
            if item[CommonKeys.NAME] in [SHAPE_GROUP_NAME, PIXEL_SHAPE_GROUP_NAME]:
                value = item
    except KeyError:
        pass
    return value


def _find_depends_on_path(items: List[Dict], name: str) -> Optional[str]:
    if not isinstance(items, list):
        raise RuntimeError(
            f'List of children in node with the name "{name}" is not a list.'
        )
    for item in items:
        try:
            config = item[NodeType.CONFIG]
            if config[CommonKeys.NAME] != CommonAttrs.DEPENDS_ON:
                continue
            return config[CommonKeys.VALUES]
        except KeyError:
            pass  # Not all items has a config node, ignore those that do not.
    return None


class JSONReader:
    def __init__(self):
        self.entry_node = None
        self.warnings = JsonWarningsContainer()

        # key: TransformId for transform which has a depends on
        # value: the Transformation object itself and the TransformId for the Transformation which it depends on
        # Populated while loading the transformations so that depends_on property of each Transformation can be set
        # to the appropriate Transformation after all the Transformations have been created, otherwise they would
        # need to be created in a particular order
        self._transforms_depends_on: Dict[
            TransformId, Tuple[Transformation, Optional[TransformId]]
        ] = {}

        # key: name of the component (uniquely identifies Component)
        # value: the Component object itself and the TransformId for the Transformation which it depends on
        # Populated while loading the components so that depends_on property of each Component can be set to the
        # appropriate Transformation after all the Transformations have been created, otherwise they would
        # need to be created in a particular order
        self._components_depends_on: Dict[
            str, Tuple[Component, Optional[TransformId]]
        ] = {}

    def _set_components_depends_on(self):
        """
        Once all transformations have been loaded we should be able to set each component's depends_on property without
        worrying that the Transformation dependency has not been created yet
        """
        for (
            component_name,
            (
                component,
                depends_on_id,
            ),
        ) in self._components_depends_on.items():
            try:
                # If it has a dependency then find the corresponding Transformation and assign it to
                # the depends_on property
                if depends_on_id is not None:
                    component.depends_on = self._transforms_depends_on[depends_on_id][0]
            except KeyError:
                self.warnings.append(
                    TransformDependencyMissing(
                        f"Component {component_name} depends on {depends_on_id.transform_name} in component "
                        f"{depends_on_id.component_name}, but that transform was not successfully loaded from the JSON"
                    )
                )

    def _set_transforms_depends_on(self):
        """
        Once all transformations have been loaded we should be able to set their depends_on property without
        worrying that the Transformation dependency has not been created yet
        """
        for (
            transform_id,
            (
                transform,
                depends_on_id,
            ),
        ) in self._transforms_depends_on.items():
            try:
                # If it has a dependency then find the corresponding Transformation and assign it to
                # the depends_on property
                if depends_on_id is not None:
                    transform.depends_on = self._transforms_depends_on[depends_on_id][0]
            except KeyError:
                self.warnings.append(
                    TransformDependencyMissing(
                        f"Transformation {transform_id.transform_name} in component {transform_id.component_name} "
                        f"depends on {depends_on_id.transform_name} in component {depends_on_id.component_name}, "
                        f"but that transform was not successfully loaded from the JSON"
                    )
                )

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
                self.warnings.append(
                    InvalidJson(
                        f"Provided file not recognised as valid JSON. Exception: {exception}"
                    )
                )
                return False

            return self._load_from_json_dict(json_dict)

    def _load_from_json_dict(self, json_dict: Dict) -> bool:
        self.entry_node = self._read_json_object(json_dict[CommonKeys.CHILDREN][0])
        # self._set_transforms_depends_on()
        # self._set_components_depends_on()
        return True

    def _read_json_object(self, json_object: Dict, parent_node: Group = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object: A component from the JSON dictionary.
        :param parent_name: The name of the parent object. Used for warning messages if something goes wrong.
        """
        nexus_object: Union[Group, Module] = None
        if (
            CommonKeys.TYPE in json_object
            and json_object[CommonKeys.TYPE] == NodeType.GROUP
        ):
            try:
                name = json_object[CommonKeys.NAME]
            except KeyError:
                self._add_object_warning(CommonKeys.NAME, parent_node)
                return None
            nx_class = _find_nx_class(json_object.get(CommonKeys.ATTRIBUTES))
            if not self._validate_nx_class(name, nx_class):
                self._add_object_warning(f"valid Nexus class {nx_class}", parent_node)
            nexus_object = Group(name=name)
            nexus_object.parent_node = parent_node
            nexus_object.nx_class = nx_class
            if CommonKeys.CHILDREN in json_object:
                for child in json_object[CommonKeys.CHILDREN]:
                    node = self._read_json_object(child, nexus_object)
                    if node:
                        nexus_object.children.append(node)
        elif CommonKeys.MODULE in json_object and NodeType.CONFIG in json_object:
            module_type = json_object[CommonKeys.MODULE]
            if module_type in [x.value for x in WriterModules]:
                nexus_object = create_fw_module_object(
                    module_type, json_object[NodeType.CONFIG]
                )
                nexus_object.parent_node = parent_node
                # nexus_object.writer_module = json_object[CommonKeys.MODULE]
                # nexus_object.module_configs = json_object[NodeType.CONFIG]
            else:
                self._add_object_warning("valid module type", parent_node)
                return None
        else:
            self._add_object_warning(
                f"valid {CommonKeys.TYPE} or {CommonKeys.MODULE}", parent_node
            )

        # Add attributes to nexus_object.
        if nexus_object:
            attributes = Attributes()
            json_attrs = json_object.get(CommonKeys.ATTRIBUTES)
            if json_attrs:
                for json_attr in json_attrs:
                    if not json_attr[CommonKeys.VALUES]:
                        self._add_object_warning(
                            f"values in attribute {json_attr[CommonKeys.NAME]}",
                            parent_node,
                        )
                    elif CommonKeys.DATA_TYPE in json_attr:
                        attributes.set_attribute_value(
                            json_attr[CommonKeys.NAME],
                            json_attr[CommonKeys.VALUES],
                            json_attr[CommonKeys.DATA_TYPE],
                        )
                    elif CommonKeys.NAME in json_attr:
                        attributes.set_attribute_value(
                            json_attr[CommonKeys.NAME], json_attr[CommonKeys.VALUES]
                        )

        return nexus_object

    def _add_object_warning(self, missing_info, parent_node):
        if parent_node:
            self.warnings.append(
                NameFieldMissing(
                    f"Unable to find {missing_info} "
                    f"for child of {parent_node.name}."
                )
            )
        else:
            self.warnings.append(
                NameFieldMissing(f"Unable to find object {missing_info} for NXEntry.")
            )

    def _validate_nx_class(self, name: str, nx_class: str) -> bool:
        """
        Validates the NXclass by checking if it was found, and if it matches known NXclasses for components.
        :param name: The name of the component having its nx class validated.
        :param nx_class: The NXclass string obtained from the dictionary.
        :return: True if the NXclass is valid, False otherwise.
        """
        if not nx_class:
            self.warnings.append(
                NXClassAttributeMissing(
                    f"Unable to determine NXclass of component {name}."
                )
            )
            return False

        if nx_class not in COMPONENT_TYPES:
            return False

        return True


def _get_data_type(json_object: Dict):
    if CommonKeys.DATA_TYPE in json_object:
        return json_object[CommonKeys.DATA_TYPE]
    elif CommonKeys.TYPE in json_object:
        return json_object[CommonKeys.TYPE]
    raise KeyError


def _create_dataset(json_object: Dict, parent: Group) -> Dataset:
    value_type = _get_data_type(json_object[NodeType.CONFIG])
    name = json_object[NodeType.CONFIG][CommonKeys.NAME]
    values = json_object[NodeType.CONFIG][CommonKeys.VALUES]
    if isinstance(values, list):
        # convert to a numpy array using specified type
        values = np.array(values, dtype=VALUE_TYPE_TO_NP[value_type])
    ds = Dataset(name=name, values=values, type=value_type, parent_node=parent)
    _add_attributes(json_object, ds)
    return ds


def _create_link(json_object: Dict) -> Link:
    name = json_object[NodeType.CONFIG][CommonKeys.NAME]
    target = json_object[NodeType.CONFIG][SOURCE]
    link = Link()
    link.name = name
    link.source = target
    return link


def _add_attributes(json_object: Dict, model_object: Union[Group, Dataset]):
    try:
        attrs_list = json_object[CommonKeys.ATTRIBUTES]
        for attribute in attrs_list:
            attr_name = attribute[CommonKeys.NAME]
            attr_values = attribute[CommonKeys.VALUES]
            model_object.attributes.set_attribute_value(
                attribute_name=attr_name, attribute_value=attr_values
            )
    except (KeyError, AttributeError):
        pass
