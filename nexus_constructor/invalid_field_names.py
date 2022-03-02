# Put in here to avoid circular imports

# These are invalid because there are separate inputs in the UI for these fields and therefore inputting them through
# the field name line edit would cause conflicts.
from nexus_constructor.common_attrs import (
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    TRANSFORMATIONS,
    CommonAttrs,
)
from nexus_constructor.geometry.pixel_data_utils import PIXEL_FIELDS

INVALID_FIELD_NAMES = [
    CommonAttrs.DESCRIPTION,
    SHAPE_GROUP_NAME,
    CommonAttrs.DEPENDS_ON,
    PIXEL_SHAPE_GROUP_NAME,
    TRANSFORMATIONS,
] + PIXEL_FIELDS
