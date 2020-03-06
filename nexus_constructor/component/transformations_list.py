from nexus_constructor.transformations import Transformation

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
            and TRANSFORM_STR in self.parent_component.depends_on.absolute_path
        )

    def _transform_has_external_link(self, transformation: Transformation) -> bool:
        if transformation.depends_on is None:
            return False
        return (
            TRANSFORM_STR in transformation.depends_on.absolute_path
            and (self.parent_component.absolute_path + TRANSFORM_STR)
            not in transformation.depends_on.absolute_path
        )

    def _has_indirect_link(self) -> bool:
        for transform in self:
            if self._transform_has_external_link(transform):
                return True
        return False

    @property
    def has_link(self) -> bool:
        has_link_value = self.parent_component.file.get_attribute_value(
            self.parent_component.group, LINK_STR
        )
        if has_link_value is None:
            has_link_value = self._has_direct_link() or self._has_indirect_link()
            self.parent_component.file.set_attribute_value(
                self.parent_component.group, LINK_STR, has_link_value
            )
        return bool(has_link_value)

    @has_link.setter
    def has_link(self, value: bool):
        self.parent_component.file.set_attribute_value(
            self.parent_component.group, LINK_STR, value
        )
