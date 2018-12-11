import json
from typing import List
from geometry_constructor.data_model import Component, Geometry, CylindricalGeometry, OFFGeometry,\
    PixelGrid, PixelMapping, SinglePixelId, Transformation, Translation, Rotation
from geometry_constructor.qml_models.instrument_model import InstrumentModel


"""
Methods for converting the data from an InstrumentModel instance to json
"""


def generate_json(model: InstrumentModel):
    """
    Returns a formatted json string built from a given InstrumentModel

    :param model: The model to generate a json representation of
    :return: A string containing a json representation of the model"""
    data = {
        'sample': build_component_dictionary(model.components[0], model),
        'components': build_components_list(model)
    }
    return json.dumps(data, indent=2)


def build_components_list(model: InstrumentModel):
    """
    Builds a list of dictionaries for the non sample components in the InstrumentModel

    :param model: The model to use as a source of component data
    :return: A list of dictionaries containing components data
    """
    data = []
    for component in model.components[1:]:
        component_data = build_component_dictionary(component, model)
        data.append(component_data)
    return data


def build_component_dictionary(component: Component, model: InstrumentModel):
    """
    Builds a dictionary containing the data for a component in the model

    :param component: The component to build a describing dictionary for
    :param model: The model the component is in, used to determine the id number to store for its transform parent
    :return: A dictionary describing the component
    """
    data = {
        'name': component.name,
        'description': component.description,
        'type': component.component_type.value,
        'transform_id': model.components.index(component),
        'transforms': build_transform_list(component.transforms),
        'geometry': build_geometry_dictionary(component.geometry)
    }

    if component.pixel_data is not None:
        add_pixel_info_to_dictionary(data, component)

    parent = component.transform_parent
    if parent is not None and parent != component:
        data['transform_parent_id'] = model.components.index(parent)

        dependent_transform = component.dependent_transform
        if dependent_transform is not None:
            data['parent_transform_index'] = parent.transforms.index(dependent_transform)

    return data


def build_transform_list(transforms: List[Transformation]):
    data = []
    for transform in transforms:
        if isinstance(transform, Translation):
            data.append(
                {
                    'type': 'translate',
                    'name': transform.name,
                    'vector': {
                        'x': transform.vector.x,
                        'y': transform.vector.y,
                        'z': transform.vector.z
                    },
                    'unit': 'm'
                }
            )
        elif isinstance(transform, Rotation):
            data.append(
                {
                    'type': 'rotate',
                    'name': transform.name,
                    'axis': {
                        'x': transform.axis.x,
                        'y': transform.axis.y,
                        'z': transform.axis.z
                    },
                    'angle': {
                        'unit': 'degrees',
                        'value': transform.angle
                    }
                }
            )
    return data


def add_pixel_info_to_dictionary(json_data: dict, detector: Component):
    """
    Adds detector specific information to a component's data dictionary

    :param json_data: The component describing dictionary to add detector specific properties to
    :param detector: The detector that the dictionary describes, and to obtain additional data from
    """
    pixels = detector.pixel_data
    if isinstance(pixels, PixelGrid):
        json_data['pixel_grid'] = {
            'rows': pixels.rows,
            'columns': pixels.columns,
            'row_height': pixels.row_height,
            'column_width': pixels.col_width,
            'first_id': pixels.first_id,
            'count_direction': pixels.count_direction.name,
            'starting_corner': pixels.initial_count_corner.name
        }
    elif isinstance(pixels, PixelMapping):
        json_data['pixel_mapping'] = [
            {
                'face': face_no,
                'pixel_id': pixels.pixel_ids[face_no]
            }
            for face_no
            in range(len(pixels.pixel_ids))
            if pixels.pixel_ids[face_no] is not None
        ]
    elif isinstance(pixels, SinglePixelId):
        json_data['pixel_id'] = pixels.pixel_id


def build_geometry_dictionary(geometry: Geometry):
    """
    Builds a dictionary containing geometry information for converting to json

    :param geometry: The geometry to build a describing dictionary from
    """
    if isinstance(geometry, OFFGeometry):
        data = {
            'type': 'OFF',
            'vertices': [vector.xyz_list for vector in geometry.vertices],
            'winding_order': geometry.winding_order_indices,
            'faces': geometry.winding_order
        }
    elif isinstance(geometry, CylindricalGeometry):
        data = {
            'type': 'Cylinder',
            'base_center': {
                'x': geometry.base_center_point.x,
                'y': geometry.base_center_point.y,
                'z': geometry.base_center_point.z
            },
            'base_edge': {
                'x': geometry.base_edge_point.x,
                'y': geometry.base_edge_point.y,
                'z': geometry.base_edge_point.z
            },
            'top_center': {
                'x': geometry.top_center_point.x,
                'y': geometry.top_center_point.y,
                'z': geometry.top_center_point.z
            },
            'axis_direction': {
                'x': geometry.axis_direction.x,
                'y': geometry.axis_direction.y,
                'z': geometry.axis_direction.z
            },
            'height': geometry.height,
            'radius': geometry.radius
        }
    else:
        data = None
    return data
