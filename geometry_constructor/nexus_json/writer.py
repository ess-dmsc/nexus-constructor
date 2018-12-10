import json
from PySide2.QtCore import QObject, QUrl, Slot
from geometry_constructor.data_model import Component, Translation, Rotation, CylindricalGeometry, OFFGeometry,\
    PixelGrid, PixelMapping, SinglePixelId
from geometry_constructor.nexus import NexusEncoder
from geometry_constructor.qml_models.instrument_model import InstrumentModel


class Writer(QObject):
    """
    Loads data from a nexus FileWriter JSON command into an InstrumentModel
    Format description can be found at https://github.com/ess-dmsc/kafka-to-nexus/
    """

    @Slot(QUrl, 'QVariant')
    def save_json(self, file_url: QUrl, model: InstrumentModel):
        """
        Writes a json file containing a representation of an InstrumentModel

        :param file_url: The url to save the json file to
        :param model: The model to generate the json from
        """
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        json_data = Writer.generate_json(model)
        with open(filename, 'w') as file:
            file.write(json_data)

    @staticmethod
    def generate_json(model: InstrumentModel):
        """
        Returns a formatted json string built from a given InstrumentModel

        :param model: The model to generate a json representation of
        :return: A string containing a json representation of the model
        """
        data = {
            'nexus_structure': {
                'children': [
                    {
                        'type': 'group',
                        'name': 'instrument',
                        'attributes': {
                            'NX_class': 'NXinstrument',
                        },
                        'children': Writer.generate_component_list(model),
                    },
                    Writer.generate_component_data(model.components[0])
                ],
            },
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def generate_component_list(model: InstrumentModel):
        """Returns a list of dictionaries describing the (non sample) components of the model"""
        return [Writer.generate_component_data(component) for component in model.components[1:]]

    @staticmethod
    def generate_component_data(component: Component):
        """Builds and returns a dictionary containing the details of the given component that can be written to json"""
        data = {
            'type': 'group',
            'name': component.name,
            'attributes': {
                'NX_class': NexusEncoder.component_class_name(component.component_type),
                'description': component.description,
            },
            'children': []
        }
        Writer.add_transform_data(data, component)
        Writer.add_geometry_and_pixel_data(data, component)
        return data

    @staticmethod
    def add_transform_data(json_data: dict, component: Component):
        """Adds properties to a dictionary describing the transforms in the component"""
        dependent_on = NexusEncoder.ancestral_dependent_transform(component)

        for transform in component.transforms:
            if isinstance(transform, Rotation):
                type_name = 'rotation'
                units = 'degrees',
                vector = transform.axis.xyz_list
                value = transform.angle
            elif isinstance(transform, Translation):
                type_name = 'translation'
                units = 'm'
                vector = transform.vector.unit_list
                value = transform.vector.magnitude
            else:
                continue

            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': transform.name,
                    'dataset': {
                        'type': 'float',
                        'size': [1],
                    },
                    'attributes': {
                        'NX_class': 'NXtransformations',
                        'transformation_type': type_name,
                        'depends_on': dependent_on,
                        'units': units,
                        'offset': [0.0, 0.0, 0.0],
                        'vector': vector,
                    },
                    'values': value,
                }
            )
            dependent_on = transform.name

        json_data['attributes']['depends_on'] = dependent_on

    @staticmethod
    def add_geometry_and_pixel_data(json_data: dict, component: Component):
        """Adds properties describing the geometry and pixel data of the component to its json dictionary"""
        geometry = component.geometry
        pixel_data = component.pixel_data
        if isinstance(geometry, CylindricalGeometry):
            nexus_geometry = {
                'type': 'group',
                'name': 'geometry',
                'attributes': {
                    'NX_class': 'NXcylindrical_geometry'
                },
                'children': [
                    {
                        'type': 'dataset',
                        'name': 'vertices',
                        'dataset': {
                            'type': 'float',
                            'size': [3, 3],
                        },
                        'values': [
                            geometry.base_center_point.xyz_list,
                            geometry.base_edge_point.xyz_list,
                            geometry.top_center_point.xyz_list,
                        ],
                    },
                    {
                        'type': 'dataset',
                        'name': 'cylinders',
                        'dataset': {
                            'type': 'int64',
                            'size': [1, 3],
                        },
                        'values': [[0, 1, 2]],
                    },
                ],
            }
        elif isinstance(geometry, OFFGeometry):
            nexus_geometry = {
                'type': 'group',
                'name': 'geometry',
                'attributes': {
                    'NX_class': 'NXoff_geometry',
                },
                'children': [
                    {
                        'type': 'dataset',
                        'name': 'vertices',
                        'dataset': {
                            'type': 'float',
                            'size': [len(geometry.vertices), 3]
                        },
                        'values': [vertex.xyz_list for vertex in geometry.vertices],
                    },
                    {
                        'type': 'dataset',
                        'name': 'winding_order',
                        'dataset': {
                            'type': 'int64',
                            'size': [len(geometry.winding_order)]
                        },
                        'values': geometry.winding_order,
                    },
                    {
                        'type': 'dataset',
                        'name': 'faces',
                        'dataset': {
                            'type': 'int64',
                            'size': [len(geometry.winding_order_indices)]
                        },
                        'values': geometry.winding_order_indices,
                    },
                ],
            }
            if isinstance(pixel_data, PixelMapping):
                mapping_list = NexusEncoder.pixel_mapping(pixel_data)
                nexus_geometry['children'].append(
                    {
                        'type': 'dataset',
                        'name': 'detector_faces',
                        'dataset': {
                            'type': 'int64',
                            'size': [len(mapping_list), 2]
                        },
                        'values': mapping_list,
                    }
                )
        else:
            return

        if isinstance(pixel_data, PixelGrid):
            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': 'x_pixel_offset',
                    'dataset': {
                        'type': 'float',
                        'size': [pixel_data.rows, pixel_data.columns]
                    },
                    'values': NexusEncoder.pixel_grid_x_offsets(pixel_data),
                }
            )
            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': 'y_pixel_offset',
                    'dataset': {
                        'type': 'float',
                        'size': [pixel_data.rows, pixel_data.columns]
                    },
                    'values': NexusEncoder.pixel_grid_y_offsets(pixel_data),
                }
            )
            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': 'z_pixel_offset',
                    'dataset': {
                        'type': 'float',
                        'size': [pixel_data.rows, pixel_data.columns]
                    },
                    'values': NexusEncoder.pixel_grid_z_offsets(pixel_data),
                }
            )
            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': 'detector_number',
                    'dataset': {
                        'type': 'int64',
                        'size': [pixel_data.rows, pixel_data.columns]
                    },
                    'values': NexusEncoder.pixel_grid_detector_ids(pixel_data),
                }
            )
        elif isinstance(pixel_data, SinglePixelId):
            # TODO: Replace this Mantid compatibility dataset, with the nexus standard's way (once it exists)
            json_data['children'].append(
                {
                    'type': 'dataset',
                    'name': 'detector_id',
                    'dataset': {
                        'type': 'int64',
                        'size': [1]
                    },
                    'values': pixel_data.pixel_id,
                }
            )

        json_data['children'].append(nexus_geometry)
