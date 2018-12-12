"""
Package for loading and creating json representations of an InstrumentModel that can be used by the ESS DMSC's nexus
filewriter https://github.com/ess-dmsc/kafka-to-nexus/

Note that due to format differences, saving and re-loading nexus json isn't entirely lossless.
Conversion can introduce floating point errors into cylindrical geometry and transform axes, and components without an
explicitly defined dependent transform in their transform parent will have one assigned when saving.
"""

from . import loader, writer
from geometry_constructor.qml_models.instrument_model import InstrumentModel


def generate_json(model: InstrumentModel):
    """
    Builds a json string representing the given instrument model

    The json conforms to the nexus filewriter format
    :param model: The instrument to build a representation of
    :return: A string containing formatted json
    """
    return writer.generate_json(model)


def load_json_object_into_instrument_model(json_object: dict, model: InstrumentModel):
    """
    Loads an object representation of Geometry Constructor json into a given instrument model

    The object representation should be a dictionary, built by pythons json package load functions, and conform to the
    nexus filewriter format
    :param json_object: The dictionary of objects built from a json source
    :param model: The model to populate with the json data
    """
    return loader.load_json_object_into_instrument_model(json_object, model)
