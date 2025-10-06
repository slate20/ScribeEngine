"""
SaveData - Base class for serializable game data structures.

This is the foundation for all save/load functionality in Scribe Engine V2.
Developers extend SaveData to create custom data structures that automatically
serialize to/from JSON for save files.

Example:
    @dataclass
    class PlayerSaveData(SaveData):
        health: int = 100
        max_health: int = 100
        position: Vector2 = field(default_factory=Vector2)
        inventory: List[str] = field(default_factory=list)

    # Automatic serialization
    data = PlayerSaveData(health=50, position=Vector2(100, 200))
    json_dict = data.to_dict()
    loaded = PlayerSaveData.from_dict(json_dict)
"""

from dataclasses import dataclass, field, asdict, fields
from typing import Any, Dict, Type, TypeVar
import json

T = TypeVar('T', bound='SaveData')


@dataclass
class SaveData:
    """
    Base class for all saveable data structures.

    Uses Python dataclasses for clean, type-safe data definitions.
    Provides automatic JSON serialization/deserialization.

    All SaveData subclasses automatically support:
    - to_dict() - Convert to JSON-serializable dictionary
    - from_dict() - Restore from dictionary
    - to_json() - Serialize to JSON string
    - from_json() - Restore from JSON string
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this SaveData to a dictionary.

        Returns:
            Dictionary representation (JSON-serializable)
        """
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create SaveData instance from dictionary.

        Args:
            data: Dictionary with field values

        Returns:
            New instance of this SaveData class
        """
        # Filter to only valid fields for this class
        valid_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    def to_json(self, indent: int = 2) -> str:
        """
        Serialize to JSON string.

        Args:
            indent: JSON indentation level (default 2)

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Deserialize from JSON string.

        Args:
            json_str: JSON string to parse

        Returns:
            New instance of this SaveData class
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


# Example SaveData structures that developers can use or extend

@dataclass
class Vector2Data(SaveData):
    """Serializable 2D vector."""
    x: float = 0.0
    y: float = 0.0


@dataclass
class TransformData(SaveData):
    """Serializable transform data (position, rotation, scale)."""
    position: Vector2Data = field(default_factory=Vector2Data)
    rotation: float = 0.0
    scale: Vector2Data = field(default_factory=lambda: Vector2Data(1.0, 1.0))


@dataclass
class ComponentData(SaveData):
    """
    Base class for component save data.

    Components that want custom save data should create a ComponentData subclass.
    """
    component_type: str = ""

    def __post_init__(self):
        """Auto-set component type if not specified."""
        if not self.component_type:
            self.component_type = self.__class__.__name__.replace('Data', '')
