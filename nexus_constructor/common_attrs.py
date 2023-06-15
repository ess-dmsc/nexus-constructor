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
    OFFSET = "offset"


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
FILEWRITER = "Filewriter"
SHAPE_GROUP_NAME = "shape"
PIXEL_SHAPE_GROUP_NAME = "pixel_shape"
GEOMETRY_GROUP_NAME = "geometry"
CYLINDRICAL_GEOMETRY_NX_CLASS = "NXcylindrical_geometry"
OFF_GEOMETRY_NX_CLASS = "NXoff_geometry"
SHAPE_NX_CLASS = "NXshape"
NX_SAMPLE = "NXsample"
NX_USER = "NXuser"
NX_TRANSFORMATIONS = "NXtransformations"
GEOMETRY_NX_CLASS = "NXgeometry"
NX_BOX = "nxbox"
SIZE = "size"
TRANSFORMATIONS = "transformations"

USERS_PLACEHOLDER = "$USERS$"
SAMPLE_PLACEHOLDER = "$SAMPLE$"
AD_ARRAY_SIZE_PLACEHOLDER = "$AREADET$"

NX_CLASSES_WITH_PLACEHOLDERS = {
    NX_SAMPLE: SAMPLE_PLACEHOLDER,
}
