import json
from PySide2.QtCore import QObject, QUrl, Slot
from geometry_constructor.data_model import Component, Sample, Detector, CylindricalGeometry, OFFGeometry, PixelGrid,\
    PixelMapping, CountDirection, Corner, Vector
from geometry_constructor.instrument_model import InstrumentModel


class JsonLoader(QObject):
    """
    Loads json produced by the JsonWriter class back into an InstrumentModel

    transform_id_mapping is a mapping of components transform_id numbers to the component objects
    transform_parent_ids is a mapping of transform_id numbers of components to the transform_id of their parent
    """

    def __init__(self):
        super().__init__()
        # transform_id -> component
        self.transform_id_mapping = {}
        # transform_id -> parent's transform_id
        self.transform_parent_ids = {}

    @Slot(QUrl, 'QVariant')
    def load_file_into_instrument_model(self, file_url: QUrl, model: InstrumentModel):
        """
        Loads a json file into an instrument model
        :param file_url: The url of the file to load
        :param model: The model that the loaded components will be stored in
        """
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        with open(filename, 'r') as file:
            json_data = file.read()
        self.load_json_into_instrument_model(json_data, model)

    def load_json_into_instrument_model(self, json_data: str, model: InstrumentModel):
        """
        Loads a json string into an instrument model
        :param json_data: String containing the json data to load
        :param model: The model the loaded components will be stored in
        """
        # Reset the transform mappings
        self.transform_id_mapping = {}
        self.transform_parent_ids = {}
        # Build the sample and components from the data
        data = json.loads(json_data)
        sample = self.load_component(data['sample'])
        components = [sample]
        for component_data in data['components']:
            components.append(self.load_component(component_data))
        # Set transform parent links
        for (child_id, parent_id) in self.transform_parent_ids.items():
            child = self.transform_id_mapping[child_id]
            parent = self.transform_id_mapping[parent_id]
            child.transform_parent = parent

        model.replace_contents(components)

    def load_component(self, json_obj: dict):
        """
        Builds a component object from a dictionary containing its properties
        :param json_obj: the dictionary build from json
        :return: the loaded, populated component
        """
        component_type = json_obj['type']
        if component_type == Sample.__name__:
            component = Sample()
        elif component_type == Detector.__name__:
            component = Detector()
            if 'pixel_grid' in json_obj:
                grid = json_obj['pixel_grid']
                component.pixel_data = PixelGrid(rows=grid['rows'],
                                                 columns=grid['columns'],
                                                 row_height=grid['row_height'],
                                                 col_width=grid['column_width'],
                                                 first_id=grid['first_id'],
                                                 count_direction=CountDirection[grid['count_direction']],
                                                 initial_count_corner=Corner[grid['starting_corner']])
            elif 'pixel_mapping' in json_obj:
                mapping = json_obj['pixel_mapping']
                face_count = len(json_obj['geometry']['winding_order'])
                pixel_ids = {}
                for i in range(face_count):
                    pixel_ids[i] = None
                for pixel in mapping:
                    face_no = pixel['face']
                    pixel_id = pixel['pixel_id']
                    pixel_ids[face_no] = pixel_id

                component.pixel_data = PixelMapping(pixel_ids=[pixel_ids[i] for i in range(face_count)])
        else:
            component = Component()
        component.name = json_obj['name']
        component.description = json_obj['description']
        for transform in json_obj['transforms']:
            if transform['type'] == 'rotate':
                component.rotate_axis = Vector(transform['axis']['x'],
                                               transform['axis']['y'],
                                               transform['axis']['z'])
                component.rotate_angle = transform['angle']['value']
            elif transform['type'] == 'translate':
                component.translate_vector = Vector(transform['vector']['x'],
                                                    transform['vector']['y'],
                                                    transform['vector']['z'])

        component.geometry = self.load_geometry(json_obj['geometry'])
        self.transform_id_mapping[json_obj['transform_id']] = component
        if 'transform_parent_id' in json_obj:
            self.transform_parent_ids[json_obj['transform_id']] = json_obj['transform_parent_id']
        return component

    def load_geometry(self, geometry_obj: dict):
        """Builds and returns a Geometry instance based on the dictionary describing it"""
        if geometry_obj['type'] == 'OFF':
            wound_faces = geometry_obj['faces']
            face_indices = geometry_obj['winding_order'] + [len(wound_faces)]
            return OFFGeometry(vertices=[Vector(vertex[0], vertex[1], vertex[2])
                                         for vertex
                                         in geometry_obj['vertices']],
                               faces=[wound_faces[face_indices[i]:face_indices[i+1]]
                                      for i
                                      in range(len(face_indices) - 1)])
        elif geometry_obj['type'] == 'Cylinder':
            axis_direction = Vector(geometry_obj['axis_direction']['x'],
                                    geometry_obj['axis_direction']['y'],
                                    geometry_obj['axis_direction']['z'])
            return CylindricalGeometry(axis_direction=axis_direction,
                                       height=geometry_obj['height'],
                                       radius=geometry_obj['radius'])
        else:
            return None
