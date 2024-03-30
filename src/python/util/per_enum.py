from enum import Enum, auto


class ArchType(Enum):
    """
    Enumeration for architecture types.
    """
    MESH: int = auto()
    """
    Mesh architecture type.
    """
    ONE_HOP: int = auto()
    """
    One-hop architecture type.
    """
