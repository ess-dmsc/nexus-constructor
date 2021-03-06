import json
from typing import Dict, List, Union

from nexus_constructor.common_attrs import (
    CommonAttrs,
    CommonKeys,
    SHAPE_GROUP_NAME,
    PIXEL_SHAPE_GROUP_NAME,
    NodeType,
)
from nexus_constructor.component_type import COMPONENT_TYPES
from nexus_constructor.json.load_from_json_utils import (
    _find_nx_class,
    _find_attribute_from_list_or_dict,
    DEPENDS_ON_IGNORE,
)
from nexus_constructor.json.shape_reader import ShapeReader
from nexus_constructor.json.transformation_reader import TransformationReader
from nexus_constructor.model.component import Component
from nexus_constructor.model.dataset import Dataset
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME, Group
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.link import Link, TARGET
from nexus_constructor.model.stream import (
    WRITER_MODULE,
    SOURCE,
    TOPIC,
    WriterModules,
    HS00Stream,
    NS10Stream,
    SENVStream,
    TDCTStream,
    F142Stream,
    EV42Stream,
    StreamGroup,
    Stream,
    DATA_TYPE,
    ERROR_TYPE,
    EDGE_TYPE,
    SHAPE,
    ARRAY_SIZE,
    VALUE_UNITS,
    INDEX_EVERY_MB,
    INDEX_EVERY_KB,
    STORE_LATEST_INTO,
    ADC_PULSE_DEBUG,
    CHUNK_CHUNK_KB,
    CHUNK_CHUNK_MB,
)
import numpy as np
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP

"""
The current implementation makes a couple of assumptions that may not hold true for all valid JSON descriptions of valid NeXus files, but are safe if the JSON was created by the NeXus Constructor:
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
    try:
        entry = json_dict[CommonKeys.CHILDREN][0]
        return entry[CommonKeys.CHILDREN]
    except (KeyError, IndexError, TypeError):
        return []


def _find_shape_information(children: List[Dict]) -> Union[Dict, None]:
    """
    Tries to get the shape information from a component.
    :param children: The list of dictionaries.
    :return: The shape attribute if it could be found, otherwise None.
    """
    for item in children:
        if item[CommonKeys.NAME] in [SHAPE_GROUP_NAME, PIXEL_SHAPE_GROUP_NAME]:
            return item


def _add_field_to_group(item: Dict, group: Group):
    field_type = item[CommonKeys.TYPE]
    if (
        field_type == NodeType.STREAM
    ):  # streams do not have a name field so need to be dealt with differently from other fields.
        stream = _create_stream(item)
        group.children.append(
            stream
        )  # Can't use the `[]` operator because streams do not have a name to use as a key
    else:
        child_name = item[CommonKeys.NAME]
        if (
            child_name not in CHILD_EXCLUDELIST
        ):  # ignore transforms, shape etc as these are handled separately
            if field_type == NodeType.GROUP:
                child = _create_group(item, group)
            elif field_type == NodeType.DATASET:
                child = _create_dataset(item, group)
            elif field_type == NodeType.LINK:
                child = _create_link(item)
            else:
                raise Exception(
                    f"Found unknown field type when loading JSON - {child_name}"
                )
            # Add the child to the parent group
            group[child_name] = child


def _create_stream(json_object: Dict) -> Stream:
    """
    Given a dictionary containing a stream, create a corresponding stream object to be used in the model.
    :param json_object: JSON dictionary containing a stream.
    :return: A stream object containing relevant data from the JSON.
    """
    stream_object = json_object[NodeType.STREAM]
    writer_module = stream_object[WRITER_MODULE]
    source = stream_object[SOURCE]
    topic = stream_object[TOPIC]
    # Common to ev42 and f142 stream objects
    index_mb = (
        stream_object[INDEX_EVERY_MB] if INDEX_EVERY_MB in stream_object else None
    )
    index_kb = (
        stream_object[INDEX_EVERY_KB] if INDEX_EVERY_KB in stream_object else None
    )
    if writer_module == WriterModules.F142.value:
        return __create_f142_stream(index_kb, index_mb, source, stream_object, topic)
    if writer_module == WriterModules.EV42.value:
        return __create_ev42_stream(index_kb, index_mb, source, stream_object, topic)
    if writer_module == WriterModules.HS00.value:
        data_type = stream_object[DATA_TYPE]
        error_type = stream_object[ERROR_TYPE]
        edge_type = stream_object[EDGE_TYPE]
        shape = stream_object[SHAPE]
        return HS00Stream(
            source=source,
            topic=topic,
            data_type=data_type,
            error_type=error_type,
            edge_type=edge_type,
            shape=shape,
        )
    if writer_module == WriterModules.NS10.value:
        return NS10Stream(source=source, topic=topic)
    if writer_module == WriterModules.SENV.value:
        return SENVStream(source=source, topic=topic)
    if writer_module == WriterModules.TDCTIME.value:
        return TDCTStream(source=source, topic=topic)


def __create_ev42_stream(
    index_kb: str, index_mb: str, source: str, stream_object: Dict, topic: str
):
    adc = stream_object[ADC_PULSE_DEBUG] if ADC_PULSE_DEBUG in stream_object else None
    chunk_mb = (
        stream_object[CHUNK_CHUNK_MB] if CHUNK_CHUNK_MB in stream_object else None
    )
    chunk_kb = (
        stream_object[CHUNK_CHUNK_KB] if CHUNK_CHUNK_KB in stream_object else None
    )
    return EV42Stream(
        source=source,
        topic=topic,
        adc_pulse_debug=adc,
        nexus_indices_index_every_kb=index_kb,
        nexus_indices_index_every_mb=index_mb,
        nexus_chunk_chunk_mb=chunk_mb,
        nexus_chunk_chunk_kb=chunk_kb,
    )


def __create_f142_stream(
    index_kb: str, index_mb: str, source: str, stream_object: Dict, topic: str
):
    type = stream_object[CommonKeys.TYPE]
    value_units = stream_object[VALUE_UNITS] if VALUE_UNITS in stream_object else None
    array_size = stream_object[ARRAY_SIZE] if ARRAY_SIZE in stream_object else None
    store_latest_into = (
        stream_object[STORE_LATEST_INTO] if STORE_LATEST_INTO in stream_object else None
    )
    return F142Stream(
        source=source,
        topic=topic,
        type=type,
        value_units=value_units,
        array_size=array_size,
        nexus_indices_index_every_mb=index_mb,
        nexus_indices_index_every_kb=index_kb,
        store_latest_into=store_latest_into,
    )


class JSONReader:
    def __init__(self):
        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.warnings = []
        # key: component name, value: NeXus path pointing to transformation that component depends on
        self.depends_on_paths: Dict[str, str] = {}
        # key: component name, value: Component object created from the JSON information
        self.component_dictionary: Dict[str, Component] = {}

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
        for transformation in component.transforms:
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

        for item in children:
            _add_field_to_group(item, component)

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


def _create_group(json_object: Dict, parent: Group) -> Group:
    children = json_object[CommonKeys.CHILDREN]
    name = json_object[CommonKeys.NAME]
    group = Group(name=name, parent_node=parent)
    for item in children:
        if item[CommonKeys.TYPE] == NodeType.STREAM:
            group = StreamGroup(name=name, parent_node=parent)
            break

    for item in children:
        _add_field_to_group(item, group)

    _add_attributes(json_object, group)
    return group


def _create_dataset(json_object: Dict, parent: Group) -> Dataset:
    try:
        size = json_object[NodeType.DATASET][CommonKeys.SIZE]
    except KeyError:
        size = 1
    type = json_object[NodeType.DATASET][CommonKeys.TYPE]
    name = json_object[CommonKeys.NAME]
    values = json_object[CommonKeys.VALUES]
    if isinstance(values, list):
        # convert to a numpy array using specified type
        values = np.array(values, dtype=VALUE_TYPE_TO_NP[type])
    ds = Dataset(name=name, values=values, type=type, size=size, parent_node=parent)
    _add_attributes(json_object, ds)
    return ds


def _create_link(json_object: Dict) -> Link:
    name = json_object[CommonKeys.NAME]
    target = json_object[TARGET]
    return Link(name=name, target=target)


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
