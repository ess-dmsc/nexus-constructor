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


class ShapeReader:
    def __init__(self, component: Component, shape_info: dict):
        self.component = component
        self.shape_info = shape_info
        self.warnings = []

    def _get_shape_type(self):
        try:
            return _find_nx_class(self.shape_info["attributes"])
        except KeyError:
            return None

    def add_shape_to_component(self):

        shape_type = self._get_shape_type()

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

        self._validate_data_type(faces_dataset, "int")

        try:
            faces = faces_dataset["values"]
        except KeyError:
            self.warnings.append("A message.")
            return

        if not isinstance(faces, list):
            self.warnings.append("A message.")
            return

        if not all(["int" in str(type(face)) for face in faces]):
            self.warnings.append("A message.")
            return

        return faces

    def _find_and_validate_vertices(
        self, vertices_dataset: dict
    ) -> Union[List[int], None]:

        self._validate_data_type(vertices_dataset, "float")

        try:
            values = vertices_dataset["values"]
        except KeyError:
            self.warnings.append("A message.")

        if not isinstance(values, list):
            self.warnings.append("A message.")
            return

        vertices = []

        for value in values:
            try:
                vertices.append(QVector3D(*value))
            except TypeError:
                self.warnings.append("A message.")
                return

        return vertices

    def _validate_data_type(self, dataset: dict, expected_type: str):

        try:
            if expected_type not in dataset["dataset"]["type"]:
                self.warnings.append("A message.")
        except KeyError:
            self.warnings.append("A message.")

    def _find_and_validate_units(self, vertices_dataset: dict) -> Union[str, None]:

        try:
            attributes_list = vertices_dataset["attributes"]
        except KeyError:
            self.warnings.append("A warnings.")
            return

        units = _find_attribute_from_list_or_dict("units", attributes_list)
        if not units:
            self.warnings.append("A warnings.")
            return

        if not units_are_recognised_by_pint(units, False):
            self.warnings.append("A warnings.")
            return
        if not units_are_expected_dimensionality(units, METRES, False):
            self.warnings.append("A warnings.")
            return
        if not units_have_magnitude_of_one(units, False):
            self.warnings.append("A warnings.")
            return

        return units
