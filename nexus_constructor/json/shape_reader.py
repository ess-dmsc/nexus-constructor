from typing import List, Union

from nexus_constructor.json.load_from_json_utils import _find_nx_class
from nexus_constructor.model.component import (
    Component,
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    OFF_GEOMETRY_NX_CLASS,
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
            self.warnings.append("No children!")  # todo: proper message
            return

        faces_dataset = self._get_shape_attribute_from_list("faces", children)
        if not faces_dataset:
            return

        vertices_dataset = self._get_shape_attribute_from_list("vertices", children)
        if not vertices_dataset:
            return

        winding_order = self._get_shape_attribute_from_list("winding_order", children)
        if not winding_order:
            return

        faces = self._find_and_validate_faces_list(faces_dataset)
        if not faces:
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

        try:
            if "int" not in faces_dataset["dataset"]["type"]:
                self.warnings.append("A message.")
        except KeyError:
            self.warnings.append("A message.")
            pass

        try:
            faces = faces_dataset["values"]
        except KeyError:
            self.warnings.append("A message.")
            return

        if not all(["int" in str(type(face)) for face in faces]):
            self.warnings.append("A message.")
            return

        return faces

    def _find_and_validate_vertices(
        self, vertices_dataset: dict
    ) -> Union[List[int], None]:
        pass
