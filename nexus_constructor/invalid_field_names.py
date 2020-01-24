# Put in here to avoid circular imports

# These are invalid because there are separate inputs in the UI for these fields and therefore inputting them through
# the field name line edit would cause conflicts.
from nexus_constructor.common_attrs import CommonAttrs
from nexus_constructor.pixel_data_to_nexus_utils import PIXEL_FIELDS

INVALID_FIELD_NAMES = [
    "description",
    "shape",
    CommonAttrs.DEPENDS_ON,
    "pixel_shape",
] + PIXEL_FIELDS
