import json
from typing import Dict, List, Union

from nexus_constructor.common_attrs import CommonAttrs, CommonKeys
from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.json.load_from_json_utils import (
    _find_nx_class,
    _find_attribute_from_list_or_dict,
    DEPENDS_ON_IGNORE,
)
from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.json.transformation_reader import TransformationReader
from nexus_constructor.model.component import (
    Component,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
)
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.transformation import Transformation

"""
The current implementation makes a couple of assumptions that may not hold true for all valid JSON descriptions of valid NeXus files, but are safe if the JSON was created by the NeXus Constructor:
1. All transformations exist in NXtransformations groups inside components.
2. All depends_on paths are absolute, not relative.
"""
NX_INSTRUMENT = "NXinstrument"
NX_SAMPLE = "NXsample"


def _retrieve_children_list(json_dict: dict) -> list:
    """
    Attempts to retrieve the children from the JSON dictionary.
    :param json_dict: The JSON dictionary loaded by the user.
    :return: The children value is returned if it was found, otherwise an empty list is returned.
    """
    try:
        entry = json_dict[CommonKeys.CHILDREN][0]
        return entry[CommonKeys.CHILDREN]
    except (KeyError, IndexError, TypeError):
        return []


def _find_shape_information(children: List[dict]) -> Union[dict, None]:
    """
    Tries to get the shape information from a component.
    :param children: The list of dictionaries.
    :return: The shape attribute if it could be found, otherwise None.
    """
    for item in children:
        if item[CommonKeys.NAME] in [SHAPE_GROUP_NAME, PIXEL_SHAPE_GROUP_NAME]:
            return item


class JSONReader:
    def __init__(self):
        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.warnings = []
        # key: component name, value: NeXus path pointing to transformation that component depends on
        self.depends_on_paths: Dict[str, str] = dict()
        # key: component name, value: Component object created from the JSON information
        self.component_dictionary: Dict[str, Component] = dict()

    def _get_transformation_by_name(
        self,
        component: Component,
        dependency_transformation_name: str,
        dependent_component_name: str,
    ) -> Transformation:
        """
        Finds a transformation in a component based on its name in order to set the depends_on value.
        :param component: The component the dependency transformation belongs to.
        :param dependency_transformation_name: The name of the dependency transformation.
        :param dependent_component_name: The name of the dependent component.
        :return: The transformation with the given name.
        """
        for transformation in component.transforms_list:
            if transformation.name == dependency_transformation_name:
                return transformation
        self.warnings.append(
            f"Unable to find transformation with name {dependency_transformation_name} in component {component.name} "
            f"in order to set depends_on value for component {dependent_component_name}."
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
                    f"Provided file not recognised as valid JSON. Exception: {exception}"
                )
                return False

            children_list = _retrieve_children_list(json_dict)

            if not children_list:
                self.warnings.append("Provided file not recognised as valid Instrument")
                return False

            for child in children_list:
                self._read_json_object(
                    child, json_dict[CommonKeys.CHILDREN][0].get(CommonKeys.NAME)
                )

            for dependent_component_name in self.depends_on_paths.keys():
                # The following extraction of the component name and transformation name makes the assumption
                # that the transformation lives in a component and nowhere else in the file, this is safe assuming
                # the JSON was created by the NeXus Constructor.
                depends_on_path = self.depends_on_paths[dependent_component_name].split(
                    "/"
                )[3:]

                dependency_component_name = depends_on_path[0]
                dependency_transformation_name = depends_on_path[-1]

                # Assuming this is always a transformation
                self.component_dictionary[
                    dependent_component_name
                ].depends_on = self._get_transformation_by_name(
                    self.component_dictionary[dependency_component_name],
                    dependency_transformation_name,
                    dependent_component_name,
                )
                return True

            return True

    def _read_json_object(self, json_object: dict, parent_name: str = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object: A component from the JSON dictionary.
        :param parent_name: The name of the parent object. Used for warning messages if something goes wrong.
        """
        try:
            name = json_object[CommonKeys.NAME]
        except KeyError:
            self.warnings.append(
                f"Unable to find object name for child of {parent_name}."
            )
            return

        nx_class = _find_nx_class(json_object.get(CommonKeys.ATTRIBUTES))

        try:
            children = json_object[CommonKeys.CHILDREN]
        except KeyError:
            return

        if nx_class == NX_INSTRUMENT:
            for child in children:
                self._read_json_object(child, name)

        if not self._validate_nx_class(name, nx_class):
            return

        if nx_class == NX_SAMPLE:
            component = self.entry.instrument.sample
            component.name = name
        else:
            component = Component(name)
            component.nx_class = nx_class
            self.entry.instrument.add_component(component)

        transformation_reader = TransformationReader(component, children)
        transformation_reader.add_transformations_to_component()
        self.warnings += transformation_reader.warnings

        depends_on_path = _find_attribute_from_list_or_dict(
            CommonAttrs.DEPENDS_ON, children
        )

        if depends_on_path not in DEPENDS_ON_IGNORE:
            self.depends_on_paths[name] = depends_on_path

        self.component_dictionary[name] = component

        shape_info = _find_shape_information(children)
        if shape_info:
            shape_reader = ShapeReader(component, shape_info)
            shape_reader.add_shape_to_component()
            shape_reader.add_pixel_data_to_component(json_object[CommonKeys.CHILDREN])
            self.warnings += shape_reader.warnings

    def _validate_nx_class(self, name: str, nx_class: str) -> bool:
        """
        Validates the NXclass by checking if it was found, and if it matches known NXclasses for components.
        :param name: TThe name of the component having its nx class validated.
        :param nx_class: The NXclass string obtained from the dictionary.
        :return: True if the NXclass is valid, False otherwise.
        """
        if not nx_class:
            self.warnings.append(f"Unable to determine NXclass of component {name}.")
            return False

        if nx_class not in COMPONENT_TYPES:
            return False

        return True
