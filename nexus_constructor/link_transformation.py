from typing import Optional

from nexus_constructor.transformations_list import TransformationsList
from nexus_constructor.model.component import Component

TRANSFORM_STR = "/transformations/"


class LinkTransformation:
    """
    Used for keeping track of links (depends_on) to transformations outside the
    current component and for keeping track of the parent transformation list.
    """

    def __init__(self, parent: TransformationsList):
        super().__init__()
        self.parent = parent

    def _find_linked_component(self) -> Optional[Component]:
        for transformation in self.parent:
            if self.parent._transform_has_external_link(transformation):
                return transformation.depends_on._parent_component
        return None

    def _has_direct_component_link(self) -> bool:
        return self.parent._has_direct_link()

    @property
    def linked_component(self) -> Optional[Component]:
        if not self.parent.has_link:
            return None
        if self._has_direct_component_link():
            return self.parent.parent_component.depends_on._parent_component
        return self._find_linked_component()

    @linked_component.setter
    def linked_component(self, value: Component):
        parent_component = self.parent.parent_component
        target = None
        if len(parent_component.transforms) == 0:
            target = parent_component
        else:
            for c_transform in parent_component.transforms:
                if (
                    c_transform.depends_on is None
                    or c_transform.depends_on != parent_component
                ):
                    target = c_transform
                    break
        if value is not None:
            target.depends_on = value.depends_on
            return
        target.depends_on = None
