class CommonAttrs:
    """
    Commonly used attribute and field names, used to avoid typos.
    """

    DESCRIPTION = "description"
    NX_CLASS = "NX_class"
    UI_VALUE = "NCui_value"
    DEPENDS_ON = "depends_on"
    TRANSFORMATION_TYPE = "transformation_type"
    VECTOR = "vector"
    UNITS = "units"
    VERTICES = "vertices"
    NC_STREAM = "NCstream"


class CommonKeys:
    """
    Commonly used key names in the outputted JSON.
    """

    NAME = "name"
    VALUES = "values"
    TYPE = "type"
    SIZE = "size"
    CHILDREN = "children"
    ATTRIBUTES = "attributes"
    DATASET = "dataset"


class NodeType:
    STREAM = "stream"
    DATASET = "dataset"
    GROUP = "group"
    LINK = "link"


class TransformationType:
    TRANSLATION = "Translation"
    ROTATION = "Rotation"


INSTRUMENT_NAME = "instrument"
