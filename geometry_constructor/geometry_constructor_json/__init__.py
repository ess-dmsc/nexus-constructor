"""
Package for loading and creating json representations of an InstrumentModel that conform to the Geometry Constructor's
Instrument json schema
"""
from . import writer, loader
from geometry_constructor.qml_models.instrument_model import InstrumentModel


def generate_json(model: InstrumentModel):
    """
    Builds a json string representing the given instrument model

    The json conforms to the Geometry Constructors Instrument json schema
    :param model: The instrument to build a representation of
    :return: A string containing formatted json
    """
    return writer.generate_json(model)


def load_json_object_into_instrument_model(json_object: dict, model: InstrumentModel):
    """
    Loads an object representation of Geometry Constructor json into a given instrument model

    The object representation should be a dictionary, built by pythons json package load functions, and conform to the
    Geometry Constructors Instrument json schema
    :param json_object: The dictionary of objects built from a json source
    :param model: The model to populate with the json data
    """
    loader.load_json_object_into_instrument_model(json_object, model)
