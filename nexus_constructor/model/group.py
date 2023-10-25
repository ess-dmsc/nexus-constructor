from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

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
from nexus_constructor.model.module import Dataset, StreamModules
from nexus_constructor.model.value_type import ValueTypes

if TYPE_CHECKING:
    from nexus_constructor.model.module import FileWriterModule

TRANSFORMS_GROUP_NAME = "transformations"


CHILD_EXCLUDELIST = [TRANSFORMS_GROUP_NAME]


def create_list_of_possible_streams():
    return [module.value for module in StreamModules]


@attr.s
class Group:
    """
    Base class for any group which has a set of children and an nx_class attribute.
    """

    name: str = attr.ib()
    parent_node: Optional["Group"] = attr.ib(default=None)
    children: List[Union["FileWriterModule", "Group"]] = attr.ib(
        factory=list, init=False
    )
    attributes: Attributes = attr.ib(factory=Attributes, init=False)
    values = None
    possible_stream_modules: List[str] = attr.ib(
        default=attr.Factory(create_list_of_possible_streams)
    )
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

    def as_nexus(self, nexus_node, error_collector: List[str]):
        nx_group = nexus_node.create_group(self.name)
        for attribute in self.attributes:
            nx_group.attrs[attribute.name] = attribute.values
        for child in self.children:
            child.as_nexus(nx_group, error_collector)

    def set_possible_stream_modules(self, possible_stream_modules: List[str]):
        self.possible_stream_modules = possible_stream_modules.copy()

    def get_possible_stream_modules(self) -> List[str]:
        return self.possible_stream_modules.copy()

    def add_stream_module(self, module: str):
        if module not in self.possible_stream_modules and module in [
            module.value for module in StreamModules
        ]:
            self._modify_possible_streams(module, self.possible_stream_modules.append)

    def remove_stream_module(self, module: str):
        if module in self.possible_stream_modules:
            self._modify_possible_streams(module, self.possible_stream_modules.remove)

    def _modify_possible_streams(self, module: str, modify_list: Callable):
        if module in [StreamModules.EV42.value, StreamModules.EV44.value]:
            modify_list(StreamModules.EV42.value)
            modify_list(StreamModules.EV44.value)
        elif module in [StreamModules.F142.value, StreamModules.F144.value]:
            modify_list(StreamModules.F142.value)
            modify_list(StreamModules.F144.value)
        elif module in [StreamModules.SENV.value, StreamModules.SE00.value]:
            modify_list(StreamModules.SENV.value)
            modify_list(StreamModules.SE00.value)
        else:
            modify_list(module)


def name_not_in_excludelist(child: Any):
    if hasattr(child, CommonKeys.NAME) and child.name in CHILD_EXCLUDELIST:
        return False
    return True
