import h5py
from PySide2.QtCore import QObject, Slot


class HdfWriter(QObject):

    @Slot(str, 'QVariantList')
    def write_pixels(self, filename, pixels):
        print(filename)
        print(len(pixels))
        with h5py.File(filename, 'w') as file:
            pixel_group = file.create_group("pixels")
            for pixel in pixels:
                pixel_group.create_dataset(name=pixel['name'], dtype='i', data=pixel['faces'])


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
