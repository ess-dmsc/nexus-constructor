from PySide2.QtCore import QObject, QUrl, Slot, Signal
from geometry_constructor.qml_models.instrument_model import InstrumentModel
from geometry_constructor.geometry_constructor_json.loader import JsonLoader as GCJsonLoader
from geometry_constructor.geometry_constructor_json.writer import JsonWriter as GCJsonWriter
from geometry_constructor.nexus_filewriter_json.loader import Loader as NexusJsonLoader
from geometry_constructor.nexus_filewriter_json.writer import Writer as NexusJsonWriter
import json
import jsonschema


class JsonConnector(QObject):

    def __init__(self):
        super().__init__()

        with open('Instrument.schema.json') as file:
            self.schema = json.load(file)

    @Slot(QUrl, 'QVariant')
    def load_file_into_instrument_model(self, file_url: QUrl, model: InstrumentModel):
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        with open(filename, 'r') as file:
            json_string = file.read()
        data = json.loads(json_string)

        geometry_constructor_json = True
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.exceptions.ValidationError:
            geometry_constructor_json = False

        if geometry_constructor_json:
            GCJsonLoader.load_json_object_into_instrument_model(data, model)
        else:
            NexusJsonLoader.load_json_into_instrument_model(data, model)

    @Slot(QUrl, 'QVariant')
    def save_to_filewriter_json(self, file_url: QUrl, model: InstrumentModel):
        json_string = NexusJsonWriter.generate_json(model)
        self.save_to_file(json_string, file_url)

    @Slot(QUrl, 'QVariant')
    def save_to_geometry_constructor_json(self, file_url: QUrl, model: InstrumentModel):
        json_string = GCJsonWriter.generate_json(model)
        self.save_to_file(json_string, file_url)

    @staticmethod
    def save_to_file(data: str, file_url: QUrl):
        filename = file_url.toString(options=QUrl.PreferLocalFile)
        with open(filename, 'w') as file:
            file.write(data)

    requested_geometry_constructor_json = Signal(str)

    @Slot('QVariant')
    def request_geometry_constructor_json(self, model: InstrumentModel):
        self.requested_geometry_constructor_json.emit(GCJsonWriter.generate_json(model))

    requested_filewriter_json = Signal(str)

    @Slot('QVariant')
    def request_filewriter_json(self, model: InstrumentModel):
        self.request_filewriter_json.emit(NexusJsonWriter.generate_json(model))
