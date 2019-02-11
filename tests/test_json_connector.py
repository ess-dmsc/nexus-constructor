from nexus_constructor.json_connector import JsonConnector
from nexus_constructor.qml_models.instrument_model import InstrumentModel as model
import json
import pytest


def test_good_json_returns_true():

    with open("tests/sample.json", mode="r") as file:
        json_string = file.read()

    json_connector = JsonConnector()

    assert json_connector.json_string_to_instrument_model(json_string, model())
