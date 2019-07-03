from nexus_constructor.axes import Axes


class InstrumentViewAxes(Axes):
    def __init__(self, component_root_entity, far_plane, component_adder):

        super().__init__(component_root_entity, component_adder)

        self.cylinder_length = far_plane
        self.cylinder_radius = 0.01
