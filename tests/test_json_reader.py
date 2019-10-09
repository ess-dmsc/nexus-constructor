import pytest
import json
from nexus_constructor.nexus_filewriter_json.reader import json_to_nexus


def test_GIVEN_empty_json_string_WHEN_json_to_nexus_called_THEN_error_is_raised():
    with pytest.raises(ValueError):
        json_to_nexus("")


def test_GIVEN_invalid_json_string_WHEN_json_to_nexus_called_THEN_error_is_raised():
    with pytest.raises(ValueError):
        json_to_nexus("{")
