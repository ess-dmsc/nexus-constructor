from typing import Dict, List

from nexus_constructor.component_type import nexus_dtype_dict, nexus_units_dict

required_component_fields: Dict[str, List[tuple]] = {
    # dict_key: nexus class,
    # item is a list of tuples where the tuple is on the format:
    # (field_name, datatype, array([0.0])/scalar(""), units).
    "NXslit": [
        ("x_gap", nexus_dtype_dict["NX_FLOAT"], "", nexus_units_dict["NX_LENGTH"]),
        ("y_gap", nexus_dtype_dict["NX_FLOAT"], "", nexus_units_dict["NX_LENGTH"]),
    ],
    "NXdisk_chopper": [
        ("slits", nexus_dtype_dict["NX_INT"], "", ""),
        (
            "slit_edges",
            nexus_dtype_dict["NX_FLOAT"],
            [0.0],
            nexus_units_dict["NX_ANGLE"],
        ),
        (
            "slit_height",
            nexus_dtype_dict["NX_FLOAT"],
            "",
            nexus_units_dict["NX_LENGTH"],
        ),
        ("radius", nexus_dtype_dict["NX_FLOAT"], "", nexus_units_dict["NX_LENGTH"]),
    ],
}
