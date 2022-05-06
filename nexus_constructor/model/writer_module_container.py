from .module import FileWriterModule


class ModuleContainer:
    def __init__(self, module: FileWriterModule):
        self._module = module

    @property
    def module(self) -> FileWriterModule:
        return self.module

    @module.setter
    def group(self, new_module: FileWriterModule):
        self._module = new_module
