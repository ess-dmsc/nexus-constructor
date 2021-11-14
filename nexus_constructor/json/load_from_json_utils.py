from typing import Any, Dict, List, Optional, Union

import numpy as np

from nexus_constructor.common_attrs import (
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.model.group import TRANSFORMS_GROUP_NAME, Group
from nexus_constructor.model.stream import (
    ARRAY_SIZE,
    DATA_TYPE,
    DATASET,
    EDGE_TYPE,
    ERROR_TYPE,
    INDEX_EVERY_KB,
    INDEX_EVERY_MB,
    LINK,
    SHAPE,
    SOURCE,
    TOPIC,
    VALUE_UNITS,
    Dataset,
    EV42Stream,
    F142Stream,
    FileWriterModule,
    HS00Stream,
    Link,
    NS10Stream,
    SENVStream,
    Stream,
    TDCTStream,
    WriterModules,
)
from nexus_constructor.model.value_type import VALUE_TYPE_TO_NP

DEPENDS_ON_IGNORE = [None, "."]


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


def _add_field_to_group(item: Dict, group: Group):
    child: Group
    if CommonKeys.TYPE in item:
        if item[CommonKeys.NAME] == TRANSFORMS_GROUP_NAME:
            return
        field_type = item[CommonKeys.TYPE]
        child_name = item[CommonKeys.NAME]
        if field_type == NodeType.GROUP:
            child = _create_group(item, group)
        else:
            raise Exception(
                f'Found unknown field type ("{field_type}") when loading JSON - {child_name}'
            )
        group[child_name] = child
    elif CommonKeys.MODULE in item:
        stream: Union[FileWriterModule, Group]
        writer_module = item[CommonKeys.MODULE]
        if writer_module == LINK:
            stream = _create_link(item)
        elif writer_module == DATASET:
            if item[NodeType.CONFIG][CommonKeys.NAME] == CommonAttrs.DEPENDS_ON:
                return
            stream = _create_dataset(item, group)
        else:
            stream = _create_stream(item)
        group.children.append(
            stream
        )  # Can't use the `[]` operator because streams do not have a name to use as a key
    else:
        raise Exception(
            "Unable to add field as neither writer module type nor child type was found in the current node."
        )


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


def _find_attribute_from_dict(attribute_name: str, entry: dict) -> Any:
    """
    Attempts to fing an attribute in a dictionary by looking for the value associated with the attribute key,
    or by looking for the "values" fields.
    :param entry: The dictionary containing the information.
    :return: The attribute value if it could be found, otherwise None.
    """
    if entry.get(CommonKeys.NAME) == attribute_name:
        return entry.get(CommonKeys.VALUES)
    if entry.get(attribute_name):
        return entry.get(attribute_name)
    return None


def _find_attribute_from_list_or_dict(
    attribute_name: str,
    entry: Union[list, dict],
) -> Any:
    """
    Attempts to determine the value of an attribute in a dictionary or a list of dictionaries.
    :param entry: A dictionary of list of a dictionaries.
    :return: The attribute value if it can be found, otherwise None.
    """
    if isinstance(entry, list):
        for item in entry:
            attribute = _find_attribute_from_dict(attribute_name, item)
            if attribute:
                return attribute
        return None
    elif isinstance(entry, dict):
        return _find_attribute_from_dict(attribute_name, entry)


def _find_nx_class(entry: Union[list, dict]) -> str:
    """
    Tries to find the NX class value from a dictionary or a list of dictionaries.
    :param entry: A dictionary or list of dictionaries.
    :return: The NXclass if it could be found, otherwise an empty string is returned.
    """
    nx_class = _find_attribute_from_list_or_dict(CommonAttrs.NX_CLASS, entry)
    return nx_class if nx_class is not None else ""


def _create_stream(json_object: Dict) -> Stream:
    """
    Given a dictionary containing a stream, create a corresponding stream object to be used in the model.
    :param json_object: JSON dictionary containing a stream.
    :return: A stream object containing relevant data from the JSON.
    """
    stream_object = json_object[NodeType.CONFIG]
    writer_module = json_object[CommonKeys.MODULE]
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
        return HS00Stream(  # type: ignore
            source=source,
            topic=topic,
            data_type=data_type,
            error_type=error_type,
            edge_type=edge_type,
            shape=shape,
        )
    if writer_module == WriterModules.NS10.value:
        return NS10Stream(parent_node=None, source=source, topic=topic)
    if writer_module == WriterModules.SENV.value:
        return SENVStream(parent_node=None, source=source, topic=topic)
    if writer_module == WriterModules.TDCTIME.value:
        return TDCTStream(parent_node=None, source=source, topic=topic)

    return None


def __create_ev42_stream(
    index_kb: str, index_mb: str, source: str, stream_object: Dict, topic: str
):
    return EV42Stream(
        parent_node=None,
        source=source,
        topic=topic,
    )


def __create_f142_stream(
    index_kb: str, index_mb: str, source: str, stream_object: Dict, topic: str
):
    value_type = stream_object[CommonKeys.DATA_TYPE]
    value_units = stream_object[VALUE_UNITS] if VALUE_UNITS in stream_object else None
    array_size = stream_object[ARRAY_SIZE] if ARRAY_SIZE in stream_object else None
    return F142Stream(
        parent_node=None,
        source=source,
        topic=topic,
        type=value_type,
        value_units=value_units,
        array_size=array_size,
    )


def _create_group(json_object: Dict, parent: Group) -> Group:
    children = json_object[CommonKeys.CHILDREN]
    name = json_object[CommonKeys.NAME]
    group = Group(name=name, parent_node=parent)
    for item in children:
        if CommonKeys.MODULE in item:
            group = Group(name=name, parent_node=parent)
            break

    for item in children:
        _add_field_to_group(item, group)

    _add_attributes(json_object, group)
    return group


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
    return Link(parent_node=None, name=name, source=target)


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
