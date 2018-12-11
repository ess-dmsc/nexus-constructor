from . import loader, writer
from geometry_constructor.qml_models.instrument_model import InstrumentModel


def generate_json(model: InstrumentModel):
    return writer.generate_json(model)


def load_json_object_into_instrument_model(json_object: dict, model: InstrumentModel):
    return loader.load_json_object_into_instrument_model(json_object, model)
