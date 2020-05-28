from nexus_constructor.model.transformation import Transformation

TRANSFORM_STR = "/transformations/"
LINK_STR = "has_link"


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
        return (
            len(self) == 0
            and self.parent_component.depends_on is not None
            and TRANSFORM_STR in self.parent_component.depends_on
        )

    def _transform_has_external_link(self, transformation: Transformation) -> bool:
        if transformation.depends_on is None:
            return False
        return (
            TRANSFORM_STR in transformation.depends_on
            and self.parent_component != transformation.depends_on
        )

    def _has_indirect_link(self) -> bool:
        for transform in self:
            if self._transform_has_external_link(transform):
                return True
        return False

    @property
    def has_link(self) -> bool:
        try:
            return self[-1].depends_on is not None
        except IndexError:
            return False

    @has_link.setter
    def has_link(self, value: bool):
        self.parent_component.set_attribute_value(LINK_STR, value)
