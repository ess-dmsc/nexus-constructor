from nexus_constructor.component.component import Component
from nexus_constructor.component.transformations_list import TransformationsList

TRANSFORM_STR = "/transformations/"

class LinkTransformation:
    """
    Used for keeping track of links (depends_on) to transformations outside the
    current component and for keeping track of the parent transformation list.
    """
    def __init__(self, parent: TransformationsList):
        super().__init__()
        self.parent = parent

    def _find_linked_component(self) -> Component:
        for transformation in self.parent:
            if self.parent._transform_has_external_link(transformation):
                component_path = transformation.depends_on.absolute_path[
                                 : transformation.depends_on.absolute_path.find(TRANSFORM_STR)
                                 ]
                return Component(
                    self.parent.parent_component.file,
                    self.parent.parent_component.file.nexus_file[component_path],
                )
        return None

    def _has_direct_component_link(self) -> bool:
        return self.parent._has_direct_link()

    @property
    def linked_component(self) -> Component:
        if not self.parent.has_link:
            return None
        if self._has_direct_component_link():
            component_path = self.parent.parent_component.depends_on.absolute_path[
                : self.parent.parent_component.depends_on.absolute_path.find(
                    TRANSFORM_STR
                )
            ]
            return Component(
                self.parent.parent_component.file,
                self.parent.parent_component.file.nexus_file[component_path],
            )
        return self._find_linked_component()

    @linked_component.setter
    def linked_component(self, value):
        parent_component = self.parent.parent_component
        target = None
        if len(parent_component.transforms) == 0:
            target = parent_component
        else:
            for c_transform in parent_component.transforms:
                if (
                    parent_component.absolute_path + TRANSFORM_STR
                    not in c_transform.depends_on.absolute_path
                ):
                    target = c_transform
                    break
        if value is not None:
            target.depends_on = value.depends_on
            return
        target.depends_on = None