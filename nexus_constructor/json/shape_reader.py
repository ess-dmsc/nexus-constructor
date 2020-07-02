from typing import List, Union

from PySide2.QtGui import QVector3D

from nexus_constructor.json.load_from_json_utils import (
    _find_nx_class,
    _find_attribute_from_list_or_dict,
)
from nexus_constructor.model.component import (
    Component,
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    OFF_GEOMETRY_NX_CLASS,
)
from nexus_constructor.unit_utils import (
    units_are_recognised_by_pint,
    METRES,
    units_are_expected_dimensionality,
    units_have_magnitude_of_one,
)

INT_TYPE = "int"


def _all_in_list_have_expected_type(values: list, expected_type: str):
    return all([expected_type in str(type(value)) for value in values])


class ShapeReader:
    def __init__(self, component: Component, shape_info: dict):
        self.component = component
        self.shape_info = shape_info
        self.warnings = []
        self.error_message = ""

    def _get_shape_type(self):
        try:
            return _find_nx_class(self.shape_info["attributes"])
        except KeyError:
            return None

    def add_shape_to_component(self):

        shape_type = self._get_shape_type()

        self.error_message = f"Error encountered when constructing {shape_type} for component {self.component.name}:"
        self.issue_message = f"Issue encountered when constructing {shape_type} for component {self.component.name}:"

        if shape_type == OFF_GEOMETRY_NX_CLASS:
            self._add_off_shape_to_component()
        elif shape_type == CYLINDRICAL_GEOMETRY_NX_CLASS:
            self._add_cylindrical_shape_to_component()
        else:
            self.warnings.append(
                f"Unrecgonised shape type for component {self.component.name}. Expected '{OFF_GEOMETRY_NX_CLASS}' or '{CYLINDRICAL_GEOMETRY_NX_CLASS}' but found '{shape_type}.'"
            )

    def _add_off_shape_to_component(self):
        try:
            children = self.shape_info["children"]
        except KeyError:
            self.warnings.append("No children!")  # todo: proper messages
            return

        faces_dataset = self._get_shape_attribute_from_list("faces", children)
        if not faces_dataset:
            return

        vertices_dataset = self._get_shape_attribute_from_list("vertices", children)
        if not vertices_dataset:
            return

        winding_order_dataset = self._get_shape_attribute_from_list(
            "winding_order", children
        )
        if not winding_order_dataset:
            return

        faces = self._find_and_validate_faces_list(
            faces_dataset
        )  # todo: format for OFFGeometry class?
        if not faces:
            return

        units = self._find_and_validate_units(vertices_dataset)
        if not units:
            return

        vertices = self._find_and_validate_vertices(vertices_dataset)
        if not vertices:
            return

        winding_order = self._find_and_validate_winding_order(winding_order_dataset)
        if not winding_order:
            return

    def _add_cylindrical_shape_to_component(self):
        pass

    def _get_shape_attribute_from_list(
        self, attribute_name: str, children: List[dict]
    ) -> Union[dict, None]:
        for attribute in children:
            try:
                if attribute["name"] == attribute_name:
                    return attribute
            except KeyError:
                self.warnings.append(
                    f"Couldn't find attribute {attribute_name} for shape in component {self.component.name}."
                )

    def _find_and_validate_faces_list(
        self, faces_dataset: dict
    ) -> Union[List[int], None]:

        self._validate_data_type(faces_dataset, "int", "faces")

        try:
            faces = faces_dataset["values"]
        except KeyError:
            self.warnings.append("A message.")
            return

        if not isinstance(faces, list):
            self.warnings.append("A message.")
            return

        self._validate_list_size(faces_dataset["dataset"], faces, "faces")

        if not _all_in_list_have_expected_type(faces, "int"):
            self.warnings.append("A message.")
            return

        return faces

    def _find_and_validate_vertices(
        self, vertices_dataset: dict
    ) -> Union[List[int], None]:

        self._validate_data_type(vertices_dataset, "float", "vertices")

        try:
            values = vertices_dataset["values"]
        except KeyError:
            self.warnings.append(
                f"{self.error_message} Unable to find vertices list in vertices dataset."
            )
            return

        if not isinstance(values, list):
            self.warnings.append(
                f"{self.error_message} Vertices attribute is not a list."
            )
            return

        self._validate_list_size(vertices_dataset["dataset"], values, "vertices")

        vertices = []

        for value in values:
            try:
                vertices.append(QVector3D(*value))
            except TypeError:
                self.warnings.append(
                    f"{self.error_message} Unable to convert vertices values to QVector3D."
                )
                return

        return vertices

    def _validate_data_type(self, dataset: dict, expected_type: str, parent_name: str):
        """
        Checks if the type in the dataset attribute has an expected value. Failing this check does not stop the geometry
        creation.
        :param dataset: The dataset.
        :param expected_type: The expected type that the dataset type field should contain.
        :param parent_name: The name of the parent dataset
        """
        try:
            if expected_type not in dataset["dataset"]["type"]:
                self.warnings.append(
                    f"{self.issue_message} Type attribute for {parent_name} doe not match expected type {expected_type}."
                )
        except KeyError:
            self.warnings.append(
                f"{self.issue_message} Unable to find type attribute for {parent_name}."
            )

    def _find_and_validate_units(self, vertices_dataset: dict) -> Union[str, None]:
        """
        Attempts to retrieve and validate the units data.
        :param vertices_dataset: The vertices dataset.
        :return: Th units value if it was found and passed validation, otherwise None is returned.
        """
        try:
            attributes_list = vertices_dataset["attributes"]
        except KeyError:
            self.warnings.append(
                f"{self.error_message} Unable to find attributes list in vertices dataset."
            )
            return

        units = _find_attribute_from_list_or_dict("units", attributes_list)
        if not units:
            self.warnings.append(
                f"{self.error_message} Unable to find units attribute in vertices dataset."
            )
            return

        if not units_are_recognised_by_pint(units, False):
            self.warnings.append(
                f"{self.error_message} Vertices units are not recognised by pint. Found {units}."
            )
            return
        if not units_are_expected_dimensionality(units, METRES, False):
            self.warnings.append(
                f"{self.error_message} Vertices units have wrong dimensionality. Expected something that can be converted to metred but found {units}."
            )
            return
        if not units_have_magnitude_of_one(units, False):
            self.warnings.append(
                f"{self.error_message} Vertices units do not have magnitude of one. Found {units}."
            )
            return

        return units

    def _find_and_validate_winding_order(
        self, winding_order_dataset: dict
    ) -> Union[List[int], None]:
        """
        Attempts to retrieve and validate the winding order data.
        :param winding_order_dataset: The winding order dataset.
        :return: The winding order list if it was found and passed validation, otherwise None is returned.
        """
        self._validate_data_type(winding_order_dataset, "int", "winding order")

        try:
            values = winding_order_dataset["values"]
        except KeyError:
            self.warnings.append(
                f"{self.error_message} Unable to find values attribute in winding order dataset."
            )
            return

        if not isinstance(values, list):
            self.warnings.append(
                f"{self.error_message} Values in winding order dataset is not a list."
            )
            return

        self._validate_list_size(
            winding_order_dataset["dataset"], values, "winding order"
        )

        if not _all_in_list_have_expected_type(values, INT_TYPE):
            self.warnings.append(
                f"{self.error_message} Values list in winding order dataset do not all have type {INT_TYPE}."
            )
            return

        return values

    def _validate_list_size(
        self, data_properties: dict, values: List, parent_name: str
    ):
        """
        Checks to see if the length of a list matches the size attribute in the dataset. A warning is recorded if the
        size attribute cannot be found or if this value doesn't match the length of the list. Failing this check does
        not stop the geometry creation.
        :param data_properties: The dictionary containing he size attribute.
        :param values: The list of values.
        :param parent_name: The name of the parent dataset.
        """
        try:
            if data_properties["size"][0] != len(values):
                self.warnings.append(
                    f"{self.issue_message} Mismatch between length of {parent_name} list ({len(values)}) and size attribute from dataset ({data_properties['size'][0]})."
                )
        except KeyError:
            self.warnings.append(
                f"{self.issue_message} Unable to find size attribute for {parent_name} dataset."
            )
