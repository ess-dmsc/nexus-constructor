from typing import Sequence

from PySide2.QtWidgets import QListWidget
import numpy as np
from h5py import Group

from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails
from nexus_constructor.nexus.nexus_wrapper import decode_bytes_string
from nexus_constructor.validators import DATASET_TYPE

SLIT_EDGES_NAME = "slit_edges"
SLITS_NAME = "slits"
RADIUS_NAME = "radius"
SLIT_HEIGHT_NAME = "slit_height"
NAME = "name"

UNABLE = "Unable to create chopper geometry - "
EXPECTED_TYPE_ERROR_MSG = {
    SLIT_EDGES_NAME: "float",
    SLITS_NAME: "int",
    RADIUS_NAME: "float",
    SLIT_HEIGHT_NAME: "float",
}

REQUIRED_CHOPPER_FIELDS = {SLIT_EDGES_NAME, SLITS_NAME, RADIUS_NAME, SLIT_HEIGHT_NAME}
INT_TYPES = [value for value in DATASET_TYPE.values() if "int" in str(value)]
FLOAT_TYPES = [value for value in DATASET_TYPE.values() if "float" in str(value)]


def incorrect_field_type_message(fields_dict: dict, field_name: str):
    """
    Creates a string explaining to the user that the field input did not have the expected type.
    :param fields_dict: The dictionary containing the different data fields for the disk chopper.
    :param field_name: The name of the field that failed the check.
    :return: A string that contains the name of the field, the type it should have, and the type the user entered.
    """
    return "Wrong {} type. Expected {} but found {}.".format(
        field_name, EXPECTED_TYPE_ERROR_MSG[field_name], type(fields_dict[field_name])
    )


def check_data_type(data_type, expected_types):
    try:
        return data_type.dtype in expected_types
    except AttributeError:
        return False


class GenericChopperChecker:
    def __init__(self):

        self._chopper_details = None
        self._angle_units = None
        self._slit_height_units = None
        self._radius_units = None

    @staticmethod
    def fields_have_correct_type(fields_dict: dict):

        correct_slits_type = check_data_type(fields_dict[SLITS_NAME], INT_TYPES)
        correct_radius_type = check_data_type(fields_dict[RADIUS_NAME], FLOAT_TYPES)
        correct_slit_height_type = check_data_type(
            fields_dict[SLIT_HEIGHT_NAME], FLOAT_TYPES
        )
        correct_slit_edges_type = check_data_type(
            fields_dict[SLIT_EDGES_NAME], FLOAT_TYPES
        )

        if (
            correct_slits_type
            and correct_radius_type
            and correct_slit_height_type
            and correct_slit_edges_type
        ):
            return True

        problems = []

        if not correct_slits_type:
            problems.append(incorrect_field_type_message(fields_dict, SLITS_NAME))

        if not correct_radius_type:
            problems.append(incorrect_field_type_message(fields_dict, RADIUS_NAME))

        if not correct_slit_height_type:
            problems.append(incorrect_field_type_message(fields_dict, SLIT_HEIGHT_NAME))

        if not correct_slit_edges_type:
            problems.append(incorrect_field_type_message(fields_dict, SLIT_EDGES_NAME))

        print(UNABLE + "\n".join(problems))
        return False

    @staticmethod
    def edges_array_has_correct_shape(edges_dim: int, edges_shape: tuple):
        """
        Checks that the edges array consists of either one row or one column.
        :return: True if the edges array is 1D. False otherwise.
        """
        if edges_dim > 2:
            print(
                UNABLE
                + "Expected slit edges array to be 1D but it has {} dimensions.".format(
                    edges_dim
                )
            )
            return False

        if edges_dim == 2:
            if edges_shape[0] != 1 and edges_shape[1] != 1:
                print(
                    UNABLE
                    + "Expected slit edges array to be 1D but it has shape {}.".format(
                        edges_shape
                    )
                )
                return False

        return True

    @staticmethod
    def input_describes_valid_chopper(
        chopper_details: ChopperDetails, slit_edges: Sequence
    ):
        """
        A final check that the input has the following properties:
            - The length of the slit edges array is twice the number of slits
            - The slit height is smaller than the radius
            - The slit edges array is sorted.
            - The slit edges array doesn't contain repeated angles.
            - The slit edges array doesn't contain overlapping slits.
        If this is all true then a chopper mesh can be created.
        :return: True if all the conditions above are met. False otherwise.
        """
        # Check that the number of slit edges is equal to two times the number of slits
        if len(chopper_details.slit_edges) != 2 * chopper_details.slits:
            print(
                UNABLE
                + "Size of slit edges array should be twice the number of slits. Instead there are {} slits and {} slit edges.".format(
                    chopper_details.slits, len(chopper_details.slit_edges)
                )
            )
            return False

        # Check that the slit height is smaller than the radius
        if chopper_details.slit_height >= chopper_details.radius:
            print(
                UNABLE
                + "Slit height should be smaller than radius. Instead slit height is {} and radius is {}".format(
                    chopper_details.slit_height, chopper_details.radius
                )
            )
            return False

        # Check that the list of slit edges is sorted
        if not (np.diff(slit_edges) >= 0).all():
            print(UNABLE + "Slit edges array is not sorted. Found values:", slit_edges)
            return False

        # Check that there are no repeated angles
        if len(slit_edges) != len(np.unique(slit_edges)):
            print(
                UNABLE + "Angles in slit edges array should be unique. Found values:",
                slit_edges,
            )
            return False

        # Check that the first and last edges do not overlap
        if (chopper_details.slit_edges != sorted(chopper_details.slit_edges)) and (
            chopper_details.slit_edges[-1] >= chopper_details.slit_edges[0]
        ):
            print(
                UNABLE + "Slit edges contains overlapping slits. Found values:",
                slit_edges,
            )
            return False

        return True


class UserDefinedChopperChecker:
    def __init__(self, fields_widget: QListWidget):

        self.fields_dict = dict()
        self._chopper_details = None

        self._angle_units = "deg"
        self._slit_height_units = "m"
        self._radius_units = "m"

        for i in range(fields_widget.count()):
            widget = fields_widget.itemWidget(fields_widget.item(i))
            self.fields_dict[widget.name] = widget

        self._generic_chopper_checker = GenericChopperChecker()

    def get_chopper_details(self):
        """
        :return: The ChopperDetails object of the user-defined disk chopper.
        """
        return self._chopper_details

    def required_fields_present(self):
        """
        Checks that all of the fields required to create the disk chopper are present.
        :return: True if all the required fields are present. False otherwise.
        """
        missing_fields = REQUIRED_CHOPPER_FIELDS - self.fields_dict.keys()

        if len(missing_fields) > 0:
            print(UNABLE + "Required field(s) missing:", ", ".join(missing_fields))
            return False

        return True

    def validate_chopper(self):
        """
        Performs the following checks in order to determine if the chopper input is valid: 1) Checks that the required
        fields are present, 2) Checks that the fields have the correct type, 3) Checks that the slit edges array is 1D,
        and 4) Checks that the overall chopper geometry is valid (no overlapping slits, repeated angles, etc).
        :return: True if the chopper is valid. False otherwise.
        """
        if not (
            self.required_fields_present()
            and self._generic_chopper_checker.fields_have_correct_type(self.fields_dict)
            and self._generic_chopper_checker.edges_array_has_correct_shape(
                self.fields_dict[SLIT_EDGES_NAME].value.ndim,
                self.fields_dict[SLIT_EDGES_NAME].value.shape,
            )
        ):
            return False

        self._chopper_details = ChopperDetails(
            self.fields_dict[SLITS_NAME].value,
            self.fields_dict[SLIT_EDGES_NAME].value,
            self.fields_dict[RADIUS_NAME].value,
            self.fields_dict[SLIT_HEIGHT_NAME].value,
            self._angle_units,
            self._slit_height_units,
            self._radius_units,
        )

        return self._generic_chopper_checker.input_describes_valid_chopper(
            self._chopper_details, self.fields_dict[SLIT_EDGES_NAME].value
        )


class NexusDefinedChopperChecker:
    def __init__(self, disk_chopper: Group):

        self.fields_dict = dict()
        self._chopper_details = None
        self._angle_units = None
        self._slit_height_units = None
        self._radius_units = None

        self._generic_chopper_checker = GenericChopperChecker()
        self._disk_chopper = disk_chopper

    def get_chopper_details(self):
        """
        :return: The ChopperDetails object of the NeXus-defined disk chopper.
        """
        return self._chopper_details

    def required_fields_present(self):

        try:

            self.fields_dict[SLITS_NAME] = self._disk_chopper[SLITS_NAME][()]
            self.fields_dict[SLIT_EDGES_NAME] = self._disk_chopper[SLIT_EDGES_NAME][()]
            self.fields_dict[RADIUS_NAME] = self._disk_chopper[RADIUS_NAME][()]
            self.fields_dict[SLIT_HEIGHT_NAME] = self._disk_chopper[SLIT_HEIGHT_NAME][
                ()
            ]
            self._angle_units = decode_bytes_string(
                self._disk_chopper[SLIT_EDGES_NAME].attrs["units"]
            )
            self._slit_height_units = decode_bytes_string(
                self._disk_chopper[SLIT_HEIGHT_NAME].attrs["units"]
            )
            self._radius_units = decode_bytes_string(
                self._disk_chopper[RADIUS_NAME].attrs["units"]
            )
            self._disk_chopper[NAME][()],

        except KeyError:
            print(self._radius_units)
            return False

        return True

    def validate_chopper(self):
        """
        Performs the following checks in order to determine if the chopper input is valid: 1) Checks that the required
        fields are present, 2) Checks that the fields have the correct type, 3) Checks that the slit edges array is 1D,
        and 4) Checks that the overall chopper geometry is valid (no overlapping slits, repeated angles, etc).
        :return: True if the chopper is valid. False otherwise.
        """
        if not (
            self.required_fields_present()
            and self._generic_chopper_checker.fields_have_correct_type(self.fields_dict)
            and self._generic_chopper_checker.edges_array_has_correct_shape(
                self.fields_dict[SLIT_EDGES_NAME].ndim,
                self.fields_dict[SLIT_EDGES_NAME].shape,
            )
        ):
            return False

        self._chopper_details = ChopperDetails(
            self.fields_dict[SLITS_NAME],
            self.fields_dict[SLIT_EDGES_NAME],
            self.fields_dict[RADIUS_NAME],
            self.fields_dict[SLIT_HEIGHT_NAME],
            self._angle_units,
            self._slit_height_units,
            self._radius_units,
        )

        return self._generic_chopper_checker.input_describes_valid_chopper(
            self._chopper_details, self.fields_dict[SLIT_EDGES_NAME]
        )
