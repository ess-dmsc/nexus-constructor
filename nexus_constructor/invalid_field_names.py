# Put in here to avoid circular imports

# These are invalid because there are separate inputs in the UI for these fields and therefore inputting them through
# the field name line edit would cause conflicts.
INVALID_FIELD_NAMES = [
    "description",
    "shape",
    "depends_on",
    "x_pixel_offset",
    "y_pixel_offset",
    "z_pixel_offset",
    "detector_number",
    "detector_faces",
    "pixel_shape",
]
