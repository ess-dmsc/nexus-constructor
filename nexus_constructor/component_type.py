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
    "NXdetector_group",
    "NXdetector_module",
    "NXfermi_chopper",
    "NXfilter",
    "NXflipper",
    "NXfresnel_zone_plate",
    "NXgrating",
    "NXguide",
    "NXinsertion_device",
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
    "NXvelocity_selector",
    "NXxraylens",
}

NX_CLASSES = {
    "NXaperture",
    "NXattenuator",
    "NXbeam",
    "NXbeam_stop",
    "NXbending_magnet",
    "NXcapillary",
    "NXcite",
    "NXcollection",
    "NXcollimator",
    "NXcrystal",
    "NXcylindrical_geometry",
    "NXdata",
    "NXdetector",
    "NXdetector_group",
    "NXdetector_module",
    "NXdisk_chopper",
    "NXentry",
    "NXenvironment",
    "NXevent_data",
    "NXfermi_chopper",
    "NXfilter",
    "NXflipper",
    "NXfresnel_zone_plate",
    "NXgeometry",
    "NXgrating",
    "NXguide",
    "NXinsertion_device",
    "NXinstrument",
    "NXlog",
    "NXmirror",
    "NXmoderator",
    "NXmonitor",
    "NXmonochromator",
    "NXnote",
    "NXobject",
    "NXoff_geometry",
    "NXorientation",
    "NXparameters",
    "NXpdb",
    "NXpinhole",
    "NXpolarizer",
    "NXpositioner",
    "NXprocess",
    "NXreflections",
    "NXroot",
    "NXsample",
    "NXsample_component",
    "NXsensor",
    "NXshape",
    "NXslit",
    "NXsource",
    "NXsubentry",
    "NXtransformations",
    "NXtranslation",
    "NXuser",
    "NXvelocity_selector",
    "NXxraylens",
}

CHOPPER_CLASS_NAME = "NXdisk_chopper"
SOURCE_CLASS_NAME = "NXsource"
SAMPLE_CLASS_NAME = "NXsample"
SLIT_CLASS_NAME = "NXslit"


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
    if nx_class_name in NX_CLASSES:
        component_definitions[nx_class_name] = class_fields
