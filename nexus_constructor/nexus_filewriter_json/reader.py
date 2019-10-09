import json
from typing import Tuple, List, Union

from nexus_constructor.nexus.nexus_wrapper import NexusWrapper

"""
Read the JSON, perform some validation and construct an in-memory NeXus file from the nexus_structure field
"""


def _validate_broker(broker: Union[str, object]):
    pass


def _validate_job_id(job_id: Union[str, object]):
    pass


def _validate_file_attributes(file_attributes: Union[str, object]):
    pass


def _validate_nexus_structure(nexus_structure: Union[str, object]):
    pass


def _validate_command(command: Union[str, object]):
    allowed_commands = {"FileWriter_new"}
    if command not in allowed_commands:
        return '"cmd" field contains invalid string'


REQUIRED_FIELDS = {
    "cmd": _validate_command,
    "broker": _validate_broker,
    "job_id": _validate_job_id,
    "file_attributes": _validate_file_attributes,
    "nexus_structure": _validate_nexus_structure,
}


def validate_top_level_fields(json_data: dict) -> List[str]:
    """
    Checks required fields are present in the json and returns warning if not
    :param json_data:
    :return: A list of warning messages created during validation
    """
    warning_messages = []

    for required_field, validator in REQUIRED_FIELDS.items():
        try:
            field_value = json_data[required_field]
        except KeyError:
            warning_messages.append(f'Required field "{required_field}" is missing')
        else:
            message = validator(field_value)
            if message is not None:
                warning_messages.append(message)

    return warning_messages


def json_to_nexus(json_input: str) -> Tuple[NexusWrapper, List[str]]:
    """
    Convert JSON to in-memory NeXus file
    :param json_input:
    :return: NeXus file and any warning messages produced from validating the JSON
    """

    if not json_input:
        raise ValueError("Empty json string, nothing to load!")

    json_data = json.loads(json_input)
    validation_output = validate_top_level_fields(json_data)

    wrapper = NexusWrapper("json_to_nexus")

    return wrapper, validation_output
