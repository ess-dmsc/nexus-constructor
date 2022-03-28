from typing import Optional

from nexus_constructor.model.component import Component
from nexus_constructor.model.group import Group
from nexus_constructor.transformations_list import TransformationsList


class LinkTransformation:
    """
    Used for keeping track of links (depends_on) to transformations outside the
    current component and for keeping track of the parent transformation list
    Not a "link" in the NeXus/HDF5 sense
    """

    def __init__(self, parent: TransformationsList):
        super().__init__()
        self.parent = parent
        self.parent_node: Group = (
            None  # This will always be an NXtransformations group.
        )

    def _find_linked_component(self) -> Optional[Component]:
        for transformation in self.parent:
            if self.parent._transform_has_external_link(transformation):
                return transformation.depends_on.parent_component
        return None

    def _has_direct_component_link(self) -> bool:
        return self.parent._has_direct_link()

    @property
    def linked_component(self) -> Optional[Component]:
        if not self.parent.has_link:
            return None
        if self._has_direct_component_link():
            return self.parent.parent_component.depends_on.parent_component
        return self._find_linked_component()

    @linked_component.setter
    def linked_component(self, value: Component):
        parent_component = self.parent.parent_component
        if len(parent_component.transforms) == 0:
            target = parent_component
        else:
            # The last transform of the parent component will now depend on the
            # transform that the value component depends on
            target = parent_component.transforms[-1]
        if value is not None:
            target.depends_on = value.depends_on
            return
        target.depends_on = None
