from nexus_constructor.json_connector import JsonConnector
from nexus_constructor.qml_models.instrument_model import InstrumentModel as model


def test_valid_json_returns_true():

    json_connector = JsonConnector()

    valid_json = (r'{'
                  r'"components": [],'
                  r'"sample": {'
                  r'"geometry": {'
                  r'"type": "OFF",'
                  r'"vertices": ['
                  r'[-0.5, -0.5, 0.5]'
                  r']'
                  r'},'
                  r'"type": "Sample"'
                  r'}'
                  r'}')

    assert json_connector.json_string_to_instrument_model(valid_json, model())


def test_invalid_jsons_returns_false():

    json_connector = JsonConnector()

    with open("tests/wrongformat.json", mode="r") as file:
        json_string = file.read()

    assert not json_connector.json_string_to_instrument_model(json_string, model())

    empty_json = ""
    assert not json_connector.json_string_to_instrument_model(empty_json, model())
