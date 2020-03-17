from typing import Dict, Any


def get_item(dictionary_to_look_in: Dict[str, Any], attr_name: str) -> Any:
    return (
        dictionary_to_look_in[attr_name] if attr_name in dictionary_to_look_in else None
    )


def set_item(dictionary_to_look_in, item_name, new_value):
    dictionary_to_look_in[item_name] = new_value
