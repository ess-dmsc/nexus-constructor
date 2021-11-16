import os
from typing import Dict, List

import xmltodict

PIXEL_COMPONENT_TYPES = {"NXdetector"}
COMPONENT_TYPES = {
    "NXmonitor",
    "NXdetector",
    "NXsample",
    "NXsource",
    "NXdisk_chopper",
    "NXaperture",
    "NXattenuator",
    "NXbeam_stop",
    "NXbending_magnet",
    "NXcapillary",
    "NXcollimator",
    "NXcrystal",
    "NXdata",
    "NXdetector_group",
    "NXdetector_module",
    "NXentry",
    "NXfermi_chopper",
    "NXfilter",
    "NXflipper",
    "NXfresnel_zone_plate",
    "NXgrating",
    "NXguide",
    "NXinsertion_device",
    "NXinstrument",
    "NXlog",
    "NXmirror",
    "NXmoderator",
    "NXmonochromator",
    "NXpinhole",
    "NXpolarizer",
    "NXpositioner",
    "NXsample",
    "NXsample_component",
    "NXsensor",
    "NXslit",
    "NXuser",
    "NXvelocity_selector",
    "NXxraylens",
    "NXtransformations",
}

CHOPPER_CLASS_NAME = "NXdisk_chopper"


def __list_base_class_files(file_list):
    for file in file_list:
        if file.endswith(".nxdl.xml"):
            yield file


def make_dictionary_of_class_definitions(
    repo_directory="nexus_definitions", black_list: List[str] = None
):
    base_class_dir = os.path.join(repo_directory, "base_classes")

    component_definitions: Dict[str, List] = {}
    all_class_definitions: Dict[str, List] = {}
    for base_class_file in __list_base_class_files(os.listdir(base_class_dir)):
        with open(os.path.join(base_class_dir, base_class_file)) as def_file:
            _create_base_class_dict(
                def_file.read(),
                black_list,
                all_class_definitions,
                component_definitions,
            )
    return all_class_definitions, component_definitions


def _create_base_class_dict(
    xml_text, black_list, class_definitions, component_definitions
):
    if black_list is None:
        black_list = []

    xml_definition = xmltodict.parse(xml_text)["definition"]
    nx_class_name = xml_definition["@name"]
    if nx_class_name in black_list:
        return
    class_fields = []
    try:
        fields = xml_definition["field"]
        try:
            for field in fields:
                class_fields.append(field["@name"])
        except Exception:
            class_fields.append(fields["@name"])
    except KeyError:
        pass
    class_definitions[nx_class_name] = class_fields
    if nx_class_name in COMPONENT_TYPES:
        component_definitions[nx_class_name] = class_fields
