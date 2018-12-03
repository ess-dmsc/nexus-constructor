import h5py
from pprint import pprint
from geometry_constructor.data_model import ComponentType, PixelGrid, PixelMapping, CountDirection, Corner, \
    Geometry, OFFGeometry, CylindricalGeometry, Component, Rotation, Translation
from geometry_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import QObject, QUrl, Slot


class HdfWriter(QObject):
    """
    Stores InstrumentModel data in nexus compliant hdf5 files
    """

    @Slot('QVariant')
    def print_instrument_to_console(self, model: InstrumentModel):
        components = model.components
        print(len(components))
        pprint(components)

    @Slot(QUrl, 'QVariant')
    def save_instrument(self, file_url: QUrl, model: InstrumentModel):
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        print(filename)
        with h5py.File(filename, 'w') as file:
            self.save_instrument_to_file(file, model)

    def save_instrument_to_file(self, file: h5py.File, model: InstrumentModel):
        root = file.create_group('entry')
        root.attrs['NX_class'] = 'NXentry'

        instrument = root.create_group('instrument')
        instrument.attrs['NX_class'] = 'NXinstrument'

        for component in model.components:
            nx_component = instrument.create_group(component.name)
            self.store_transformations(nx_component, component)
            nx_component.attrs['description'] = component.description

            if component.component_type == ComponentType.SAMPLE:
                nx_component.attrs['NX_class'] = 'NXsample'
            elif component.component_type == ComponentType.DETECTOR:
                nx_component.attrs['NX_class'] = 'NXdetector'
                self.store_pixel_data(nx_component, component)

    def store_transformations(self, nx_component: h5py.Group, component: Component):
        if component.transform_parent is None or component.transform_parent == component:
            dependent_on = '.'
        else:
            dependent_on = '.'
            dependent_found = False
            no_dependent = False
            ancestor = component.transform_parent
            while not (dependent_found or no_dependent):
                if len(ancestor.transforms) > 0:
                    dependent_on = '/entry/instrument/{}/{}'.format(ancestor.name,
                                                                    ancestor.transforms[-1].name)
                    dependent_found = True
                elif ancestor.transform_parent is None or ancestor.transform_parent == ancestor:
                    no_dependent = True
                else:
                    ancestor = ancestor.transform_parent

        for i in range(len(component.transforms)):
            transform = component.transforms[i]
            name = transform.name
            if isinstance(transform, Rotation):
                rotate = nx_component.create_dataset(
                    name,
                    data=[transform.angle])
                rotate.attrs['NX_class'] = 'NXtransformations'
                rotate.attrs['depends_on'] = dependent_on
                rotate.attrs['transformation_type'] = 'rotation'
                rotate.attrs['units'] = 'degrees'
                rotate.attrs['vector'] = transform.axis.unit_list
                dependent_on = name
            elif isinstance(transform, Translation):
                magnitude = transform.vector.magnitude
                translate = nx_component.create_dataset(
                    name,
                    data=[magnitude])
                translate.attrs['NX_class'] = 'NXtransformations'
                translate.attrs['depends_on'] = dependent_on
                translate.attrs['transformation_type'] = 'translation'
                translate.attrs['units'] = 'm'
                translate.attrs['vector'] = transform.vector.unit_list if magnitude != 0 else [0, 0, 1]
                dependent_on = name

        nx_component.attrs['depends_on'] = dependent_on

    def store_pixel_data(self, nx_detector: h5py.Group, component: Component):
        pixel_data = component.pixel_data
        # if it's a repeating pixel shape
        if isinstance(pixel_data, PixelGrid):
            self.store_pixel_grid(nx_detector, component.geometry, pixel_data)
        # if it's a mapping
        elif isinstance(pixel_data, PixelMapping):
            self.store_pixel_mapping(nx_detector, component.geometry, pixel_data)

    def store_pixel_grid(self, nx_detector: h5py.Group, geometry: Geometry, pixel_data: PixelGrid):
        if pixel_data is not None:
            pixel_shape = nx_detector.create_group('pixel_shape')
            self.store_geometry(pixel_shape, geometry)

        nx_detector.create_dataset(
            'x_pixel_offset',
            data=[[x * pixel_data.col_width for x in range(pixel_data.columns)]] * pixel_data.rows)

        nx_detector.create_dataset(
            'y_pixel_offset',
            data=[[y * pixel_data.row_height] * pixel_data.columns for y in range(pixel_data.rows)])

        nx_detector.create_dataset(
            'z_pixel_offset',
            data=[[0] * pixel_data.columns] * pixel_data.rows)

        detector_numbers = nx_detector.create_dataset(
            'detector_number',
            shape=(pixel_data.rows, pixel_data.columns),
            dtype='i')
        for id_offset in range(pixel_data.rows * pixel_data.columns):
            # Determine a coordinate for the id based on the count direction from (0,0)
            if pixel_data.count_direction == CountDirection.ROW:
                col = id_offset % pixel_data.columns
                row = id_offset // pixel_data.columns
            else:
                col = id_offset // pixel_data.rows
                row = id_offset % pixel_data.rows
            # Invert axes needed if starting in a different corner
            if pixel_data.initial_count_corner in (Corner.TOP_LEFT, Corner.TOP_RIGHT):
                row = pixel_data.rows - (1 + row)
            if pixel_data.initial_count_corner in (Corner.TOP_RIGHT, Corner.BOTTOM_RIGHT):
                col = pixel_data.columns - (1 + col)
            # Set the id at the calculated coordinate
            detector_numbers[row, col] = pixel_data.first_id + id_offset

    def store_pixel_mapping(self, nx_detector: h5py.Group, geometry: Geometry, pixel_data: PixelMapping):
        if pixel_data is not None:
            detector_shape = nx_detector.create_group('detector_shape')
            self.store_geometry(detector_shape, geometry)
            detector_shape.create_dataset(
                'detector_faces',
                dtype='i',
                data=[[face_id, pixel_data.pixel_ids[face_id]]
                      for face_id
                      in range(len(pixel_data.pixel_ids))
                      if pixel_data.pixel_ids[face_id] is not None])

    def store_geometry(self, nx_group: h5py.Group, geometry: Geometry):
        if isinstance(geometry, OFFGeometry):
            self.store_off_geometry(nx_group, geometry)
        elif isinstance(geometry, CylindricalGeometry):
            self.store_cylindrical_geometry(nx_group, geometry)

    def store_off_geometry(self, nx_group: h5py.Group, geometry: OFFGeometry):
        nx_group.attrs['NX_class'] = 'NXoff_geometry'
        nx_group.create_dataset(
            'vertices',
            data=[vector.xyz_list for vector in geometry.vertices])
        nx_group.create_dataset(
            'winding_order',
            dtype='i',
            data=geometry.winding_order)
        nx_group.create_dataset(
            'faces',
            dtype='i',
            data=geometry.winding_order_indices)

    def store_cylindrical_geometry(self, nx_group: h5py.Group, geometry: CylindricalGeometry):
        nx_group.attrs['NX_class'] = 'NXcylindrical_geometry'

        nx_group.create_dataset(
            'vertices',
            data=[geometry.base_center_point.xyz_list,
                  geometry.base_edge_point.xyz_list,
                  geometry.top_center_point.xyz_list])
        nx_group.create_dataset(
            'cylinders',
            dtype='i',
            data=[0, 1, 2])


class Logger(QObject):
    """
    Provides methods to prints strings, lists and objects to console from QML.

    While QML has console.log support through its javascript, it does not work in all terminal environments.
    """

    @Slot(str)
    def log(self, message):
        print(message)

    @Slot('QVariantList')
    def log_list(self, message):
        print(message)

    @Slot('QVariant')
    def log_object(self, message):
        print(message)
