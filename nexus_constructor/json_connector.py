from PySide2.QtCore import QObject, QUrl, Slot
from PySide2.QtGui import QGuiApplication
from nexus_constructor.qml_models.instrument_model import InstrumentModel
from nexus_constructor.nexus_filewriter_json import writer as nf_writer
import json


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
        self.clipboard = QGuiApplication.clipboard()

        with open("Instrument.schema.json") as file:
            self.schema = json.load(file)

    @Slot(QUrl, "QVariant")
    def save_to_filewriter_json(self, file_url: QUrl, model: InstrumentModel):
        json_string = nf_writer.generate_json(model)
        self.save_to_file(json_string, file_url)

    @staticmethod
    def save_to_file(data: str, file_url: QUrl):
        filename = file_url.toString(
            options=QUrl.FormattingOptions(QUrl.PreferLocalFile)
        )
        with open(filename, "w") as file:
            file.write(data)

    @Slot("QVariant")
    def copy_nexus_filewriter_json_to_clipboard(self, model: InstrumentModel):
        self.clipboard.setText(nf_writer.generate_json(model))

    @Slot("QVariant")
    def request_filewriter_json(self, model: InstrumentModel):
        self.requested_filewriter_json.emit(nf_writer.generate_json(model))
