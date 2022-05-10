from .module import StreamModule


class ModuleContainer:
    def __init__(self, module: StreamModule):
        self._module = module

    @property
    def module(self) -> StreamModule:
        return self._module

    @module.setter
    def module(self, new_module: StreamModule):
        self._module = new_module
