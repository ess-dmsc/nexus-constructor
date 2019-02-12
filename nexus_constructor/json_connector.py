from PySide2.QtCore import QObject, QUrl, Slot, Signal
from nexus_constructor.qml_models.instrument_model import InstrumentModel
import nexus_constructor.nexus_constructor_json as gc_json
import nexus_constructor.nexus_filewriter_json as nf_json
import json
import jsonschema


class JsonConnector(QObject):
    """
    Exposes the json parsers to be callable via QML

    Data can be saved to filewriter or nexus constructor json with the following methods:
    - save_to_filewriter_json
    - save_to_nexus_constructor_json

    And can be loaded from a file containing either format using
    - load_file_into_instrument_model

    Slots and signals also exist to allow the json to be generated on the fly and propagated to other sources:
    Calls to:
    - request_nexus_constructor_json
    - request_filewriter_json
    Will generate the json in the requested format, and send it in the relevant signal:
    - requested_nexus_constructor_json
    - requested_filewriter_json
    """

    def __init__(self):
        super().__init__()

        with open('Instrument.schema.json') as file:
            self.schema = json.load(file)

    @Slot(QUrl, 'QVariant', result=bool)
    def load_file_into_instrument_model(self, file_url: QUrl, model: InstrumentModel):
        filename = file_url.toString(options=QUrl.FormattingOptions(QUrl.PreferLocalFile))
        with open(filename, 'r') as file:
            json_string = file.read()

        return self.json_string_to_instrument_model(json_string, model)

    def json_string_to_instrument_model(self, json_string, model: InstrumentModel):

        try:
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return False

        nexus_constructor_json = True
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.exceptions.ValidationError:
            nexus_constructor_json = False

        try:
            if nexus_constructor_json:
                gc_json.load_json_object_into_instrument_model(data, model)
            else:
                nf_json.load_json_object_into_instrument_model(data, model)
        except KeyError:
            return False

        return True

    @Slot(QUrl, 'QVariant')
    def save_to_filewriter_json(self, file_url: QUrl, model: InstrumentModel):
        json_string = nf_json.generate_json(model)
        self.save_to_file(json_string, file_url)

    @Slot(QUrl, 'QVariant')
    def save_to_nexus_constructor_json(self, file_url: QUrl, model: InstrumentModel):
        json_string = gc_json.generate_json(model)
        self.save_to_file(json_string, file_url)

    @staticmethod
    def save_to_file(data: str, file_url: QUrl):
        filename = file_url.toString()
        with open(filename, 'w') as file:
            file.write(data)

    requested_nexus_constructor_json = Signal(str)

    @Slot('QVariant')
    def request_nexus_constructor_json(self, model: InstrumentModel):
        self.requested_nexus_constructor_json.emit(gc_json.generate_json(model))

    requested_filewriter_json = Signal(str)

    @Slot('QVariant')
    def request_filewriter_json(self, model: InstrumentModel):
        self.requested_filewriter_json.emit(nf_json.generate_json(model))
