import json
from json import JSONDecodeError
from typing import Dict, Optional, Tuple, Union

from nexus_constructor.common_attrs import (
    NX_CLASSES_WITH_PLACEHOLDERS,
    NX_TRANSFORMATIONS,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.component_type import (
    COMPONENT_TYPES,
    ENTRY_CLASS_NAME,
    NX_CLASSES,
    SAMPLE_CLASS_NAME,
)
from nexus_constructor.json.json_warnings import (
    InvalidJson,
    JsonWarningsContainer,
    NameFieldMissing,
    NXClassAttributeMissing,
    TransformDependencyMissing,
)
from nexus_constructor.json.load_from_json_utils import (
    DEPENDS_ON_IGNORE,
    _find_depends_on_path,
    _find_nx_class,
    _find_shape_information,
)
from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.json.transform_id import TransformId
from nexus_constructor.json.transformation_reader import (
    TransformationReader,
    get_component_and_transform_name,
)
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import USERS_PLACEHOLDER
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME, Group
from nexus_constructor.model.model import Model
from nexus_constructor.model.module import (
    Dataset,
    FileWriter,
    FileWriterModule,
    Link,
    StreamModule,
    WriterModules,
    create_fw_module_object,
)
from nexus_constructor.model.transformation import Transformation

"""
The current implementation makes a couple of assumptions that may not hold true for all valid JSON descriptions of
valid NeXus files, but are safe if the JSON was created by the NeXus Constructor:
1. All transformations exist in NXtransformations groups inside components.
2. All depends_on paths are absolute, not relative.
"""
NX_INSTRUMENT = "NXinstrument"
CHILD_EXCLUDELIST = [
    SHAPE_GROUP_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    TRANSFORMS_GROUP_NAME,
    CommonAttrs.DEPENDS_ON,
]

PLACEHOLDER_WITH_NX_CLASSES = {v: k for k, v in NX_CLASSES_WITH_PLACEHOLDERS.items()}


class JSONReader:
    def __init__(self):
        self.entry_node: Group = None
        self.model = Model()
        self.sample_name: str = ""
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

    def _append_transformations_to_nx_group(self):
        """
        Correctly adds the transformations in the components, with respect
        to the instance of TransformationList, to transformation nexus group.
        """
        for component in self.model.get_components():
            transformation_list = component.transforms
            transformation_children = []
            for child in component.children:
                if isinstance(child, Group) and child.nx_class == NX_TRANSFORMATIONS:
                    for transformation in transformation_list:
                        transformation_children.append(transformation)
                    child.children = transformation_children

    def _set_transformation_links(self):
        """
        Adds transformation links to the components where a link exists.
        """
        for component in self.model.get_components():
            nx_transformation_group = None
            for child in component.children:
                if isinstance(child, Group) and child.nx_class == NX_TRANSFORMATIONS:
                    for childs_child in child.children:
                        attrs = childs_child.attributes
                        if attrs.get_attribute_value(CommonAttrs.DEPENDS_ON):
                            nx_transformation_group = child
                            component.transforms.has_link = True
                            break
                    break
            if nx_transformation_group:
                transformation_list = component.transforms
                transformation_list.link.parent_node = nx_transformation_group
                nx_transformation_group.children.append(transformation_list.link)

    def load_model_from_json(self, filename: str) -> bool:
        """
        Tries to load a model from a JSON file.
        :param filename: The filename of the JSON file.
        :return: True if the model was loaded without problems, False otherwise.
        """
        with open(filename, "r") as json_file:
            try:
                json_dict = json.load(json_file)
            except JSONDecodeError as exception:
                self.warnings.append(
                    InvalidJson(
                        f"Provided file not recognised as valid JSON. Exception: {exception}"
                    )
                )
                return False

            return self._load_from_json_dict(json_dict)

    def _load_from_json_dict(self, json_dict: Dict) -> bool:
        self.entry_node = self._read_json_object(json_dict[CommonKeys.CHILDREN][0])
        self.model.entry.attributes = self.entry_node.attributes
        for child in self.entry_node.children:
            if isinstance(child, (Dataset, Link, FileWriter, Group)):
                self.model.entry[child.name] = child
            else:
                self.model.entry.children.append(child)
            child.parent_node = self.model.entry
        self._set_transforms_depends_on()
        self._set_components_depends_on()
        self._append_transformations_to_nx_group()
        self._set_transformation_links()
        return True

    def _replace_placeholder(self, placeholder: str):
        if placeholder in PLACEHOLDER_WITH_NX_CLASSES:
            nx_class = PLACEHOLDER_WITH_NX_CLASSES[placeholder]
            name = placeholder.replace("$", "").lower()
            return {
                CommonKeys.NAME: name,
                CommonKeys.TYPE: NodeType.GROUP,
                CommonKeys.ATTRIBUTES: [
                    {
                        CommonKeys.NAME: CommonAttrs.NX_CLASS,
                        CommonKeys.DATA_TYPE: "string",
                        CommonKeys.VALUES: nx_class,
                    }
                ],
                CommonKeys.CHILDREN: [],
            }
        return None

    def _read_json_object(self, json_object: Dict, parent_node: Group = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object: A component from the JSON dictionary.
        :param parent_name: The name of the parent object. Used for warning messages if something goes wrong.
        """
        nexus_object: Union[Group, FileWriterModule] = None
        use_placeholder = False
        if isinstance(json_object, str) and json_object in PLACEHOLDER_WITH_NX_CLASSES:
            json_object = self._replace_placeholder(json_object)
            if not json_object:
                return
            use_placeholder = True
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
            if nx_class == SAMPLE_CLASS_NAME:
                self.sample_name = name
            if not self._validate_nx_class(name, nx_class):
                self._add_object_warning(f"valid Nexus class {nx_class}", parent_node)
            if nx_class in COMPONENT_TYPES:
                nexus_object = Component(name=name, parent_node=parent_node)
                children_dict = json_object[CommonKeys.CHILDREN]
                self._add_transform_and_shape_to_component(nexus_object, children_dict)
                self.model.append_component(nexus_object)
            else:
                nexus_object = Group(name=name, parent_node=parent_node)
            nexus_object.nx_class = nx_class
            if CommonKeys.CHILDREN in json_object:
                for child in json_object[CommonKeys.CHILDREN]:
                    node = self._read_json_object(child, nexus_object)
                    if node and isinstance(node, StreamModule):
                        nexus_object.children.append(node)
                        nexus_object.remove_stream_module(node.writer_module)
                    elif node and node.name not in nexus_object:
                        nexus_object[node.name] = node
        elif CommonKeys.MODULE in json_object and NodeType.CONFIG in json_object:
            module_type = json_object[CommonKeys.MODULE]
            if (
                module_type == WriterModules.DATASET.value
                or module_type == WriterModules.FILEWRITER.value
            ) and json_object[NodeType.CONFIG][
                CommonKeys.NAME
            ] == CommonAttrs.DEPENDS_ON:
                nexus_object = None
            elif module_type in [x.value for x in WriterModules]:
                nexus_object = create_fw_module_object(
                    module_type, json_object[NodeType.CONFIG], parent_node
                )
                nexus_object.parent_node = parent_node
            else:
                self._add_object_warning("valid module type", parent_node)
                return None
        elif json_object == USERS_PLACEHOLDER:
            self.model.entry.users_placeholder = True
            return None
        else:
            self._add_object_warning(
                f"valid {CommonKeys.TYPE} or {CommonKeys.MODULE}", parent_node
            )

        # Add attributes to nexus_object.
        if nexus_object:
            json_attrs = json_object.get(CommonKeys.ATTRIBUTES)
            if json_attrs:
                attributes = Attributes()
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
                nexus_object.attributes = attributes
            if (
                parent_node
                and isinstance(nexus_object, Dataset)
                and parent_node.nx_class == ENTRY_CLASS_NAME
            ):
                self.model.entry[nexus_object.name] = nexus_object
            if isinstance(nexus_object, Group) and not nexus_object.nx_class:
                self._add_object_warning(
                    f"valid {CommonAttrs.NX_CLASS}",
                    parent_node,
                )
            elif isinstance(nexus_object, Group) and nexus_object.nx_class == "NXuser":
                self.model.entry[nexus_object.name] = nexus_object
            if isinstance(nexus_object, Group):
                nexus_object.group_placeholder = use_placeholder
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
        if nx_class not in NX_CLASSES:
            return False
        return True

    def _add_transform_and_shape_to_component(self, component, children_dict):
        # Add transformations if they exist.
        transformation_reader = TransformationReader(
            component, children_dict, self._transforms_depends_on
        )
        transformation_reader.add_transformations_to_component()
        self.warnings += transformation_reader.warnings
        depends_on = _find_depends_on_path(children_dict, component.name)
        if depends_on not in [".", "", None]:
            if depends_on[0] != "/":
                #   we are always in the NXtransformations group but the path could be anything
                if len(depends_on.split("/")) == 2:
                    depends_on = depends_on.split('/')[1]
                depends_on = component.absolute_path + "/transformations/" + depends_on

        if depends_on not in DEPENDS_ON_IGNORE:
            depends_on_id = TransformId(
                *get_component_and_transform_name(depends_on)
            )
            self._components_depends_on[component.name] = (component, depends_on_id)
        else:
            self._components_depends_on[component.name] = (component, None)

        # Add shape if there is a shape.
        shape_info = _find_shape_information(children_dict)
        if shape_info:
            shape_reader = ShapeReader(component, shape_info)
            shape_reader.add_shape_to_component()
            try:
                shape_reader.add_pixel_data_to_component(children_dict)
            except TypeError:
                # Will fail if not a detector shape
                pass
            self.warnings += shape_reader.warnings

        return component
