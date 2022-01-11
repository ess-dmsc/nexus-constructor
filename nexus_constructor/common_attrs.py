class CommonAttrs:
    """
    Commonly used attribute and field names, used to avoid typos.
    """

    DESCRIPTION = "description"
    NX_CLASS = "NX_class"
    DEPENDS_ON = "depends_on"
    TRANSFORMATION_TYPE = "transformation_type"
    VECTOR = "vector"
    UNITS = "units"
    VERTICES = "vertices"


class CommonKeys:
    """
    Commonly used key names in the outputted JSON.
    """

    NAME = "name"
    VALUES = "values"
    TYPE = "type"
    DATA_TYPE = "dtype"
    MODULE = "module"
    CHILDREN = "children"
    ATTRIBUTES = "attributes"


class NodeType:
    CONFIG = "config"
    GROUP = "group"


class TransformationType:
    TRANSLATION = "translation"
    ROTATION = "rotation"


INSTRUMENT_NAME = "instrument"
SAMPLE_NAME = "sample"
ARRAY = "Array"
SCALAR = "Scalar"
SHAPE_GROUP_NAME = "shape"
PIXEL_SHAPE_GROUP_NAME = "pixel_shape"
CYLINDRICAL_GEOMETRY_NX_CLASS = "NXcylindrical_geometry"
OFF_GEOMETRY_NX_CLASS = "NXoff_geometry"
SHAPE_NX_CLASS = "NXshape"
NX_TRANSFORMATIONS = "NXtransformations"
NX_GEOMETRY = "NXgeometry"
