from typing import Any, Dict, List, Union

import numpy as np
from PySide2.QtGui import QVector3D

from nexus_constructor.common_attrs import (
    CYLINDRICAL_GEOMETRY_NX_CLASS,
    GEOMETRY_NX_CLASS,
    NX_BOX,
    OFF_GEOMETRY_NX_CLASS,
    PIXEL_SHAPE_GROUP_NAME,
    SHAPE_GROUP_NAME,
    SIZE,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.json.json_warnings import InvalidShape, JsonWarningsContainer
from nexus_constructor.json.load_from_json_utils import (
    _find_attribute_from_list_or_dict,
    _find_nx_class,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import (
    CYLINDERS,
    DETECTOR_FACES,
    DETECTOR_NUMBER,
    FACES,
    WINDING_ORDER,
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    Z_PIXEL_OFFSET,
    BoxGeometry,
    CylindricalGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.model.value_type import FLOAT_TYPES, INT_TYPES, VALUE_TYPE_TO_NP
from nexus_constructor.unit_utils import (
    METRES,
    units_are_expected_dimensionality,
    units_are_recognised_by_pint,
    units_have_magnitude_of_one,
)


def _convert_vertices_to_qvector3d(
    vertices: List[List[float]],
) -> List[QVector3D]:
    """
    Converts a list of vertices to QVector3D
    :param vertices: The list of vertices.
    :return: The list of QVector3D vertices.
    """
    return [QVector3D(*vertex) for vertex in vertices]


class ShapeReader:
    def __init__(self, component: Component, shape_info: Dict):
        self.component = component
        self.shape_info = shape_info
        self.warnings = JsonWarningsContainer()
        self.error_message = ""
        self.issue_message = ""
        self.shape = None

    def _get_shape_type(self):
        """
        Tries to determine if the shape is an OFF or Cylindrical geometry.
        :return: The shape type i attribute if it could be found, otherwise an empty string is returned.
        """
        try:
            return _find_nx_class(self.shape_info[CommonKeys.ATTRIBUTES])
        except KeyError:
            return ""

    def add_shape_to_component(self):

        shape_type = self._get_shape_type()

        # An error message means the shape object couldn't be made
        self.error_message = f"Error encountered when constructing {shape_type} for component {self.component.name}:"
        # An issue message means something didn't add up
        self.issue_message = f"Issue encountered when constructing {shape_type} for component {self.component.name}:"
        if shape_type == OFF_GEOMETRY_NX_CLASS:
            self._add_off_shape_to_component()
        elif shape_type == CYLINDRICAL_GEOMETRY_NX_CLASS:
            self._add_cylindrical_shape_to_component()
        elif shape_type == GEOMETRY_NX_CLASS:
            for child in self.shape_info[CommonKeys.CHILDREN][0][CommonKeys.CHILDREN]:
                if (
                    child[NodeType.CONFIG][CommonKeys.NAME] == SHAPE_GROUP_NAME
                    and child[NodeType.CONFIG][CommonKeys.VALUES] == NX_BOX
                ):
                    self._add_box_shape_to_component()
        else:
            self.warnings.append(
                InvalidShape(
                    f"Unrecognised shape type for component {self.component.name}. Expected '{OFF_GEOMETRY_NX_CLASS}' or "
                    f"'{CYLINDRICAL_GEOMETRY_NX_CLASS}' but found '{shape_type}'."
                )
            )

    def _add_off_shape_to_component(self):
        """
        Attempts to create an OFF Geometry and set this as the shape of the component. If the required information can
        be found and passes validation then the geometry is created and writen to the component, otherwise the function
        just returns without changing the component.
        """
        children = self.children
        if not children:
            return

        name = self.name

        if not isinstance(children, list):
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Children attribute in shape group is not a list."
                )
            )
            return

        faces_dataset = self._get_shape_dataset_from_list(FACES, children)
        if not faces_dataset:
            return

        vertices_dataset = self._get_shape_dataset_from_list(
            CommonAttrs.VERTICES, children
        )
        if not vertices_dataset:
            return

        winding_order_dataset = self._get_shape_dataset_from_list(
            WINDING_ORDER, children
        )
        if not winding_order_dataset:
            return

        faces_dtype = self._find_and_validate_data_type(faces_dataset, INT_TYPES, FACES)
        faces_starting_indices = self._find_and_validate_values_list(
            faces_dataset, INT_TYPES, FACES
        )
        if not faces_starting_indices:
            return

        units = self._find_and_validate_units(vertices_dataset)
        if not units:
            return

        self._find_and_validate_data_type(
            vertices_dataset, FLOAT_TYPES, CommonAttrs.VERTICES
        )
        vertices = self._find_and_validate_values_list(
            vertices_dataset, FLOAT_TYPES, CommonAttrs.VERTICES
        )
        if not vertices:
            return
        vertices = _convert_vertices_to_qvector3d(vertices)

        winding_order_dtype = self._find_and_validate_data_type(
            winding_order_dataset, INT_TYPES, WINDING_ORDER
        )
        winding_order = self._find_and_validate_values_list(
            winding_order_dataset, INT_TYPES, WINDING_ORDER
        )
        if not winding_order:
            return

        off_geometry = self.__create_off_geometry(
            faces_dtype,
            faces_starting_indices,
            name,
            units,
            vertices,
            winding_order,
            winding_order_dtype,
        )
        self.component[name] = off_geometry
        self.shape = off_geometry

    @staticmethod
    def __create_off_geometry(
        faces_dtype,
        faces_starting_indices,
        name,
        units,
        vertices,
        winding_order,
        winding_order_dtype,
    ):
        off_geometry = OFFGeometryNexus(name)
        off_geometry.nx_class = OFF_GEOMETRY_NX_CLASS
        off_geometry.vertices = vertices
        off_geometry.units = units
        off_geometry.set_field_value(FACES, faces_starting_indices, faces_dtype)
        off_geometry.set_field_value(
            WINDING_ORDER, np.array(winding_order), winding_order_dtype
        )
        return off_geometry

    def _add_box_shape_to_component(self):
        """
        Attempts to create a box geometry and set this as the shape of the component. If the required
        information can be found and passes validation then the geometry is created and written to the component,
        otherwise the function just returns without changing the component.
        """
        children = self.children[0][CommonKeys.CHILDREN]
        name = self.name
        if not children:
            return
        tmp_dict = {}
        for child in children:
            if NodeType.CONFIG in child:
                tmp_dict[child[NodeType.CONFIG][CommonKeys.NAME]] = child[
                    NodeType.CONFIG
                ]
        units = self.__get_units(children)
        size = tmp_dict[SIZE][CommonKeys.VALUES]
        box_geometry = BoxGeometry(size[0], size[1], size[2], name, units)
        self.component[name] = box_geometry
        self.shape = box_geometry  # type:ignore

    @staticmethod
    def __get_units(children):
        for child in children:
            if CommonKeys.ATTRIBUTES in child:
                for attr in child[CommonKeys.ATTRIBUTES]:
                    if attr[CommonKeys.NAME] == CommonAttrs.UNITS:
                        return attr[CommonKeys.VALUES]
        return None

    def _add_cylindrical_shape_to_component(self):
        """
        Attempts to create a cylindrical geometry and set this as the shape of the component. If the required
        information can be found and passes validation then the geometry is created and written to the component,
        otherwise the function just returns without changing the component.
        """
        children = self.children
        if not children:
            return

        name = self.name

        vertices_dataset = self._get_shape_dataset_from_list(
            CommonAttrs.VERTICES, children
        )
        if not vertices_dataset:
            return

        cylinders_dataset = self._get_shape_dataset_from_list(CYLINDERS, children)
        if not cylinders_dataset:
            return

        units = self._find_and_validate_units(vertices_dataset)
        if not units:
            return

        cylinders_dtype = self._find_and_validate_data_type(
            cylinders_dataset, INT_TYPES, CYLINDERS
        )
        cylinders_list = self._find_and_validate_values_list(
            cylinders_dataset, INT_TYPES, CYLINDERS
        )
        if not cylinders_list:
            return

        vertices_dtype = self._find_and_validate_data_type(
            vertices_dataset, FLOAT_TYPES, CommonAttrs.VERTICES
        )
        vertices = self._find_and_validate_values_list(
            vertices_dataset, FLOAT_TYPES, CommonAttrs.VERTICES
        )
        if not vertices:
            return

        cylindrical_geometry = self.__create_cylindrical_geometry(
            cylinders_dtype, cylinders_list, name, units, vertices, vertices_dtype
        )
        self.component[name] = cylindrical_geometry
        self.shape = cylindrical_geometry

    @staticmethod
    def __create_cylindrical_geometry(
        cylinders_dtype, cylinders_list, name, units, vertices, vertices_dtype
    ):
        cylindrical_geometry = CylindricalGeometry(name)
        cylindrical_geometry.nx_class = CYLINDRICAL_GEOMETRY_NX_CLASS
        cylindrical_geometry.set_field_value(
            CYLINDERS, np.array(cylinders_list), cylinders_dtype
        )
        cylindrical_geometry.set_field_value(
            CommonAttrs.VERTICES, np.vstack(vertices), vertices_dtype
        )
        cylindrical_geometry[CommonAttrs.VERTICES].attributes.set_attribute_value(
            CommonAttrs.UNITS, units
        )
        return cylindrical_geometry

    def _get_shape_dataset_from_list(
        self, dataset_name: str, children: List[Dict], warning: bool = True
    ) -> Union[Dict, None]:
        """
        Tries to find a given shape dataset from a list of datasets.
        :param dataset_name: The name of the dataset that the function will search for.
        :param children: The children list where we expect to find the dataset.
        :return: The dataset if it could be found, otherwise None is returned.
        """
        for dataset in children:
            try:
                if dataset[NodeType.CONFIG][CommonKeys.NAME] == dataset_name:
                    return dataset
            except KeyError:
                pass
        if warning:
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Couldn't find {dataset_name} dataset."
                )
            )
        return None

    def _find_and_validate_data_type(
        self, dataset: Dict, expected_types: List[str], parent_name: str
    ) -> Union[str, None]:
        """
        Checks if the type in the dataset attribute has an expected value. Failing this check does not stop the geometry
        creation.
        :param dataset: The dataset where we expect to find the type information.
        :param expected_types: The expected type that the dataset type field should contain.
        :param parent_name: The name of the parent dataset
        """
        try:
            found_type = None
            if CommonKeys.DATA_TYPE in dataset[NodeType.CONFIG]:
                found_type = dataset[NodeType.CONFIG][CommonKeys.DATA_TYPE]
            elif CommonKeys.TYPE in dataset[NodeType.CONFIG]:
                found_type = dataset[NodeType.CONFIG][CommonKeys.TYPE]
            else:
                self.warnings.append(
                    InvalidShape(
                        f"{self.issue_message} Type attribute for {parent_name} not found."
                    )
                )
            if found_type is not None and found_type not in expected_types:
                self.warnings.append(
                    InvalidShape(
                        f"{self.issue_message} Type attribute for {parent_name} does not match expected type(s) "
                        f"{expected_types}."
                    )
                )
            elif found_type is not None:
                return found_type
        except KeyError:
            self.warnings.append(
                InvalidShape(
                    f"{self.issue_message} Unable to find type attribute for {parent_name}."
                )
            )

        return None

    def _find_and_validate_units(self, vertices_dataset: Dict) -> Union[str, None]:
        """
        Attempts to retrieve and validate the units data.
        :param vertices_dataset: The vertices dataset.
        :return: Th units value if it was found and passed validation, otherwise None is returned.
        """
        try:
            attributes_list = vertices_dataset[CommonKeys.ATTRIBUTES]
        except KeyError:
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Unable to find attributes list in vertices dataset."
                )
            )
            return None

        units = _find_attribute_from_list_or_dict(CommonAttrs.UNITS, attributes_list)
        if not units:
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Unable to find units attribute in vertices dataset."
                )
            )
            return None

        if not units_are_recognised_by_pint(units, False):
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Vertices units are not recognised by pint. Found {units}."
                )
            )
            return None
        if not units_are_expected_dimensionality(units, METRES, False):
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Vertices units have wrong dimensionality. Expected something that can be "
                    f"converted to metred but found {units}. "
                )
            )
            return None
        if not units_have_magnitude_of_one(units, False):
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Vertices units do not have magnitude of one. Found {units}."
                )
            )
            return None

        return units

    def _all_in_list_have_expected_type(
        self, values: List, expected_types: List[str], list_parent_name: str
    ) -> bool:
        """
        Checks if all the items in a given list have the expected type.
        :param values: The list of values.
        :param expected_types: The expected types.
        :param list_parent_name: The name of the dataset the list belongs to.
        :return: True of all the items in the list have the expected type, False otherwise.
        """
        flat_array = np.array(values).flatten()
        if all(
            [
                type(value)
                in [
                    numpy_dtype
                    for human_readable_type, numpy_dtype in VALUE_TYPE_TO_NP.items()
                    if human_readable_type in expected_types
                ]
                for value in flat_array
            ]
        ):
            return True
        self.warnings.append(
            InvalidShape(
                f"{self.error_message} Values in {list_parent_name} list do not all have type(s) {expected_types}."
            )
        )
        return False

    def _get_values_attribute(
        self, dataset: Dict, parent_name: str
    ) -> Union[List, None]:
        """
        Attempts to get the values attribute in a dataset. Creates an error message if it cannot be found.
        :param dataset: The dataset we hope to find the values attribute in.
        :param parent_name: The name of the parent dataset.
        :return: The values attribute if it could be found, otherwise None is returned.
        """
        try:
            return dataset[NodeType.CONFIG][CommonKeys.VALUES]
        except KeyError:
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Unable to find values in {parent_name} dataset."
                )
            )
            return None

    def _attribute_is_a_list(self, attribute: Any, parent_name: str) -> bool:
        """
        Checks if an attribute has the type list.
        :param attribute: The attribute to check.
        :param parent_name: The name of the parent dataset.
        :return: True if attribute is a list, False otherwise.
        """
        if isinstance(attribute, list):
            return True

        self.warnings.append(
            InvalidShape(
                f"{self.error_message} values attribute in {parent_name} dataset is not a list."
            )
        )
        return False

    @property
    def children(self) -> Union[List, None]:
        """
        Attempts to get the children list from the shape dictionary.
        :return: The children list if it could be found, otherwise None is returned.
        """
        try:
            return self.shape_info[CommonKeys.CHILDREN]
        except KeyError:
            self.warnings.append(
                InvalidShape(
                    f"{self.error_message} Unable to find children list in shape group."
                )
            )
            return None

    @property
    def name(self) -> str:
        """
        Attempts to get the name attribute from the shape dictionary.
        :return: The name if it could be found, otherwise 'shape' is returned.
        """
        try:
            return self.shape_info[CommonKeys.NAME]
        except KeyError:
            self.warnings.append(
                InvalidShape(
                    f"{self.issue_message} Unable to find name of shape. Will use 'shape'."
                )
            )
            return SHAPE_GROUP_NAME

    def _find_and_validate_values_list(
        self, dataset: Dict, expected_types: List[str], attribute_name: str
    ) -> Union[List, None]:
        """
        Attempts to find and validate the contents of the values attribute from the dataset.
        :param dataset: The dataset containing the values list.
        :param expected_types: The type(s) we expect the values list to have.
        :param attribute_name: The name of the attribute.
        :return: The values list if it was found and passed validation, otherwise None is returned.
        """
        values = self._get_values_attribute(dataset, attribute_name)
        if not values:
            return None

        if not self._attribute_is_a_list(values, attribute_name):
            return None

        if not self._all_in_list_have_expected_type(
            values, expected_types, attribute_name
        ):
            return None

        return values

    def add_pixel_data_to_component(self, children: List[Dict]):
        """
        Attempts to find and write pixel information to the component.
        :param children: The JSON children list for the component.
        """
        shape_has_pixel_grid = (
            self.shape_info[CommonKeys.NAME] == PIXEL_SHAPE_GROUP_NAME
        )

        self._get_detector_number(children, shape_has_pixel_grid)

        # return if the shape is not a pixel grid
        if not shape_has_pixel_grid:
            # Shape is pixel mapping
            self._handle_mapping(children)
            return

        for offset in [X_PIXEL_OFFSET, Y_PIXEL_OFFSET, Z_PIXEL_OFFSET]:
            self._find_and_add_pixel_offsets_to_component(offset, children)

    def _get_detector_number(self, children: List[Dict], shape_has_pixel_grid: bool):
        """
        Attempt to find the detector_number in the component group, and if found apply it the model component.
        :param children:
        :param shape_has_pixel_grid:
        :return:
        """
        detector_number_dataset = self._get_shape_dataset_from_list(
            DETECTOR_NUMBER, children, shape_has_pixel_grid
        )
        if detector_number_dataset:
            detector_number_dtype = self._find_and_validate_data_type(
                detector_number_dataset, INT_TYPES, DETECTOR_NUMBER
            )
            detector_number = self._find_and_validate_values_list(
                detector_number_dataset, INT_TYPES, DETECTOR_NUMBER
            )
            if detector_number:
                self.component.set_field_value(
                    DETECTOR_NUMBER, detector_number, detector_number_dtype
                )
                if self.shape and isinstance(self.shape, CylindricalGeometry):
                    self.shape.detector_number = detector_number

    def _handle_mapping(self, children: List[Dict]):
        shape_group = self._get_shape_dataset_from_list(
            SHAPE_GROUP_NAME, children, False
        )
        if shape_group and self.shape:
            detector_faces_dataset = self._get_shape_dataset_from_list(
                DETECTOR_FACES, shape_group[CommonKeys.CHILDREN], False
            )
            self.shape.detector_faces = detector_faces_dataset[CommonKeys.VALUES]

    def _find_and_add_pixel_offsets_to_component(
        self, offset_name: str, children: List[Dict]
    ):
        """
        Attempts to find and add pixel offset data to the component.
        :param offset_name: The name of the pixel offset field.
        :param children: The JSON children list for the component.
        """
        offset_dataset = self._get_shape_dataset_from_list(
            offset_name, children, offset_name != Z_PIXEL_OFFSET
        )
        if not offset_dataset:
            return

        pixel_offset_dtype = self._find_and_validate_data_type(
            offset_dataset, FLOAT_TYPES, offset_name
        )
        pixel_offset = self._find_and_validate_values_list(
            offset_dataset, FLOAT_TYPES, offset_name
        )
        if not pixel_offset:
            return

        units = self.__get_units([offset_dataset])
        self.component.set_field_value(
            offset_name,
            np.array(pixel_offset),
            pixel_offset_dtype,
            units if units else "m",
        )
