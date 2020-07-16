from nexus_constructor.model.transformation import Transformation

TRANSFORM_STR = "/transformations/"


class TransformationsList(list):
    """
    Holds a list of (component) local transformations and, the parent component
    and weather any of the transformations has an external link (depends_on to
    a transformation outside of the current component).
    """

    def __init__(self, parent):
        super().__init__()
        self.parent_component = parent
        from nexus_constructor.component.link_transformation import LinkTransformation

        self.link = LinkTransformation(self)

    def _has_direct_link(self) -> bool:
        try:
            return len(self) == 0 and self.parent_component.depends_on is not None
        except AttributeError:
            return False

    def _transform_has_external_link(self, transformation: Transformation) -> bool:
        try:
            return (
                transformation.depends_on._parent_component
                != transformation._parent_component
            )
        except AttributeError:
            return False

    def _has_indirect_link(self) -> bool:
        for transform in self:
            if self._transform_has_external_link(transform):
                return True
        return False

    @property
    def has_link(self) -> bool:
        try:
            has_link = self.parent_component.has_link
        except AttributeError:
            has_link = self._has_direct_link() or self._has_indirect_link()
            self.parent_component.has_link = has_link
        return has_link

    @has_link.setter
    def has_link(self, value: bool):
        self.parent_component.has_link = value
