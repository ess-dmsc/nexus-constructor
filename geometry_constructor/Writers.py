import h5py
import pprint
from geometry_constructor.Models import InstrumentModel
from PySide2.QtCore import QObject, Slot


class HdfWriter(QObject):

    @Slot(str, 'QVariant')
    def write_instrument(self, filename, model: InstrumentModel):
        print(filename)
        components = model.components
        print(len(components))
        pprint.pprint(components)


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
