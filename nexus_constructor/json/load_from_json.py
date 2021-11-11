import json
from typing import Dict, Optional, Tuple

from nexus_constructor.common_attrs import (
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
)
from nexus_constructor.component_type import COMPONENT_TYPES
from nexus_constructor.json.json_warnings import (
    InvalidJson,
    JsonWarningsContainer,
    NameFieldMissing,
    NXClassAttributeMissing,
    TransformDependencyMissing,
)
from nexus_constructor.json.load_from_json_utils import (
    DEPENDS_ON_IGNORE,
    _add_field_to_group,
    _find_depends_on_path,
    _find_nx_class,
    _find_shape_information,
    _retrieve_children_list,
)
from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.json.transform_id import TransformId
from nexus_constructor.json.transformation_reader import (
    TransformationReader,
    get_component_and_transform_name,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.transformation import Transformation

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


class JSONReader:
    def __init__(self):
        self.entry = Entry()
        self.entry.instrument = Instrument()
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
        children_list = _retrieve_children_list(json_dict)

        for child in children_list:
            if child.get('module', '') == 'dataset':
                _add_field_to_group(child, self.entry)
                continue

            self._read_json_object(
                child, json_dict[CommonKeys.CHILDREN][0].get(CommonKeys.NAME)
            )

        self._set_transforms_depends_on()
        self._set_components_depends_on()

        return True

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

    def _read_json_object(self, json_object: Dict, parent_name: str = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object: A component from the JSON dictionary.
        :param parent_name: The name of the parent object. Used for warning messages if something goes wrong.
        """
        try:
            name = json_object[CommonKeys.NAME]
        except KeyError:
            self.warnings.append(
                NameFieldMissing(
                    f"Unable to find object name for child of {parent_name}."
                )
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
            component = Component(name, parent_node=self.entry.instrument)
            component.nx_class = nx_class
            self.entry.instrument.component_list.append(component)

        for item in children:
            _add_field_to_group(item, component)

        transformation_reader = TransformationReader(
            component, children, self._transforms_depends_on
        )
        transformation_reader.add_transformations_to_component()
        self.warnings += transformation_reader.warnings

        depends_on_path = _find_depends_on_path(children, name)

        if depends_on_path not in DEPENDS_ON_IGNORE:
            depends_on_id = TransformId(
                *get_component_and_transform_name(depends_on_path)
            )
            self._components_depends_on[name] = (component, depends_on_id)
        else:
            self._components_depends_on[name] = (component, None)

        shape_info = _find_shape_information(children)
        if shape_info:
            shape_reader = ShapeReader(component, shape_info)
            shape_reader.add_shape_to_component()
            try:
                shape_reader.add_pixel_data_to_component(
                    json_object[CommonKeys.CHILDREN]
                )
            except TypeError:
                # Will fail if not a detector shape
                pass
            self.warnings += shape_reader.warnings

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
