import pytest
import json
from nexus_constructor.nexus_filewriter_json.reader import (
    json_to_nexus,
    validate_top_level_fields,
    REQUIRED_FIELDS,
)


def test_GIVEN_empty_json_string_WHEN_json_to_nexus_called_THEN_error_is_raised():
    with pytest.raises(ValueError):
        json_to_nexus("")


def test_GIVEN_json_with_missing_required_fields_WHEN_validated_THEN_message_returned_for_each_missing_field():
    json_input = r"{}"
    json_data = json.loads(json_input)
    messages = validate_top_level_fields(json_data)
    assert len(messages) == len(
        REQUIRED_FIELDS
    ), "Expect same number of warning messages as missing required fields"


def test_GIVEN_json_with_valid_required_fields_WHEN_validated_THEN_no_messages_returned():
    json_input = (
        r"{"
        r'"cmd": "FileWriter_new",'
        r'"broker": "localhost:9092",'
        r'"job_id": "test_job",'
        r'"file_attributes": {"file_name": "test_file.nxs"},'
        r'"nexus_structure": {"children": []}'
        r"}"
    )
    json_data = json.loads(json_input)
    messages = validate_top_level_fields(json_data)
    assert (
        len(messages) == 0
    ), "Expect no messages if all required fields are present and valid"
