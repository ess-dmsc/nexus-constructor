import h5py
from geometry_constructor.DataModel import PixelModel
from PySide2.QtCore import QObject, Slot


class HdfWriter(QObject):

    @Slot(str, 'QVariant')
    def write_pixels(self, filename, model: PixelModel):
        print(filename)
        pixels = model.my_list
        print(len(pixels))
        print(pixels)
        with h5py.File(filename, 'w') as file:
            pixel_group = file.create_group("pixels")
            for pixel in pixels:
                pixel_group.create_dataset(name=pixel.name, dtype='i', data=pixel.faces)


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
