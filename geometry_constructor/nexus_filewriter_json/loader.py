"""
Functions to load nexus filewriter json data into an InstrumentModel

This module contains all the parsing functions used to load the data.
It is recommended that instead of importing this module, the root of the package be imported instead, as this exposes
only the required root function to load the json

Json format description can be found at https://github.com/ess-dmsc/kafka-to-nexus/
"""
from geometry_constructor.data_model import Component, ComponentType, Rotation, Translation, Vector, OFFGeometry,\
    CylindricalGeometry, SinglePixelId
from geometry_constructor.nexus import NexusEncoder, NexusDecoder
from geometry_constructor.qml_models.instrument_model import InstrumentModel


def load_json_object_into_instrument_model(json_data: dict, model: InstrumentModel):
    """
    Loads an object representation of filewriter json into an InstrumentModel

    :param json_data: Dictionary containing the json data to load
    :param model: The model the loaded components will be stored in
    """
    nx_instrument = None
    nx_sample = None
    for child in json_data['nexus_structure']['children']:
        if has_nx_class(child):
            if child['attributes']['NX_class'] == 'NXinstrument':
                nx_instrument = child
            elif child['attributes']['NX_class'] == 'NXsample':
                nx_sample = child

    components = []
    if nx_sample is None:
        sample = Component(
            component_type=ComponentType.SAMPLE,
            name='Sample'
        )
    else:
        sample, _, _ = generate_component(nx_sample)
    components.append(sample)

    component_classes = [NexusEncoder.component_class_name(component_type)
                         for component_type in ComponentType
                         if component_type != ComponentType.SAMPLE]

    parent_names = [None]
    dependent_transform_names = [None]
    named_components = {
        sample.name: sample
    }

    for child in nx_instrument['children']:
        if has_nx_class(child) and child['attributes']['NX_class'] in component_classes:
            component, parent_name, dependent_transform_name = generate_component(child)
            components.append(component)
            parent_names.append(parent_name)
            dependent_transform_names.append(dependent_transform_name)
            named_components[component.name] = component

    # assign parent components and transforms
    for i in range(len(components)):
        component = components[i]
        parent_name = parent_names[i]
        dependent_transform_name = dependent_transform_names[i]

        if parent_name is not None:
            parent = named_components[parent_name]
            component.transform_parent = parent
            if dependent_transform_name is not None:
                for candidate_transform in parent.transforms:
                    if candidate_transform.name == dependent_transform_name:
                        component.dependent_transform = candidate_transform

    model.replace_contents(components)


def has_nx_class(json_object: dict):
    """Returns whether a json object has a nexus class"""
    return 'attributes' in json_object and 'NX_class' in json_object['attributes']


def generate_component(json_component: dict):
    """
    Builds a Component instance using data from the json object that describes it

    :param json_component: The json object describing the component
    :return: A tuple of the component, the name of its transform parent, and the name of the transform in its parent
    that it's dependent on
    """
    name = json_component['name']
    component_type = NexusDecoder.component_type_from_classname(json_component['attributes']['NX_class'])
    description = json_component['attributes']['description']
    geometry, pixel_data = generate_geometry_and_pixel_data(json_component)

    transforms, dependent_on = generate_transforms(json_component)

    parent_name, dependent_transform_name = NexusDecoder.extract_dependency_names(dependent_on)

    component = Component(
        component_type=component_type,
        name=name,
        description=description,
        transforms=transforms,
        geometry=geometry,
        pixel_data=pixel_data,
    )
    return component, parent_name, dependent_transform_name


def generate_geometry_and_pixel_data(json_component: dict):
    """
    Builds Geometry and PixelData instances populated with data from the given component's json object

    :param json_component: The json object describing the component whose geometry and pixel data is being extracted
    :return: A tuple of the components Geometry and PixelData objects
    """
    geometry = None
    pixel_data = None

    x_offsets = None
    y_offsets = None
    z_offsets = None
    detector_numbers = None

    for child in json_component['children']:
        if child['name'] == 'geometry':
            geometry = None
            if not has_nx_class(child):
                continue
            if child['attributes']['NX_class'] == 'NXcylindrical_geometry':
                vectors = []
                cylinders = []
                for subchild in child['children']:
                    if subchild['name'] == 'vertices':
                        for vertex in subchild['values']:
                            vectors.append(Vector(vertex[0], vertex[1], vertex[2]))
                    elif subchild['name'] == 'cylinders':
                        cylinders = subchild['values']
                assert len(cylinders) == 1, "Cylindrical geometry only supports one cylinder"
                base_center = vectors[cylinders[0][0]]
                base_edge = vectors[cylinders[0][1]]
                top_center = vectors[cylinders[0][2]]
                assert base_center.xyz_list == [0, 0, 0], "Cylindrical geometry requires a center at its origin"
                radius = base_edge.magnitude
                height = top_center.magnitude

                geometry = CylindricalGeometry(axis_direction=top_center, radius=radius, height=height)
            elif child['attributes']['NX_class'] == 'NXoff_geometry':
                vertices = None
                winding_order = None
                winding_order_indexes = None
                detector_ids = None
                for subchild in child['children']:
                    if subchild['name'] == 'vertices':
                        vertices = []
                        for vertex in subchild['values']:
                            vertices.append(
                                Vector(vertex[0], vertex[1], vertex[2])
                            )
                    elif subchild['name'] == 'winding_order':
                        winding_order = subchild['values']
                    elif subchild['name'] == 'faces':
                        winding_order_indexes = subchild['values']
                    elif subchild['name'] == 'detector_faces':
                        detector_ids = subchild['values']
                assert vertices is not None, "OFF geometry had no vertices dataset"
                assert winding_order is not None, "OFF geometry had no winding_order dataset"
                assert winding_order_indexes is not None, "OFF geometry had no faces dataset"
                geometry = OFFGeometry(
                    vertices=vertices,
                    faces=NexusDecoder.unwound_off_faces(winding_order, winding_order_indexes)
                )
                if detector_ids is not None:
                    pixel_data = NexusDecoder.unmap_pixel_ids(detector_ids, len(winding_order_indexes))

        elif child['name'] == 'x_pixel_offset':
            x_offsets = child['values']
        elif child['name'] == 'y_pixel_offset':
            y_offsets = child['values']
        elif child['name'] == 'z_pixel_offset':
            z_offsets = child['values']
        elif child['name'] == 'detector_number':
            detector_numbers = child['values']
        elif child['name'] == 'detector_id':
            pixel_data = SinglePixelId(child['values'])

    if x_offsets is not None and y_offsets is not None and z_offsets is not None and detector_numbers is not None:
        pixel_data = NexusDecoder.build_pixel_grid(x_offsets, y_offsets, z_offsets, detector_numbers)

    return geometry, pixel_data


def generate_transforms(json_component: dict):
    """
    Builds a list of transforms that belong to the given component

    :param json_component: The json object describing the component whose transforms are being extracted
    :return: A tuple of the list of transforms, and the string of the path to the component's dependent transform
    """
    transforms = []
    dependencies = {}

    for child in json_component['children']:
        if has_nx_class(child) and child['attributes']['NX_class'] == 'NXtransformations':
            name = child['name']
            if child['attributes']['transformation_type'] == 'rotation':
                angle = child['values']
                x = child['attributes']['vector'][0]
                y = child['attributes']['vector'][1]
                z = child['attributes']['vector'][2]
                transform = Rotation(
                    axis=Vector(x, y, z),
                    angle=angle,
                    name=name
                )
            elif child['attributes']['transformation_type'] == 'translation':
                magnitude = child['values']
                x = child['attributes']['vector'][0] * magnitude
                y = child['attributes']['vector'][1] * magnitude
                z = child['attributes']['vector'][2] * magnitude
                transform = Translation(
                    vector=Vector(x, y, z),
                    name=name
                )
            else:
                continue
            transforms.append(transform)
            dependencies[name] = child['attributes']['depends_on']

    dependent_on = json_component['attributes']['depends_on']
    while dependent_on in dependencies:
        dependent_on = dependencies[dependent_on]

    return transforms, dependent_on
