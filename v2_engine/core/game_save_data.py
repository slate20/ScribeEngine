"""
GameSaveData - Pre-built SaveData structure for Scribe Engine games.

This is the default save data structure used by the engine's built-in save/load system.
It handles persistent entities, components, global variables, and scene states.

Developers can:
1. Use this as-is for standard games
2. Extend it to add custom fields
3. Create their own SaveData structures from scratch

Example extending GameSaveData:
    @dataclass
    class MyGameSaveData(GameSaveData):
        quest_log: List[str] = field(default_factory=list)
        player_stats: Dict[str, int] = field(default_factory=dict)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

from v2_engine.core.save_data import SaveData, Vector2Data, ComponentData


@dataclass
class EntitySaveData(SaveData):
    """
    Save data for a persistent entity (sprite with components).
    """
    name: str = ""
    position: Vector2Data = field(default_factory=Vector2Data)
    rotation: float = 0.0
    scale: Vector2Data = field(default_factory=lambda: Vector2Data(1.0, 1.0))
    visible: bool = True
    layer: int = 0
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntitySaveData':
        """
        Override to handle nested Vector2Data objects.
        """
        # Convert position and scale dicts to Vector2Data
        position_data = data.get('position', {})
        position = Vector2Data(
            x=position_data.get('x', 0.0),
            y=position_data.get('y', 0.0)
        )

        scale_data = data.get('scale', {})
        scale = Vector2Data(
            x=scale_data.get('x', 1.0),
            y=scale_data.get('y', 1.0)
        )

        return cls(
            name=data.get('name', ''),
            position=position,
            rotation=data.get('rotation', 0.0),
            scale=scale,
            visible=data.get('visible', True),
            layer=data.get('layer', 0),
            components=data.get('components', {})
        )

    @classmethod
    def from_sprite(cls, sprite: 'Sprite') -> 'EntitySaveData':
        """
        Create EntitySaveData from a Sprite instance.

        Args:
            sprite: Sprite to serialize

        Returns:
            EntitySaveData instance
        """
        # Serialize components
        components_data = {}
        for comp_type, component in sprite.components.items():
            if hasattr(component, 'to_dict'):
                components_data[comp_type.__name__] = component.to_dict()

        return cls(
            name=sprite.name,
            position=Vector2Data(sprite.position.x, sprite.position.y),
            rotation=sprite.rotation,
            scale=Vector2Data(sprite.scale.x, sprite.scale.y),
            visible=sprite.visible,
            layer=sprite.layer,
            components=components_data
        )

    def restore_to_sprite(self, sprite: 'Sprite'):
        """
        Restore this save data to a Sprite instance.

        Args:
            sprite: Sprite to restore state to
        """
        # Restore transform
        sprite.position.x = self.position.x
        sprite.position.y = self.position.y
        sprite.rotation = self.rotation
        sprite.scale.x = self.scale.x
        sprite.scale.y = self.scale.y
        sprite.visible = self.visible
        sprite.layer = self.layer

        # Restore components
        for comp_name, comp_data in self.components.items():
            # Find component by name
            for comp_type, component in sprite.components.items():
                if comp_type.__name__ == comp_name and hasattr(component, 'from_dict'):
                    component.from_dict(comp_data)
                    break


@dataclass
class GameStateSaveData(SaveData):
    """
    Complete game state save data.

    This is what gets serialized to save files.
    """
    # Global variables (flags, counters, etc.)
    variables: Dict[str, Any] = field(default_factory=dict)

    # Persistent entities (player, companions, etc.)
    persistent_entities: Dict[str, EntitySaveData] = field(default_factory=dict)

    # Per-scene state (puzzle solutions, opened chests, etc.)
    scene_states: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=dict)

    # Spawn point mappings
    spawn_mappings: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Override to handle nested SaveData objects.
        """
        return {
            'variables': self.variables,
            'persistent_entities': {
                k: v.to_dict() for k, v in self.persistent_entities.items()
            },
            'scene_states': self.scene_states,
            'spawn_mappings': self.spawn_mappings
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateSaveData':
        """
        Override to handle nested SaveData objects.
        """
        # Restore persistent entities
        entities = {}
        for entity_id, entity_data in data.get('persistent_entities', {}).items():
            entities[entity_id] = EntitySaveData.from_dict(entity_data)

        return cls(
            variables=data.get('variables', {}),
            persistent_entities=entities,
            scene_states=data.get('scene_states', {}),
            spawn_mappings=data.get('spawn_mappings', {})
        )


@dataclass
class SaveMetadata(SaveData):
    """
    Metadata for a save slot (shown in save/load menu).
    """
    slot: int = 0
    description: str = ""
    scene_name: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    created_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    playtime: float = 0.0
    version: str = "1.0"


@dataclass
class SaveFile(SaveData):
    """
    Complete save file structure (metadata + game state).

    This is what gets written to slot_N.json files.
    """
    metadata: SaveMetadata = field(default_factory=SaveMetadata)
    game_state: GameStateSaveData = field(default_factory=GameStateSaveData)

    def to_dict(self) -> Dict[str, Any]:
        """Override to handle nested SaveData objects."""
        return {
            'metadata': self.metadata.to_dict(),
            'game_state': self.game_state.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveFile':
        """Override to handle nested SaveData objects."""
        return cls(
            metadata=SaveMetadata.from_dict(data.get('metadata', {})),
            game_state=GameStateSaveData.from_dict(data.get('game_state', {}))
        )
