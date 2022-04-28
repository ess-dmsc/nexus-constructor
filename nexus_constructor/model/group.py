from typing import TYPE_CHECKING, Any, Dict, List, Union

import attr

from nexus_constructor.common_attrs import (
    NX_CLASSES_WITH_PLACEHOLDERS,
    CommonAttrs,
    CommonKeys,
    NodeType,
)
from nexus_constructor.model.attributes import Attributes
from nexus_constructor.model.helpers import (
    _get_item,
    _remove_item,
    _set_item,
    get_absolute_path,
)
from nexus_constructor.model.module import Dataset
from nexus_constructor.model.value_type import ValueTypes

if TYPE_CHECKING:
    from nexus_constructor.model.module import FileWriterModule  # noqa: F401

TRANSFORMS_GROUP_NAME = "transformations"


CHILD_EXCLUDELIST = [TRANSFORMS_GROUP_NAME]


@attr.s
class Group:
    """
    Base class for any group which has a set of children and an nx_class attribute.
    """

    name = attr.ib(type=str)
    parent_node = attr.ib(type="Group", default=None)
    children: List[Union["FileWriterModule", "Group"]] = attr.ib(  # noqa: F821
        factory=list, init=False
    )
    attributes = attr.ib(type=Attributes, factory=Attributes, init=False)
    values = None
    _group_placeholder: bool = False

    def __getitem__(self, key: str):
        return _get_item(self.children, key)

    def row(self) -> int:
        if self.parent_node is None:
            return 0
        return self.parent_node.children.index(self)

    def __setitem__(
        self,
        key: str,
        value: Union["Group", "FileWriterModule"],
    ):
        try:
            value.parent_node = self
        except AttributeError:
            pass
        _set_item(self, self.children, key, value)

    def __contains__(self, item: str):
        result = None
        try:
            result = _get_item(self.children, item)
        except AttributeError:
            pass
        return True if result is not None else False

    def __delitem__(self, key):
        _remove_item(self.children, key)

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False
        return self.absolute_path() == other.absolute_path()

    def has_pixel_shape(self):
        return False

    @property
    def description(self) -> str:
        try:
            return self.get_field_value(CommonAttrs.DESCRIPTION)
        except AttributeError:
            return ""

    @description.setter
    def description(self, new_description: str):
        self.set_field_value(
            CommonAttrs.DESCRIPTION, new_description, ValueTypes.STRING
        )

    def number_of_children(self):
        return len(self.children)

    def tree_depth(self):
        """
        The depth of the tree.
        """
        return self._apply_function_to_tree_structure(max)

    def tree_size(self):
        """
        Number of nodes in the tree structure.
        """
        return self._apply_function_to_tree_structure(sum)

    def _apply_function_to_tree_structure(self, func):
        if not self.children:
            return 1
        else:
            return (
                func(
                    [
                        child._apply_function_to_tree_structure(func)
                        if isinstance(child, Group)
                        else 1
                        for child in self.children
                    ]
                )
                + 1
            )

    @property
    def absolute_path(self):
        return get_absolute_path(self)

    @property
    def group_placeholder(self) -> bool:
        return self._group_placeholder

    @group_placeholder.setter
    def group_placeholder(self, enable: bool):
        self._group_placeholder = enable

    @property
    def nx_class(self):
        return self.attributes.get_attribute_value(CommonAttrs.NX_CLASS)

    @nx_class.setter
    def nx_class(self, new_nx_class: str):
        self.attributes.set_attribute_value(CommonAttrs.NX_CLASS, new_nx_class)

    def set_field_value(self, name: str, value: Any, dtype: str, unit: str = ""):
        self[name] = Dataset(parent_node=self, name=name, type=dtype, values=value)
        if unit:
            self[name].attributes.set_attribute_value(CommonAttrs.UNITS, unit)

    def get_field_value(self, name: str):
        return self[name].values

    def get_field_attribute(self, name: str, attribute: str):
        return self[name].attributes.get_attribute_value(attribute)

    def as_dict(self, error_collector: List[str]) -> Dict[str, Any]:
        if self._group_placeholder and self.nx_class in NX_CLASSES_WITH_PLACEHOLDERS:
            return NX_CLASSES_WITH_PLACEHOLDERS[self.nx_class]  # type: ignore
        return_dict: Dict = {
            CommonKeys.NAME: self.name,
            CommonKeys.TYPE: NodeType.GROUP,
        }
        if self.attributes:
            return_dict[CommonKeys.ATTRIBUTES] = self.attributes.as_dict(
                error_collector
            )
        return_dict[CommonKeys.CHILDREN] = (
            [
                child.as_dict(error_collector)
                for child in self.children
                if name_not_in_excludelist(child)
            ]
            if self.children
            else []
        )
        return return_dict


def name_not_in_excludelist(child: Any):
    if hasattr(child, CommonKeys.NAME) and child.name in CHILD_EXCLUDELIST:
        return False
    return True
