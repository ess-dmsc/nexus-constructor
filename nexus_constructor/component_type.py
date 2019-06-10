from typing import List
import os
import xmltodict


PIXEL_COMPONENT_TYPES = ["NXmonitor", "NXdetector", "NXdetector_module"]

# TODO: unit test this


def __list_base_class_files(repo_directory):
    base_class_dir = os.path.join(repo_directory, "base_classes")
    for file in os.listdir(base_class_dir):
        if file.endswith(".nxdl.xml"):
            yield os.path.join(base_class_dir, file)


def make_dictionary_of_class_definitions(
    repo_directory="nexus_definitions", black_list: List[str] = None
):
    if black_list is None:
        black_list = []

    class_definitions = {}
    for base_class_file in __list_base_class_files(repo_directory):
        with open(base_class_file) as def_file:
            xml_definition = xmltodict.parse(def_file.read())["definition"]
            nx_class_name = xml_definition["@name"]
            if nx_class_name in black_list:
                continue
            class_definitions[nx_class_name] = []
            try:
                fields = xml_definition["field"]
                try:
                    for field in fields:
                        class_definitions[nx_class_name].append(field["@name"])
                except Exception:
                    class_definitions[nx_class_name].append(fields["@name"])
            except KeyError:
                # TODO: No key called "field"
                pass
    return class_definitions
