"""
CameraFollow component for smooth camera tracking.

Attaches to sprites to make the scene camera follow them.
"""

from v2_engine.components.component import Component
from v2_engine.utils.math import Vector2


class CameraFollow(Component):
    """
    Makes the scene camera follow this sprite.

    Properties:
        smoothness: How quickly camera catches up (0-1, where 1 = instant, 0.1 = smooth)
        offset: Camera offset from sprite position (X, Y in world units)
        deadzone: Minimum distance sprite must move before camera follows
        enabled: Whether camera follow is active
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Gameplay',
        'description': 'Smooth camera tracking for player or objects',
        'icon': '📷',
        'properties_info': {
            'smoothness': 'Camera tracking speed (1.0 = instant, 0.1 = smooth)',
            'offset': 'Camera offset from sprite position',
            'deadzone': 'Minimum movement distance before camera follows'
        }
    }

    def __init__(self, sprite: 'Sprite'):
        """
        Initialize CameraFollow component.

        Args:
            sprite: The sprite to attach to (camera will follow this sprite)
        """
        super().__init__(sprite)

        # Camera follow settings
        self.smoothness = 0.1  # Lower = smoother, higher = more responsive
        self.offset = Vector2(0, 0)  # Offset from sprite position
        self.deadzone = 0.0  # Minimum movement before camera follows (0 = always follow)

        # Internal state
        self._last_camera_pos = None

    def update(self, dt: float):
        """
        Update camera position to follow sprite.

        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return

        # Get scene and camera
        scene = getattr(self.sprite, 'scene', None)
        if not scene or not scene.camera:
            return

        camera = scene.camera

        # Calculate target camera position (sprite position + offset)
        target_pos = Vector2(
            self.sprite.position.x + self.offset.x,
            self.sprite.position.y + self.offset.y
        )

        # Initialize last camera position if first frame
        if self._last_camera_pos is None:
            self._last_camera_pos = Vector2(camera.position.x, camera.position.y)

        # Calculate distance from current camera position to target
        if self.deadzone > 0:
            distance = Vector2(
                target_pos.x - camera.position.x,
                target_pos.y - camera.position.y
            )
            distance_magnitude = (distance.x ** 2 + distance.y ** 2) ** 0.5

            # Only move camera if outside deadzone
            if distance_magnitude > self.deadzone:
                # Move camera toward target
                camera.follow(target_pos, self.smoothness)
        else:
            # No deadzone - always follow
            camera.follow(target_pos, self.smoothness)

        # Update last camera position
        self._last_camera_pos = Vector2(camera.position.x, camera.position.y)

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'smoothness': self.smoothness,
            'offset': {'x': self.offset.x, 'y': self.offset.y},
            'deadzone': self.deadzone
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'smoothness' in data:
            self.smoothness = data['smoothness']
        if 'offset' in data:
            self.offset.x = data['offset']['x']
            self.offset.y = data['offset']['y']
        if 'deadzone' in data:
            self.deadzone = data['deadzone']
