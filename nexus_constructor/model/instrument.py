from nexus_constructor.model.group import Group


class Instrument(Group):
    def __init__(self):
        self.nx_class = "NXinstrument"
