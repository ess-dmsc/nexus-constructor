import json
from PySide2.QtCore import QObject, QUrl, Signal, Slot
from geometry_constructor.data_model import Component, Detector, Geometry, CylindricalGeometry, OFFGeometry,\
    PixelGrid, PixelMapping
from geometry_constructor.instrument_model import InstrumentModel


class JsonWriter(QObject):
    """
    Converts the data from an InstrumentModel instance to json
    """

    requested_model_json = Signal(str)

    @Slot('QVariant')
    def request_model_json(self, model: InstrumentModel):
        """
        Generates json from the InstrumentModel and sends it to slots connected to the requested_model_json signal
        """
        self.requested_model_json.emit(self.generate_json(model))

    @Slot('QVariant')
    def print_json_to_console(self, model: InstrumentModel):
        """Generates json from an InstrumentModel instance and writes it to the console"""
        print(self.generate_json(model))

    @Slot(QUrl, 'QVariant')
    def save_json(self, file_url: QUrl, model: InstrumentModel):
        """Generates json from an InstrumentModel"""
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        json_data = self.generate_json(model)
        with open(filename, 'w') as file:
            file.write(json_data)

    def generate_json(self, model: InstrumentModel):
        """Returns a formatted json string built from the given InstrumentModel"""
        data = {
            'sample': self.build_component_dictionary(model.components[0], model),
            'components': self.build_components_list(model)
        }
        return json.dumps(data, indent=2)

    def build_components_list(self, model: InstrumentModel):
        """Builds a list of dictionaries for the non sample components in the InstrumentModel"""
        data = []
        for component in model.components[1:]:
            component_data = self.build_component_dictionary(component, model)
            if isinstance(component, Detector):
                self.add_detector_info_to_dictionary(component_data, component)
            data.append(component_data)
        return data

    def build_component_dictionary(self, component: Component, model: InstrumentModel):
        """Builds a dictionary containing the data for a component in the model"""
        data = {
            'name': component.name,
            'description': component.description,
            'type': type(component).__name__,
            'transform_id': model.components.index(component),
            'transforms': [
                {
                    'type': 'rotate',
                    'axis': {
                        'x': component.rotate_axis.x,
                        'y': component.rotate_axis.y,
                        'z': component.rotate_axis.z
                    },
                    'angle': {
                        'unit': 'degrees',
                        'value': component.rotate_angle
                    }
                },
                {
                    'type': 'translate',
                    'vector': {
                        'x': component.translate_vector.x,
                        'y': component.translate_vector.y,
                        'z': component.translate_vector.z
                    },
                    'unit': 'm'
                }
            ],
            'geometry': self.build_geometry_dictionary(component.geometry)
        }

        parent = component.transform_parent
        if parent is not None and parent != component:
            data['transform_parent_id'] = model.components.index(parent)

        return data

    def add_detector_info_to_dictionary(self, json_data: dict, detector: Detector):
        """Adds detector specific information to a component's data dictionary"""
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

    def build_geometry_dictionary(self, geometry: Geometry):
        """Builds a dictionary containing geometry information for converting to json"""
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
