from typing import List
import os
import xmltodict


PIXEL_COMPONENT_TYPES = ["NXmonitor", "NXdetector", "NXdetector_module"]


def __list_base_class_files(file_list):
    for file in file_list:
        if file.endswith(".nxdl.xml"):
            yield file


def make_dictionary_of_class_definitions(
    repo_directory="nexus_definitions", black_list: List[str] = None
):

    base_class_dir = os.path.join(repo_directory, "base_classes")

    class_definitions = {}
    for base_class_file in __list_base_class_files(os.listdir(base_class_dir)):
        with open(os.path.join(base_class_dir, base_class_file)) as def_file:
            _create_base_class_dict(def_file.read(), black_list, class_definitions)
    return class_definitions


def _create_base_class_dict(xml_text, black_list, class_definitions):
    if black_list is None:
        black_list = []

    xml_definition = xmltodict.parse(xml_text)["definition"]
    nx_class_name = xml_definition["@name"]
    if nx_class_name in black_list:
        return
    class_definitions[nx_class_name] = []
    try:
        fields = xml_definition["field"]
        try:
            for field in fields:
                class_definitions[nx_class_name].append(field["@name"])
        except Exception:
            class_definitions[nx_class_name].append(fields["@name"])
    except KeyError:
        pass
