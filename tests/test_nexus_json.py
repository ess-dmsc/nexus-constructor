from geometry_constructor.nexus_filewriter_json.loader import Loader
from geometry_constructor.nexus_filewriter_json.writer import Writer
from geometry_constructor.qml_models.instrument_model import InstrumentModel
from tests.test_json import build_sample_model
import json
from numbers import Number
from pytest import approx


def test_nexus_json_generation_and_loading_is_consistent():
    """
    The process of going from data_model classes to FileWriter/NeXus format is slightly lossy
    For instance, data_model can work with no selected transform in the parent, but FileWriter requires it explicitly.
    Certain properties also require floating point calculations to be performed, resulting in some slight variation.

    This builds a sample instrument, and saves it to json.
    That json is then loaded, saved again, and the initial json compared to this new json.
    If the object representations of the json's are identical, save for floating point inaccuracies, this passes
    """

    instrument_model = build_sample_model()

    json_string = Writer.generate_json(instrument_model)

    loader_model = InstrumentModel()
    Loader.load_json_into_instrument_model(json.loads(json_string), loader_model)

    loaded_json = Writer.generate_json(loader_model)

    assert are_objects_equivalent(json.loads(json_string), json.loads(loaded_json))


def are_objects_equivalent(obj1, obj2):
    """Test if two objects are equivalent to eachother, with approximate equality for any numeric properties"""
    type1 = type(obj1)
    type2 = type(obj2)
    if type1 != type2:
        return False
    else:
        if type1 == list:
            return are_lists_equivalent(obj1, obj2)
        elif type1 == dict:
            return are_dicts_equivalent(obj1, obj2)
        else:
            return are_values_equivalent(obj1, obj2)


def are_lists_equivalent(list1: list, list2: list):
    """Test if two lists are equivalent to eachother, with approximate equality for any numeric items"""
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if not are_objects_equivalent(list1[i], list2[i]):
            return False
    return True


def are_dicts_equivalent(dict1: dict, dict2: dict):
    """Test if two dictionaries are equivalent to eachother, with approximate equality for any numeric values"""
    if dict1.keys() != dict2.keys():
        return False
    for key in dict1.keys():
        if not are_objects_equivalent(dict1[key], dict2[key]):
            return False
    return True


def are_values_equivalent(val1, val2):
    """Test if two values are equivalent to eachother, with approximate equality if they're numeric"""
    if isinstance(val1, Number):
        return val1 == approx(val2)
    else:
        return val1 == val2
