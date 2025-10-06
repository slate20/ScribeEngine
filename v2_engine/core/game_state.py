"""
Game State Management System

Centralized system for managing:
- Global variables (score, flags, quest progress)
- Persistent entities (survive scene transitions)
- Scene-specific state (opened chests, destroyed objects)
"""

import json
from typing import Any, Dict, Optional, Set


class GameState:
    """
    Singleton for managing global game state.

    Handles:
    - Global variables accessible from anywhere
    - Persistent entities that survive scene changes
    - Per-scene object states
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one GameState instance exists."""
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize game state (only runs once due to singleton)."""
        if self._initialized:
            return

        # Global variables (any game data)
        self.variables: Dict[str, Any] = {}

        # Persistent entities (survive scene transitions)
        # Maps entity_id -> sprite instance
        self.persistent_entities: Dict[str, 'Sprite'] = {}

        # Scene-specific state (per-scene object states)
        # Maps scene_name -> object_id -> state_dict
        self.scene_states: Dict[str, Dict[str, Dict[str, Any]]] = {}

        # Track which entities should spawn at which points
        # Maps spawn_point_id -> set of entity_ids
        self.spawn_mappings: Dict[str, Set[str]] = {}

        self._initialized = True
        print("[GameState] Initialized")

    # ===== Variable Management =====

    def set_var(self, name: str, value: Any):
        """
        Set a global variable.

        Args:
            name: Variable name (e.g., "score", "quest_1_complete")
            value: Any JSON-serializable value
        """
        self.variables[name] = value
        print(f"[GameState] Set variable: {name} = {value}")

    def get_var(self, name: str, default: Any = None) -> Any:
        """
        Get a global variable.

        Args:
            name: Variable name
            default: Value to return if variable doesn't exist

        Returns:
            Variable value or default
        """
        return self.variables.get(name, default)

    def has_var(self, name: str) -> bool:
        """
        Check if a variable exists.

        Args:
            name: Variable name

        Returns:
            True if variable exists
        """
        return name in self.variables

    def delete_var(self, name: str):
        """
        Delete a variable.

        Args:
            name: Variable name
        """
        if name in self.variables:
            del self.variables[name]
            print(f"[GameState] Deleted variable: {name}")

    def increment(self, name: str, amount: float = 1):
        """
        Increment a numeric variable.

        Args:
            name: Variable name
            amount: Amount to add (default 1)
        """
        current = self.get_var(name, 0)
        if isinstance(current, (int, float)):
            self.set_var(name, current + amount)
        else:
            print(f"[GameState] Warning: Cannot increment non-numeric variable '{name}'")

    def toggle(self, name: str):
        """
        Toggle a boolean variable.

        Args:
            name: Variable name
        """
        current = self.get_var(name, False)
        self.set_var(name, not current)

    # ===== Persistent Entity Management =====

    def register_persistent(self, sprite: 'Sprite', entity_id: Optional[str] = None, home_scene: Optional[str] = None):
        """
        Mark a sprite as persistent (survives scene transitions).

        Args:
            sprite: Sprite to make persistent
            entity_id: Unique ID (defaults to sprite.name or generates one)
            home_scene: Name of the scene this entity belongs to (for editor tracking)
        """
        if entity_id is None:
            # Use sprite name or generate ID
            entity_id = getattr(sprite, 'name', None) or f"entity_{id(sprite)}"

        sprite.is_persistent = True
        sprite.entity_id = entity_id

        # Track home scene for editor purposes
        if home_scene and not hasattr(sprite, '_home_scene'):
            sprite._home_scene = home_scene

        self.persistent_entities[entity_id] = sprite

        print(f"[GameState] Registered persistent entity: {entity_id}")

    def unregister_persistent(self, entity_id: str):
        """
        Remove entity from persistence (can be destroyed normally).

        Args:
            entity_id: ID of entity to remove
        """
        if entity_id in self.persistent_entities:
            sprite = self.persistent_entities[entity_id]
            sprite.is_persistent = False
            del self.persistent_entities[entity_id]
            print(f"[GameState] Unregistered persistent entity: {entity_id}")

    def get_persistent_entity(self, entity_id: str) -> Optional['Sprite']:
        """
        Get a persistent entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Sprite instance or None
        """
        return self.persistent_entities.get(entity_id)

    def has_persistent_entity(self, entity_id: str) -> bool:
        """
        Check if an entity is registered as persistent.

        Args:
            entity_id: Entity ID

        Returns:
            True if entity exists and is persistent
        """
        return entity_id in self.persistent_entities

    # ===== Scene State Management =====

    def set_scene_state(self, scene_name: str, object_id: str, key: str, value: Any):
        """
        Set state for a specific object in a scene.

        Args:
            scene_name: Name of the scene
            object_id: Unique ID for the object
            key: State key (e.g., "opened", "destroyed")
            value: State value
        """
        if scene_name not in self.scene_states:
            self.scene_states[scene_name] = {}

        if object_id not in self.scene_states[scene_name]:
            self.scene_states[scene_name][object_id] = {}

        self.scene_states[scene_name][object_id][key] = value
        print(f"[GameState] Set scene state: {scene_name}.{object_id}.{key} = {value}")

    def get_scene_state(self, scene_name: str, object_id: str, key: str, default: Any = None) -> Any:
        """
        Get state for a specific object in a scene.

        Args:
            scene_name: Name of the scene
            object_id: Unique ID for the object
            key: State key
            default: Default value if not found

        Returns:
            State value or default
        """
        if scene_name not in self.scene_states:
            return default

        if object_id not in self.scene_states[scene_name]:
            return default

        return self.scene_states[scene_name][object_id].get(key, default)

    def has_scene_state(self, scene_name: str, object_id: str, key: str) -> bool:
        """
        Check if scene state exists.

        Args:
            scene_name: Name of the scene
            object_id: Unique ID for the object
            key: State key

        Returns:
            True if state exists
        """
        if scene_name not in self.scene_states:
            return False

        if object_id not in self.scene_states[scene_name]:
            return False

        return key in self.scene_states[scene_name][object_id]

    def clear_scene_state(self, scene_name: str):
        """
        Clear all state for a scene (useful for resetting levels).

        Args:
            scene_name: Name of the scene to clear
        """
        if scene_name in self.scene_states:
            del self.scene_states[scene_name]
            print(f"[GameState] Cleared scene state: {scene_name}")

    # ===== Spawn Point Management =====

    def register_spawn_mapping(self, spawn_point_id: str, entity_id: str):
        """
        Register which entities should spawn at which spawn points.

        Args:
            spawn_point_id: ID of spawn point (e.g., "player_start", "from_level_1")
            entity_id: ID of entity that spawns here
        """
        if spawn_point_id not in self.spawn_mappings:
            self.spawn_mappings[spawn_point_id] = set()

        self.spawn_mappings[spawn_point_id].add(entity_id)
        print(f"[GameState] Registered spawn mapping: {entity_id} -> {spawn_point_id}")

    def get_spawn_entities(self, spawn_point_id: str) -> Set[str]:
        """
        Get entities that should spawn at a given spawn point.

        Args:
            spawn_point_id: Spawn point ID

        Returns:
            Set of entity IDs
        """
        return self.spawn_mappings.get(spawn_point_id, set())

    # ===== Serialization =====

    def to_dict(self) -> dict:
        """
        Serialize game state to dictionary using SaveData system.

        Returns:
            Dictionary representation of game state
        """
        from v2_engine.core.game_save_data import EntitySaveData

        # Serialize persistent entities using EntitySaveData
        persistent_entity_states = {}
        for entity_id, sprite in self.persistent_entities.items():
            try:
                entity_save_data = EntitySaveData.from_sprite(sprite)
                persistent_entity_states[entity_id] = entity_save_data.to_dict()
            except Exception as e:
                print(f"[GameState] Warning: Failed to serialize entity {entity_id}: {e}")

        return {
            'variables': self.variables,
            'persistent_entities': persistent_entity_states,
            'scene_states': self.scene_states,
            'spawn_mappings': {k: list(v) for k, v in self.spawn_mappings.items()}
        }

    def from_dict(self, data: dict):
        """
        Restore game state from dictionary using SaveData system.

        Args:
            data: Dictionary from to_dict()
        """
        from v2_engine.core.game_save_data import EntitySaveData

        self.variables = data.get('variables', {})
        self.scene_states = data.get('scene_states', {})

        spawn_mappings = data.get('spawn_mappings', {})
        self.spawn_mappings = {k: set(v) for k, v in spawn_mappings.items()}

        # Store EntitySaveData for restoration when entities spawn
        persistent_entity_dicts = data.get('persistent_entities', {})
        self._pending_entity_states = {}
        for entity_id, entity_dict in persistent_entity_dicts.items():
            self._pending_entity_states[entity_id] = EntitySaveData.from_dict(entity_dict)

        print("[GameState] Restored from save data")

    def reset(self):
        """Reset game state to initial conditions."""
        self.variables.clear()
        self.persistent_entities.clear()
        self.scene_states.clear()
        self.spawn_mappings.clear()
        print("[GameState] Reset to initial state")

    # ===== Save/Load System =====

    def save_to_file(self, slot: int, scene_name: str, description: str = "", project_path: str = None):
        """
        Save complete game state to a save slot file using SaveData system.

        Args:
            slot: Save slot number (0-5)
            scene_name: Current scene name
            description: User description for this save
            project_path: Project directory path (for saves folder)

        Returns:
            dict: Save metadata on success, None on failure
        """
        import os
        from datetime import datetime
        from v2_engine.core.game_save_data import SaveFile, SaveMetadata, GameStateSaveData, EntitySaveData

        if project_path is None:
            print("[GameState] Error: project_path required for saving")
            return None

        # Create saves directory
        saves_dir = os.path.join(project_path, 'saves')
        os.makedirs(saves_dir, exist_ok=True)

        # Load existing save to preserve creation timestamp
        existing_meta = self.get_save_metadata(slot, project_path)
        created_timestamp = existing_meta.get('created_timestamp') if existing_meta else datetime.now().isoformat()

        # Calculate playtime (rough estimate - would need proper tracking in Game class)
        playtime = existing_meta.get('playtime', 0) if existing_meta else 0

        # Create metadata
        metadata = SaveMetadata(
            slot=slot,
            description=description,
            scene_name=scene_name,
            timestamp=datetime.now().isoformat(),
            created_timestamp=created_timestamp,
            playtime=playtime,
            version='1.0'
        )

        # Serialize persistent entities using EntitySaveData
        persistent_entities = {}
        for entity_id, sprite in self.persistent_entities.items():
            try:
                persistent_entities[entity_id] = EntitySaveData.from_sprite(sprite)
            except Exception as e:
                print(f"[GameState] Warning: Failed to serialize entity {entity_id}: {e}")

        # Create GameStateSaveData
        game_state_data = GameStateSaveData(
            variables=self.variables,
            persistent_entities=persistent_entities,
            scene_states=self.scene_states,
            spawn_mappings={k: list(v) for k, v in self.spawn_mappings.items()}
        )

        # Create complete SaveFile
        save_file = SaveFile(
            metadata=metadata,
            game_state=game_state_data
        )

        # Save to file using SaveData's to_json()
        save_path = os.path.join(saves_dir, f'slot_{slot}.json')
        try:
            with open(save_path, 'w') as f:
                f.write(save_file.to_json())
            print(f"[GameState] Saved to slot {slot}: {save_path}")
            return metadata.to_dict()
        except Exception as e:
            print(f"[GameState] Save failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_from_file(self, slot: int, project_path: str = None) -> bool:
        """
        Load game state from a save slot file using SaveData system.

        Args:
            slot: Save slot number (0-5)
            project_path: Project directory path (for saves folder)

        Returns:
            bool: True if load successful, False otherwise
        """
        import os
        from v2_engine.core.game_save_data import SaveFile

        if project_path is None:
            print("[GameState] Error: project_path required for loading")
            return False

        save_path = os.path.join(project_path, 'saves', f'slot_{slot}.json')

        if not os.path.exists(save_path):
            print(f"[GameState] No save file in slot {slot}")
            return False

        try:
            # Load save file using SaveData
            with open(save_path, 'r') as f:
                json_str = f.read()

            save_file = SaveFile.from_json(json_str)

            # Restore variables and scene states
            self.variables = save_file.game_state.variables
            self.scene_states = save_file.game_state.scene_states

            # Restore spawn mappings
            self.spawn_mappings = {k: set(v) for k, v in save_file.game_state.spawn_mappings.items()}

            # Note: Persistent entities will be restored when scene loads
            # Store their EntitySaveData for restoration
            self._pending_entity_states = save_file.game_state.persistent_entities

            print(f"[GameState] Loaded from slot {slot}")
            return True

        except Exception as e:
            print(f"[GameState] Load failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_save_metadata(self, slot: int, project_path: str = None) -> Dict[str, Any]:
        """
        Get save metadata without loading full state using SaveData system.

        Args:
            slot: Save slot number (0-5)
            project_path: Project directory path

        Returns:
            dict: Save metadata or empty dict if no save exists
        """
        import os
        from v2_engine.core.game_save_data import SaveFile

        if project_path is None:
            return {}

        save_path = os.path.join(project_path, 'saves', f'slot_{slot}.json')

        if not os.path.exists(save_path):
            return {}

        try:
            with open(save_path, 'r') as f:
                json_str = f.read()
            save_file = SaveFile.from_json(json_str)
            return save_file.metadata.to_dict()
        except Exception as e:
            print(f"[GameState] Failed to read metadata for slot {slot}: {e}")
            return {}

    def delete_save(self, slot: int, project_path: str = None) -> bool:
        """
        Delete a save file.

        Args:
            slot: Save slot number (0-5)
            project_path: Project directory path

        Returns:
            bool: True if deleted successfully
        """
        import os

        if project_path is None:
            return False

        save_path = os.path.join(project_path, 'saves', f'slot_{slot}.json')

        if os.path.exists(save_path):
            try:
                os.remove(save_path)
                print(f"[GameState] Deleted save slot {slot}")
                return True
            except Exception as e:
                print(f"[GameState] Failed to delete slot {slot}: {e}")
                return False
        return False

    def export_save(self, slot: int, export_path: str, project_path: str = None) -> bool:
        """
        Export a save file to external location.

        Args:
            slot: Save slot number (0-5)
            export_path: Destination file path
            project_path: Project directory path

        Returns:
            bool: True if exported successfully
        """
        import os
        import shutil

        if project_path is None:
            return False

        save_path = os.path.join(project_path, 'saves', f'slot_{slot}.json')

        if not os.path.exists(save_path):
            print(f"[GameState] No save in slot {slot} to export")
            return False

        try:
            shutil.copy(save_path, export_path)
            print(f"[GameState] Exported slot {slot} to {export_path}")
            return True
        except Exception as e:
            print(f"[GameState] Export failed: {e}")
            return False

    def import_save(self, import_path: str, slot: int, project_path: str = None) -> bool:
        """
        Import a save file from external location.

        Args:
            import_path: Source file path
            slot: Destination save slot number (0-5)
            project_path: Project directory path

        Returns:
            bool: True if imported successfully
        """
        import os
        import shutil

        if project_path is None:
            return False

        if not os.path.exists(import_path):
            print(f"[GameState] Import file not found: {import_path}")
            return False

        # Validate it's a valid save file
        try:
            with open(import_path, 'r') as f:
                save_data = json.load(f)
            if 'metadata' not in save_data or 'game_state' not in save_data:
                print(f"[GameState] Invalid save file format")
                return False
        except Exception as e:
            print(f"[GameState] Failed to validate import file: {e}")
            return False

        # Create saves directory
        saves_dir = os.path.join(project_path, 'saves')
        os.makedirs(saves_dir, exist_ok=True)

        # Copy to slot
        save_path = os.path.join(saves_dir, f'slot_{slot}.json')
        try:
            shutil.copy(import_path, save_path)
            print(f"[GameState] Imported to slot {slot}")
            return True
        except Exception as e:
            print(f"[GameState] Import failed: {e}")
            return False

    def restore_persistent_entity_state(self, entity_id: str, sprite: 'Sprite'):
        """
        Restore saved state to a persistent entity using EntitySaveData.

        Args:
            entity_id: Entity ID
            sprite: Sprite instance to restore state to
        """
        from v2_engine.core.game_save_data import EntitySaveData

        if not hasattr(self, '_pending_entity_states'):
            return

        if entity_id not in self._pending_entity_states:
            return

        # Get EntitySaveData for this entity
        entity_save_data = self._pending_entity_states[entity_id]

        # Use EntitySaveData's restore method
        entity_save_data.restore_to_sprite(sprite)

        print(f"[GameState] Restored state for entity: {entity_id}")

    # ===== Debug =====

    def dump_state(self):
        """Print current game state (for debugging)."""
        print("\n===== Game State =====")
        print(f"Variables ({len(self.variables)}):")
        for key, value in self.variables.items():
            print(f"  {key} = {value}")

        print(f"\nPersistent Entities ({len(self.persistent_entities)}):")
        for entity_id in self.persistent_entities.keys():
            print(f"  {entity_id}")

        print(f"\nScene States ({len(self.scene_states)} scenes):")
        for scene_name, states in self.scene_states.items():
            print(f"  {scene_name}: {len(states)} objects")

        print("======================\n")


# Global accessor function for convenience
def get_game_state() -> GameState:
    """Get the global GameState instance."""
    return GameState()
