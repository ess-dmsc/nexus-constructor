from abc import ABC, abstractmethod

from PySide2.Qt3DRender import Qt3DRender


class Mesh(ABC):
    """
    Abstract class for mesh types
    """

    @property
    @abstractmethod
    def mesh(self) -> Qt3DRender.QGeometry:
        pass
