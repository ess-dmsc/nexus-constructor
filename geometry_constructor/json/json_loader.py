from geometry_constructor.data_model import Component, ComponentType, CylindricalGeometry, OFFGeometry, PixelGrid,\
    PixelMapping, SinglePixelId, CountDirection, Corner, Vector, Translation, Rotation
from geometry_constructor.nexus import NexusDecoder
from geometry_constructor.qml_models.instrument_model import InstrumentModel


class JsonLoader:
    """
    Loads json produced by the JsonWriter class back into an InstrumentModel
    """

    @staticmethod
    def load_json_object_into_instrument_model(json_data: dict, model: InstrumentModel):
        """
        Loads a json string into an instrument model

        :param json_data: String containing the json data to load
        :param model: The model the loaded components will be stored in
        """
        # Build the sample and components from the data
        sample, transform_id, _, _ = JsonLoader.build_component(json_data['sample'])

        # transform_id -> component
        transform_id_mapping = {
            transform_id: sample
        }
        # transform_id -> parent's transform_id
        transform_parent_ids = {}
        # transform_id -> dependent transform index
        dependent_indexes = {}

        components = [sample]
        for component_data in json_data['components']:
            component, transform_id, transform_parent_id, dependent_index = JsonLoader.build_component(component_data)
            components.append(component)
            transform_id_mapping[transform_id] = component
            if transform_parent_id is not None:
                transform_parent_ids[transform_id] = transform_parent_id
                if dependent_index is not None:
                    dependent_indexes[transform_id] = dependent_index
        # Set transform parent links
        for (child_id, parent_id) in transform_parent_ids.items():
            child = transform_id_mapping[child_id]
            parent = transform_id_mapping[parent_id]
            child.transform_parent = parent
            if child_id in dependent_indexes:
                dependent_index = dependent_indexes[child_id]
                child.dependent_transform = parent.transforms[dependent_index]

        model.replace_contents(components)

    @staticmethod
    def build_component(json_obj: dict):
        """
        Builds a component object from a dictionary containing its properties

        If the relevant parameters aren't set in the object, the parent's transform id, and dependent transform index
        will be None

        :param json_obj: the dictionary built from json
        :return: A tuple of the loaded and populated component, the transform_id, the transform_id of its parent, and
        the index of the transform in the parent that it's dependent on
        """
        component_type = ComponentType(json_obj['type'])

        component = Component(component_type=component_type,
                              name=json_obj['name'],
                              description=json_obj['description'])

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

        elif 'pixel_id' in json_obj:
            component.pixel_data = SinglePixelId(json_obj['pixel_id'])

        component.name = json_obj['name']
        component.description = json_obj['description']
        for transform in json_obj['transforms']:
            if transform['type'] == 'rotate':
                component.transforms.append(Rotation(name=transform['name'],
                                                     axis=Vector(transform['axis']['x'],
                                                                 transform['axis']['y'],
                                                                 transform['axis']['z']),
                                                     angle=transform['angle']['value']))
            elif transform['type'] == 'translate':
                component.transforms.append(Translation(name=transform['name'],
                                                        vector=Vector(transform['vector']['x'],
                                                                      transform['vector']['y'],
                                                                      transform['vector']['z'])))

        component.geometry = JsonLoader.build_geometry(json_obj['geometry'])
        transform_id = json_obj['transform_id']
        transform_parent_id = None
        dependent_index = None
        if 'transform_parent_id' in json_obj:
            transform_parent_id = json_obj['transform_parent_id']
            if 'parent_transform_index' in json_obj:
                dependent_index = json_obj['parent_transform_index']
        return component, transform_id, transform_parent_id, dependent_index

    @staticmethod
    def build_geometry(geometry_obj: dict):
        """
        Builds and returns a Geometry instance based on the dictionary describing it

        :param geometry_obj: A dictionary built from json that describes the geometry
        :return: An instance of OFFGeometry or CylindricalGeometry
        """
        if geometry_obj is None:
            return None
        elif geometry_obj['type'] == 'OFF':
            wound_faces = geometry_obj['faces']
            face_indices = geometry_obj['winding_order']
            return OFFGeometry(vertices=[Vector(vertex[0], vertex[1], vertex[2])
                                         for vertex
                                         in geometry_obj['vertices']],
                               faces=NexusDecoder.unwound_off_faces(wound_faces, face_indices))
        elif geometry_obj['type'] == 'Cylinder':
            axis_direction = Vector(geometry_obj['axis_direction']['x'],
                                    geometry_obj['axis_direction']['y'],
                                    geometry_obj['axis_direction']['z'])
            return CylindricalGeometry(axis_direction=axis_direction,
                                       height=geometry_obj['height'],
                                       radius=geometry_obj['radius'])
        else:
            return None
