from nexus_constructor.json_connector import JsonConnector
from nexus_constructor.qml_models.instrument_model import InstrumentModel as model


def test_valid_json_returns_true():

    json_connector = JsonConnector()

    with open("tests/sample.json", mode="r") as file:
        json_string = file.read()

    assert json_connector.json_string_to_instrument_model(json_string, model())


def test_invalid_jsons_returns_false():

    json_connector = JsonConnector()

    with open("tests/wrongformat.json", mode="r") as file:
        json_string = file.read()

    assert not json_connector.json_string_to_instrument_model(json_string, model())

    empty_json = ""
    assert not json_connector.json_string_to_instrument_model(empty_json, model())
