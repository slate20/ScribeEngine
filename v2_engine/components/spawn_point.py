"""
Spawn Point Component

Marks locations where persistent entities should spawn when entering a scene.
"""

from v2_engine.components.component import Component


class SpawnPoint(Component):
    """
    Defines where persistent entities spawn when entering a scene.

    Usage:
    1. Create invisible sprite at spawn location
    2. Add SpawnPoint component
    3. Set spawn_id (e.g., "player_start", "from_dungeon", "checkpoint_1")
    4. Persistent entities with matching spawn mapping will appear here

    Example:
        - Scene A has SpawnPoint with spawn_id="from_level_1"
        - Player transitions from Level 1 → Level 2
        - Scene transition specifies target_spawn="from_level_1"
        - Player spawns at SpawnPoint location
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Gameplay',
        'description': 'Defines spawn locations for persistent entities',
        'icon': '📍',
        'properties_info': {
            'spawn_id': 'Unique identifier for this spawn point (e.g., "default", "from_level_1")'
        }
    }

    def __init__(self, sprite: 'Sprite'):
        """
        Initialize spawn point.

        Args:
            sprite: The sprite this component is attached to
        """
        super().__init__(sprite)

        # Unique ID for this spawn point
        self.spawn_id = "default"

        # Which entities should spawn here (comma-separated IDs)
        # Example: "player" or "player,companion" or "*" (all persistent entities)
        self.spawn_entities = "player"

        # Whether to activate on scene enter
        self.active_on_enter = True

        # Visual indicator in editor (not rendered in game)
        self.show_gizmo = True

    def update(self, dt: float):
        """Update spawn point (no runtime behavior)."""
        # Spawn points are passive - they just mark locations
        # The scene manager handles spawning logic
        pass

    def on_scene_enter(self):
        """
        Called when scene becomes active.

        Spawns registered persistent entities at this location.
        """
        if not self.active_on_enter:
            return

        from v2_engine.core.game_state import get_game_state
        game_state = get_game_state()

        # Get entities that should spawn here
        if self.spawn_entities == "*":
            # Spawn all persistent entities
            entity_ids = list(game_state.persistent_entities.keys())
        else:
            # Parse comma-separated list
            entity_ids = [e.strip() for e in self.spawn_entities.split(',')]

        # Position entities at spawn point
        for entity_id in entity_ids:
            entity = game_state.get_persistent_entity(entity_id)
            if entity:
                # Move entity to spawn location (default position)
                entity.position.x = self.sprite.position.x
                entity.position.y = self.sprite.position.y
                print(f"[SpawnPoint] Spawned '{entity_id}' at {self.spawn_id} ({entity.position.x}, {entity.position.y})")

                # Add to scene if not already present
                scene = getattr(self.sprite, 'scene', None)
                if scene and hasattr(scene, 'sprite_groups'):
                    # Check if entity is already in scene
                    found = False
                    for group in scene.sprite_groups.values():
                        if entity in group.sprites:
                            found = True
                            break

                    # Add to 'all' group if not found
                    if not found and 'all' in scene.sprite_groups:
                        scene.sprite_groups['all'].add(entity)
                        entity.scene = scene
                        # Mark entity as spawned (not original to this scene)
                        entity._spawned_by_spawn_point = True
                        print(f"[SpawnPoint] Added '{entity_id}' to scene")

                # Restore saved state if available (from loaded save)
                # This will override spawn position with saved position
                game_state.restore_persistent_entity_state(entity_id, entity)

    def get_spawn_position(self):
        """
        Get the spawn position in world coordinates.

        Returns:
            Vector2 position
        """
        return self.sprite.position.copy() if hasattr(self.sprite.position, 'copy') else self.sprite.position

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'spawn_id': self.spawn_id,
            'spawn_entities': self.spawn_entities,
            'active_on_enter': self.active_on_enter,
            'show_gizmo': self.show_gizmo
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'spawn_id' in data:
            self.spawn_id = data['spawn_id']
        if 'spawn_entities' in data:
            self.spawn_entities = data['spawn_entities']
        if 'active_on_enter' in data:
            self.active_on_enter = data['active_on_enter']
        if 'show_gizmo' in data:
            self.show_gizmo = data['show_gizmo']
