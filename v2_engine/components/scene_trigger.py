"""
SceneTrigger component for scene transitions.
"""

from v2_engine.components.component import Component
from v2_engine.components.box_collider import BoxCollider


class SceneTrigger(Component):
    """
    Component that triggers scene transitions when another sprite enters its area.

    Requires: BoxCollider component (set as trigger).
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Interaction',
        'description': 'Trigger scene transitions when entered',
        'icon': '🚪',
        'properties_info': {
            'target_scene': 'Name of scene to load on trigger',
            'trigger_tag': 'Only trigger for objects with this name',
            'trigger_once': 'Disable after first trigger',
            'spawn_point': 'Spawn point name in target scene'
        }
    }

    def __init__(self, sprite):
        """
        Initialize scene trigger.

        Args:
            sprite: Sprite this component is attached to
        """
        super().__init__(sprite)

        # Trigger settings
        self.target_scene = ""  # Name of scene to load
        self.trigger_tag = "Player"  # Only trigger for sprites with this name/tag
        self.trigger_once = False  # If True, only triggers once then disables
        self.has_triggered = False  # Internal state for trigger_once

        # Transition settings
        self.spawn_point = "default"  # Spawn point name in target scene (future feature)

    def update(self, dt: float):
        """
        Check for trigger conditions.

        Args:
            dt: Delta time in seconds
        """
        # Skip if already triggered (when trigger_once is enabled)
        if self.trigger_once and self.has_triggered:
            return

        # Skip if no target scene set
        if not self.target_scene:
            return

        # Get box collider (must be set as trigger)
        collider = self.sprite.get_component(BoxCollider)
        if not collider or not collider.is_trigger:
            return

        # Check if any colliding sprite matches the trigger tag
        for other_sprite in collider.colliding_with:
            # Check if sprite matches trigger tag
            if hasattr(other_sprite, 'name') and other_sprite.name == self.trigger_tag:
                self._trigger_scene_change()
                break

    def _trigger_scene_change(self):
        """Execute the scene transition."""
        # Mark as triggered if using trigger_once
        if self.trigger_once:
            self.has_triggered = True

        # Get scene reference
        if not hasattr(self.sprite, 'scene') or not self.sprite.scene:
            print("[SceneTrigger] Error: No scene reference")
            return

        scene = self.sprite.scene

        # Get game reference
        if not hasattr(scene, 'game') or not scene.game:
            print("[SceneTrigger] Error: No game reference")
            return

        game = scene.game

        # Trigger scene change via scene manager
        if hasattr(game, 'scene_manager') and game.scene_manager:
            print(f"[SceneTrigger] Changing scene to: {self.target_scene}")
            game.scene_manager.change_scene(self.target_scene)
        else:
            print("[SceneTrigger] Error: No scene manager found")

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'target_scene': self.target_scene,
            'trigger_tag': self.trigger_tag,
            'trigger_once': self.trigger_once,
            'has_triggered': self.has_triggered,
            'spawn_point': self.spawn_point
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'target_scene' in data:
            self.target_scene = data['target_scene']
        if 'trigger_tag' in data:
            self.trigger_tag = data['trigger_tag']
        if 'trigger_once' in data:
            self.trigger_once = data['trigger_once']
        if 'has_triggered' in data:
            self.has_triggered = data['has_triggered']
        if 'spawn_point' in data:
            self.spawn_point = data['spawn_point']
