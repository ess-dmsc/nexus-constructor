from typing import Dict, Any, List, Union, TextIO

from nexus_constructor.json.filewriter_json_writer import object_to_json_file


def generate_forwarder_command(
    output_file: TextIO, streams: Dict[str, Dict[str, Any]], provider_type: str
):
    """
    Generate a forwarder command containing a list of PVs and which topics to route them to.
    :param output_file: file object to write the JSON output to.
    :param streams: dictionary of stream objects.
    :param provider_type: whether to use channel access or pv access protocol
    """
    tree_dict = dict()
    stream_list = _extract_forwarder_stream_info(streams, provider_type)
    tree_dict["streams"] = stream_list
    object_to_json_file(tree_dict, output_file)


def _extract_forwarder_stream_info(
    streams: Dict[str, Dict[str, Any]], provider_type: str
) -> List[Dict[str, Union[Dict, str]]]:
    """
    Extracts the forwarder stream information to write a forwarder JSON command.
    :param streams: A dictionary containing all streams in the nexus file
    :return: A list of streams containing dictionaries of PV names, topics and schemas.
    """
    stream_list = []
    pv_names = (
        dict()
    )  # key is pv name, value is index in stream_list where stream exists
    for _, stream in streams.items():
        writer_module = stream["writer_module"]
        if writer_module == "f142" or writer_module == "TdcTime":
            pv_name = stream["source"]
            if pv_name not in pv_names.keys():
                stream_list.append(
                    {
                        "channel": pv_name,
                        "converter": {
                            "schema": writer_module,
                            "topic": stream["topic"],
                        },
                        "channel_provider_type": provider_type,
                    }
                )
                pv_names[pv_name] = len(stream_list)
            else:
                duplicated_stream = stream_list[pv_names[pv_name] - 1]
                new_stream_converter = {
                    "schema": writer_module,
                    "topic": stream["topic"],
                }
                if isinstance(duplicated_stream["converter"], list):
                    duplicated_stream["converter"].append(new_stream_converter)
                elif isinstance(duplicated_stream["converter"], dict):
                    duplicated_stream["converter"] = [
                        duplicated_stream["converter"],
                        new_stream_converter,
                    ]
    return stream_list
