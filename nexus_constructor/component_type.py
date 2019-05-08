from enum import Enum, unique


@unique
class ComponentType(Enum):
    SAMPLE = "Sample"
    DETECTOR = "Detector"
    MONITOR = "Monitor"
    SOURCE = "Source"
    SLIT = "Slit"
    MODERATOR = "Moderator"
    DISK_CHOPPER = "Disk Chopper"

    @classmethod
    def values(cls):
        return [item.value for item in cls]
