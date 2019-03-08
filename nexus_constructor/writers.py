import h5py
from pprint import pprint
from nexus_constructor.data_model import (
    PixelGrid,
    PixelMapping,
    SinglePixelId,
    Geometry,
    OFFGeometry,
    CylindricalGeometry,
    Component,
    Rotation,
    Translation,
)
from nexus_constructor.nexus import NexusEncoder
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from PySide2.QtCore import QObject, QUrl, Slot


class HdfWriter(QObject):
    """
    Stores InstrumentModel data in nexus compliant hdf5 files
    """

    @Slot("QVariant")
    def print_instrument_to_console(self, model: InstrumentModel):
        components = model.components
        print(len(components))
        pprint(components)

    @Slot(QUrl, "QVariant")
    def save_instrument(self, file_url: QUrl, model: InstrumentModel):
        filename = file_url.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        print(filename)
        with h5py.File(filename, "w") as file:
            self.save_instrument_to_file(file, model)

    def save_instrument_to_file(self, file: h5py.File, model: InstrumentModel):
        root = file.create_group("entry")
        root.attrs["NX_class"] = "NXentry"

        instrument = root.create_group("instrument")
        instrument.attrs["NX_class"] = "NXinstrument"

        external_types = NexusEncoder.external_component_types()
        for component in model.components:
            if component.component_type in external_types:
                self.store_component(root, component)
            else:
                self.store_component(instrument, component)

    def store_component(self, parent_group: h5py.Group, component: Component):
        nx_component = parent_group.create_group(component.name)
        nx_component.attrs["description"] = component.description
        nx_component.attrs["NX_class"] = NexusEncoder.component_class_name(
            component.component_type
        )
        self.store_transformations(nx_component, component)
        self.store_pixel_data(nx_component, component)

    def store_transformations(self, nx_component: h5py.Group, component: Component):
        dependent_on = NexusEncoder.ancestral_dependent_transform(component)

        if len(component.transforms) > 0:
            nx_transforms = nx_component.create_group("transforms")
            nx_transforms.attrs["NX_class"] = "NXtransformations"

            for i in range(len(component.transforms)):
                transform = component.transforms[i]
                name = transform.name
                if isinstance(transform, Rotation):
                    rotate = nx_transforms.create_dataset(name, data=[transform.angle])
                    rotate.attrs["depends_on"] = dependent_on
                    rotate.attrs["transformation_type"] = "rotation"
                    rotate.attrs["units"] = "degrees"
                    rotate.attrs["vector"] = transform.axis.unit_list
                elif isinstance(transform, Translation):
                    magnitude = transform.vector.magnitude
                    translate = nx_transforms.create_dataset(name, data=[magnitude])
                    translate.attrs["depends_on"] = dependent_on
                    translate.attrs["transformation_type"] = "translation"
                    translate.attrs["units"] = "m"
                    translate.attrs["vector"] = (
                        transform.vector.unit_list if magnitude != 0 else [0, 0, 1]
                    )
                else:
                    continue
                dependent_on = NexusEncoder.absolute_transform_path_name(
                    transform,
                    component,
                    component.component_type
                    not in NexusEncoder.external_component_types(),
                )

        nx_component.attrs["depends_on"] = dependent_on

    def store_pixel_data(self, nx_component: h5py.Group, component: Component):
        pixel_data = component.pixel_data
        geometry_group_name = NexusEncoder.geometry_group_name(component)
        # if it's a repeating pixel shape
        if isinstance(pixel_data, PixelGrid):
            self.store_pixel_grid(
                nx_component, component.geometry, geometry_group_name, pixel_data
            )
        # if it's a mapping
        elif isinstance(pixel_data, PixelMapping):
            self.store_pixel_mapping(
                nx_component, component.geometry, geometry_group_name, pixel_data
            )
        # if it's got a single pixel id
        elif isinstance(pixel_data, SinglePixelId):
            self.store_monitor_detector_id(nx_component, component.geometry, pixel_data)
        else:
            geometry_group = nx_component.create_group(geometry_group_name)
            self.store_geometry(geometry_group, component.geometry)

    def store_pixel_grid(
        self,
        nx_detector: h5py.Group,
        geometry: Geometry,
        geometry_group_name: str,
        pixel_data: PixelGrid,
    ):
        if pixel_data is not None:
            pixel_shape = nx_detector.create_group(geometry_group_name)
            self.store_geometry(pixel_shape, geometry)

        nx_detector.create_dataset(
            "x_pixel_offset", data=NexusEncoder.pixel_grid_x_offsets(pixel_data)
        )

        nx_detector.create_dataset(
            "y_pixel_offset", data=NexusEncoder.pixel_grid_y_offsets(pixel_data)
        )

        nx_detector.create_dataset(
            "z_pixel_offset", data=NexusEncoder.pixel_grid_z_offsets(pixel_data)
        )

        nx_detector.create_dataset(
            "detector_number",
            shape=(pixel_data.rows, pixel_data.columns),
            dtype="i",
            data=NexusEncoder.pixel_grid_detector_ids(pixel_data),
        )

    def store_pixel_mapping(
        self,
        nx_detector: h5py.Group,
        geometry: Geometry,
        geometry_group_name: str,
        pixel_data: PixelMapping,
    ):
        if pixel_data is not None:
            detector_shape = nx_detector.create_group(geometry_group_name)
            self.store_geometry(detector_shape, geometry)
            detector_shape.create_dataset(
                "detector_faces", dtype="i", data=NexusEncoder.pixel_mapping(pixel_data)
            )

    def store_monitor_detector_id(
        self,
        nx_monitor: h5py.Group,
        geometry: Geometry,
        geometry_group_name: str,
        pixel_data: SinglePixelId,
    ):
        component_shape = nx_monitor.create_group(geometry_group_name)
        self.store_geometry(component_shape, geometry)
        # TODO: Replace this Mantid compatibility dataset, with the nexus standard's way (once it exists)
        component_shape.create_dataset(
            "detector_id", dtype="i", data=[pixel_data.pixel_id]
        )

    def store_geometry(self, nx_group: h5py.Group, geometry: Geometry):
        if isinstance(geometry, OFFGeometry):
            self.store_off_geometry(nx_group, geometry)
        elif isinstance(geometry, CylindricalGeometry):
            self.store_cylindrical_geometry(nx_group, geometry)

    def store_off_geometry(self, nx_group: h5py.Group, geometry: OFFGeometry):
        nx_group.attrs["NX_class"] = "NXoff_geometry"
        nx_group.create_dataset(
            "vertices", data=[vector.vector.tolist() for vector in geometry.vertices]
        )
        nx_group.create_dataset("winding_order", dtype="i", data=geometry.winding_order)
        nx_group.create_dataset("faces", dtype="i", data=geometry.winding_order_indices)

    def store_cylindrical_geometry(
        self, nx_group: h5py.Group, geometry: CylindricalGeometry
    ):
        nx_group.attrs["NX_class"] = "NXcylindrical_geometry"

        nx_group.create_dataset(
            "vertices",
            data=[
                geometry.base_center_point.toTuple(),
                geometry.base_edge_point.toTuple(),
                geometry.top_center_point.toTuple(),
            ],
        )
        nx_group.create_dataset("cylinders", dtype="i", data=[0, 1, 2])


class Logger(QObject):
    """
    Provides methods to prints strings, lists and objects to console from QML.

    While QML has console.log support through its javascript, it does not work in all terminal environments.
    """

    @Slot(str)
    def log(self, message):
        print(message)

    @Slot("QVariantList")
    def log_list(self, message):
        print(message)

    @Slot("QVariant")
    def log_object(self, message):
        print(message)
