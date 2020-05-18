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

    @property
    def has_link(self) -> bool:
        try:
            return self[-1].depends_on is not None
        except IndexError:
            return False
