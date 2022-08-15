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
ENTRY_CLASS_NAME = "NXentry"
LOG_CLASS_NAME = "NXlog"
SOURCE_CLASS_NAME = "NXsource"
SAMPLE_CLASS_NAME = "NXsample"
SLIT_CLASS_NAME = "NXslit"


def __list_base_class_files(file_list):
    for file in file_list:
        if file.endswith(".nxdl.xml"):
            yield file


def make_dictionary_of_class_definitions(
    repo_directory="nexus_definitions", not_allowed: List[str] = None
):
    base_class_dir = os.path.join(repo_directory, "base_classes")

    component_definitions: Dict[str, List] = {}
    all_class_definitions: Dict[str, List] = {}
    for base_class_file in __list_base_class_files(os.listdir(base_class_dir)):
        with open(os.path.join(base_class_dir, base_class_file)) as def_file:
            _create_base_class_dict(
                def_file.read(),
                not_allowed,
                all_class_definitions,
                component_definitions,
            )
    return all_class_definitions, component_definitions


nexus_dtype_dict = {
    "NX_CHAR": "string",
    "NX_DATE_TIME": "string",
    "NX_FLOAT": "double",
    "NX_INT": "int64",
    "NX_NUMBER": "double",
    "NX_POSINT": "uint64",
    "NX_UINT": "uint64",
}

nexus_units_dict = {
    "NX_ANGLE": "rad",
    "NX_AREA": "m^2",
    "NX_CHARGE": "C",
    "NX_CROSS_SECTION": "m^2",
    "NX_CURRENT": "A",
    "NX_EMITTANCE": "nm*rad",
    "NX_ENERGY": "J",
    "NX_FLUX": "1/s/m^2",
    "NX_FREQUENCY": "Hz",
    "NX_LENGTH": "m",
    "NX_MASS": "kg",
    "NX_MASS_DENSITY": "kg/m^3",
    "NX_MOLECULAR_WEIGHT": "g/mol",
    "NX_PERIOD": "s",
    "NX_PER_AREA": "1/m^2",
    "NX_PER_LENGTH": "1/m",
    "NX_POWER": "W",
    "NX_PRESSURE": "Pa",
    "NX_SCATTERING_LENGTH_DENSITY": "m/m^3",
    "NX_TEMPERATURE": "K",
    "NX_TIME": "s",
    "NX_TIME_OF_FLIGHT": "s",
    "NX_VOLTAGE": "V",
    "NX_VOLUME": "m^3",
    "NX_WAVELENGTH": "nm",
    "NX_WAVENUMBER": "1/nm",
}


def _create_base_class_dict(
    xml_text, not_allowed, class_definitions, component_definitions
):
    if not_allowed is None:
        not_allowed = []

    xml_definition = xmltodict.parse(xml_text)["definition"]
    nx_class_name = xml_definition["@name"]
    if nx_class_name in not_allowed:
        return
    class_fields = []
    try:
        fields = xml_definition["field"]
        try:
            for field in fields:
                data_type = "string"
                units = ""
                if "@type" in field:
                    data_type = nexus_dtype_dict.get(field["@type"], "double")
                if "@units" in field:
                    units = nexus_units_dict.get(field["@units"], "")
                class_fields.append((field["@name"], data_type, units))
        except Exception:
            data_type = "string"
            units = ""
            if "@type" in fields:
                data_type = nexus_dtype_dict.get(fields["@type"], "double")
            if "@units" in fields:
                units = nexus_units_dict.get(fields["@units"], "")
            class_fields.append((fields["@name"], data_type, units))
    except KeyError:
        pass
    class_definitions[nx_class_name] = class_fields
    if nx_class_name in NX_CLASSES:
        component_definitions[nx_class_name] = class_fields
