"""
Functions to write data in an InstrumentModel to nexus filewriter json

This module contains all the functions used to format the data.
It is recommended that instead of importing this module, the root of the package be imported instead, as this exposes
only the required root function to generate the json

Json format description can be found at https://github.com/ess-dmsc/kafka-to-nexus/
"""
import json
from nexus_constructor.component import Component
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, SinglePixelId
from nexus_constructor.transformations import Translation, Rotation
from nexus_constructor.geometry_types import CylindricalGeometry, OFFGeometry
from nexus_constructor.nexus import (
    external_component_types,
    component_class_name,
    ancestral_dependent_transform,
    absolute_transform_path_name,
    pixel_mapping,
    geometry_group_name,
    pixel_grid_x_offsets,
    pixel_grid_y_offsets,
    pixel_grid_z_offsets,
    pixel_grid_detector_ids,
)
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from typing import List


def generate_json(model: InstrumentModel):
    """
    Returns a formatted json string built from a given InstrumentModel

    :param model: The model to generate a json representation of
    :return: A string containing a json representation of the model
    """
    internal_components = [
        component
        for component in model.components
        if component.component_type not in external_component_types()
    ]
    external_components = [
        component
        for component in model.components
        if component.component_type in external_component_types()
    ]

    data = {
        "nexus_structure": {
            "children": [
                {
                    "type": "group",
                    "name": "instrument",
                    "attributes": {"NX_class": "NXinstrument"},
                    "children": generate_component_list(internal_components),
                }
            ]
        }
    }
    data["nexus_structure"]["children"].extend(
        generate_component_list(external_components)
    )

    return json.dumps(data, indent=2)


def generate_component_list(components: List[Component]):
    """Returns a list of dictionaries describing the components provided"""
    return [generate_component_data(component) for component in components]


def generate_component_data(component: Component):
    """Builds and returns a dictionary containing the details of the given component that can be written to json"""
    data = {
        "type": "group",
        "name": component.name,
        "attributes": {
            "NX_class": component_class_name(component.nx_class),
            "description": component.description,
        },
        "children": [],
    }
    add_transform_data(data, component)
    add_geometry_and_pixel_data(data, component)
    return data


def add_transform_data(json_data: dict, component: Component):
    """Adds properties to a dictionary describing the transforms in the component"""
    dependent_on = ancestral_dependent_transform(component)

    if len(component.transforms) > 0:

        nx_transforms = {
            "type": "group",
            "name": "transforms",
            "attributes": {"NX_class": "NXtransformations"},
            "children": [],
        }

        for transform in component.transforms:
            if isinstance(transform, Rotation):
                type_name = "rotation"
                units = "degrees"
                vector = (
                    transform.axis.toTuple()
                    if transform.axis.length() != 0
                    else [0, 0, 0]
                )
                value = transform.angle
            elif isinstance(transform, Translation):
                type_name = "translation"
                units = "m"
                vector = (
                    transform.vector.normalized().toTuple()
                    if transform.vector.length() != 0
                    else [0, 0, 0]
                )
                value = transform.vector.length()
            else:
                continue

            nx_transforms["children"].append(
                {
                    "type": "dataset",
                    "name": transform.name,
                    "dataset": {"type": "double", "size": [1]},
                    "attributes": [
                        {"name": "transformation_type", "values": type_name},
                        {"name": "depends_on", "values": dependent_on},
                        {"name": "units", "values": units},
                        {"name": "offset", "values": [0.0, 0.0, 0.0], "type": "double"},
                        {"name": "vector", "values": vector, "type": "double"},
                    ],
                    "values": value,
                }
            )
            dependent_on = absolute_transform_path_name(
                transform,
                component,
                component.nx_class not in external_component_types(),
            )
        json_data["children"].append(nx_transforms)

    json_data["attributes"]["depends_on"] = dependent_on


def add_geometry_and_pixel_data(json_data: dict, component: Component):
    """Adds properties describing the geometry and pixel data of the component to its json dictionary"""
    geometry = component.geometry
    pixel_data = component.pixel_data
    geometry_group = geometry_group_name(component)

    if isinstance(geometry, CylindricalGeometry):
        nexus_geometry = {
            "type": "group",
            "name": geometry_group,
            "attributes": {"NX_class": "NXcylindrical_geometry"},
            "children": [
                {
                    "type": "dataset",
                    "name": "vertices",
                    "dataset": {"type": "double", "size": [3, 3]},
                    "values": [
                        geometry.base_center_point.toTuple(),
                        geometry.base_edge_point.toTuple(),
                        geometry.top_center_point.toTuple(),
                    ],
                },
                {
                    "type": "dataset",
                    "name": "cylinders",
                    "dataset": {"type": "int64", "size": [1, 3]},
                    "values": [[0, 1, 2]],
                },
            ],
        }
    elif isinstance(geometry, OFFGeometry):
        nexus_geometry = {
            "type": "group",
            "name": geometry_group,
            "attributes": {"NX_class": "NXoff_geometry"},
            "children": [
                {
                    "type": "dataset",
                    "name": "vertices",
                    "dataset": {"type": "double", "size": [len(geometry.vertices), 3]},
                    "values": [vertex.toTuple() for vertex in geometry.vertices],
                },
                {
                    "type": "dataset",
                    "name": "winding_order",
                    "dataset": {"type": "int64", "size": [len(geometry.winding_order)]},
                    "values": geometry.winding_order,
                },
                {
                    "type": "dataset",
                    "name": "faces",
                    "dataset": {
                        "type": "int64",
                        "size": [len(geometry.winding_order_indices)],
                    },
                    "values": geometry.winding_order_indices,
                },
            ],
        }
        if isinstance(pixel_data, PixelMapping):
            mapping_list = pixel_mapping(pixel_data)
            nexus_geometry["children"].append(
                {
                    "type": "dataset",
                    "name": "detector_faces",
                    "dataset": {"type": "int64", "size": [len(mapping_list), 2]},
                    "values": mapping_list,
                }
            )
    else:
        return

    if isinstance(pixel_data, PixelGrid):
        json_data["children"].append(
            {
                "type": "dataset",
                "name": "x_pixel_offset",
                "dataset": {
                    "type": "double",
                    "size": [pixel_data.rows, pixel_data.columns],
                },
                "values": pixel_grid_x_offsets(pixel_data),
            }
        )
        json_data["children"].append(
            {
                "type": "dataset",
                "name": "y_pixel_offset",
                "dataset": {
                    "type": "double",
                    "size": [pixel_data.rows, pixel_data.columns],
                },
                "values": pixel_grid_y_offsets(pixel_data),
            }
        )
        json_data["children"].append(
            {
                "type": "dataset",
                "name": "z_pixel_offset",
                "dataset": {
                    "type": "double",
                    "size": [pixel_data.rows, pixel_data.columns],
                },
                "values": pixel_grid_z_offsets(pixel_data),
            }
        )
        json_data["children"].append(
            {
                "type": "dataset",
                "name": "detector_number",
                "dataset": {
                    "type": "int64",
                    "size": [pixel_data.rows, pixel_data.columns],
                },
                "values": pixel_grid_detector_ids(pixel_data),
            }
        )
    elif isinstance(pixel_data, SinglePixelId):
        # TODO: Replace this Mantid compatibility dataset, with the nexus standard's way (once it exists)
        json_data["children"].append(
            {
                "type": "dataset",
                "name": "detector_id",
                "dataset": {"type": "int64", "size": [1]},
                "values": pixel_data.pixel_id,
            }
        )

    json_data["children"].append(nexus_geometry)
