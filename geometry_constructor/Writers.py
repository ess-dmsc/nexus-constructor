import h5py
from pprint import pprint
from geometry_constructor.Models import InstrumentModel, Sample, Detector, PixelGrid, PixelMapping, CountDirection,\
    Corner, Geometry, OFFGeometry, CylindricalGeometry
from PySide2.QtCore import QObject, Slot


class HdfWriter(QObject):

    @Slot('QVariant')
    def write_instrument(self, model: InstrumentModel):
        components = model.components
        print(len(components))
        pprint(components)

    @Slot(str, 'QVariant')
    def save_instrument(self, filename, model: InstrumentModel):
        with h5py.File(filename, 'w') as file:
            root = file.create_group('entry')
            root.attrs['NX_class'] = 'NXentry'

            instrument = root.create_group('instrument')
            instrument.attrs['NX_class'] = 'NXinstrument'

            for component in model.components:
                nx_component = instrument.create_group(component.name)

                if isinstance(component, Sample):
                    nx_component.attrs['NX_class'] = 'NXsample'
                elif isinstance(component, Detector):
                    nx_component.attrs['NX_class'] = 'NXdetector'
                    pixel_data = component.pixel_data

                    # if it's a repeating pixel shape
                    if isinstance(pixel_data, PixelGrid):
                        pixel_shape = nx_component.create_group('pixel_shape')
                        self.store_geometry(pixel_shape, component.geometry)

                        nx_component.create_dataset(
                            'x_pixel_offset',
                            data=[[x * pixel_data.col_width for x in range(pixel_data.columns)]] * pixel_data.rows)

                        nx_component.create_dataset(
                            'y_pixel_offset',
                            data=[[y * pixel_data.row_height] * pixel_data.columns for y in range(pixel_data.rows)])

                        nx_component.create_dataset(
                            'z_pixel_offset',
                            data=[[0] * pixel_data.columns] * pixel_data.rows)

                        detector_numbers = nx_component.create_dataset(
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

                    # if it's a mapping
                    elif isinstance(pixel_data, PixelMapping):
                        detector_shape = nx_component.create_group('detector_shape')
                        self.store_geometry(detector_shape, component.geometry)
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
            data=[[vector.x, vector.y, vector.z] for vector in geometry.vertices])
        nx_group.create_dataset(
            'winding_order',
            dtype='i',
            data=geometry.winding_order)
        nx_group.create_dataset(
            'faces',
            dtype='i',
            data=geometry.faces)

    def store_cylindrical_geometry(self, nx_group: h5py.Group, geometry: CylindricalGeometry):
        nx_group.attrs['NX_class'] = 'NXcylindrical_geometry'
        nx_group.create_dataset(
            'vertices',
            data=[[vector.x, vector.y, vector.z]
                  for vector
                  in [geometry.bottom_center, geometry.bottom_edge, geometry.top_center]])
        nx_group.create_dataset(
            'cylinders',
            dtype='i',
            data=[0, 1, 2])


class Logger(QObject):

    @Slot(str)
    def log(self, message):
        print(message)

    @Slot('QVariantList')
    def log_list(self, message):
        print(message)

    @Slot('QVariant')
    def log_object(self, message):
        print(message)
