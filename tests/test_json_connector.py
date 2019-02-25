from nexus_constructor.json_connector import JsonConnector
from nexus_constructor.qml_models.instrument_model import InstrumentModel as model
import nexus_constructor.nexus_constructor_json as gc_json
import nexus_constructor.nexus_filewriter_json as nf_json
import pyperclip


def test_valid_json_returns_true():

    json_connector = JsonConnector()

    # Simple JSON string representing a single point. This should be a valid file.
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

    # JSON string minus the "components" field. This should be an invalid file.
    invalid_json = (r'{'
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

    assert not json_connector.json_string_to_instrument_model(invalid_json, model())

    # JSON string with no information. This should be an invalid file.
    empty_json = ''
    assert not json_connector.json_string_to_instrument_model(empty_json, model())


def copy_nexus_filewriter_json_to_clipboard():

    json_connector = JsonConnector()

    # Simple JSON string representing a single point. This should be a valid file.
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

    json_connector.json_string_to_instrument_model(valid_json, model())
    json_connector.copy_nexus_filewriter_json_to_clipboard(model())

    assert pyperclip.paste() == nf_json.generate_json(model())


def test_copy_nexus_constructor_json_to_clipboard():

    json_connector = JsonConnector()

    # Simple JSON string representing a single point. This should be a valid file.
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

    json_connector.json_string_to_instrument_model(valid_json, model())
    json_connector.copy_nexus_constructor_json_to_clipboard(model())

    assert pyperclip.paste() == gc_json.generate_json(model())
