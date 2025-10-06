"""
LogicObject class for Scribe Engine V2.

Non-visual game objects for game logic and systems.
"""

from v2_engine.core.game_object import GameObject
from v2_engine.utils.math import Vector2


class LogicObject(GameObject):
    """
    Non-visual game object for logic, managers, and systems.

    LogicObjects have:
    - Component attachment (inherited from GameObject)
    - Update lifecycle (no runtime rendering)
    - Transform (for editor placement only - not rendered in-game)

    Examples:
    - SpawnPoint (needs position in editor to place spawn location)
    - AudioSource (needs position for 3D audio)
    - TriggerZone (needs position and scale for collision area)
    - GameManager (position not important, but can be placed for organization)
    """

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize logic object.

        Args:
            x: Initial x position (for editor placement)
            y: Initial y position (for editor placement)
        """
        super().__init__()

        # Transform (for editor placement and spatial behaviors)
        # These are used by the editor and some components (AudioSource, SpawnPoint)
        # but LogicObjects don't render at runtime
        self.position = Vector2(x, y)
        self.rotation = 0.0  # degrees (useful for spawn point direction, etc.)
        self.scale = Vector2(1.0, 1.0)  # useful for trigger zone size, audio range, etc.
        self.origin = Vector2(0.5, 0.5)  # origin point for editor gizmos

    # Note: LogicObject inherits update() from GameObject
    # It has no render() method since it's non-visual at runtime
    # Editor will draw gizmos to visualize logic objects during editing
