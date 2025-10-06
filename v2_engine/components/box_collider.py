"""
BoxCollider component for 2D collision detection.
"""

from v2_engine.components.component import Component
import pygame


class BoxCollider(Component):
    """
    Component that adds a rectangular collision box to a sprite.

    Provides AABB (Axis-Aligned Bounding Box) collision detection.
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Physics',
        'description': 'AABB collision detection and response',
        'icon': '📦',
        'properties_info': {
            'width': 'Box width (0 = auto from sprite)',
            'height': 'Box height (0 = auto from sprite)',
            'is_trigger': 'Detect collisions without physical response',
            'layer': 'Collision layer for filtering',
            'offset_x': 'Horizontal offset from sprite position',
            'offset_y': 'Vertical offset from sprite position'
        }
    }

    def __init__(self, sprite):
        """
        Initialize box collider.

        Args:
            sprite: Sprite this component is attached to
        """
        super().__init__(sprite)

        # Collision box size (relative to sprite image if not set)
        self.width = 0  # 0 = auto-detect from sprite image
        self.height = 0  # 0 = auto-detect from sprite image

        # Offset from sprite position
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Collision properties
        self.is_trigger = False  # If True, detects collisions but no physical response
        self.layer = 0  # Collision layer for filtering

        # Collision state (updated by collision system)
        self.colliding_with = []  # List of sprites currently colliding with

    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle in world space.

        Returns:
            pygame.Rect representing collision bounds
        """
        # Auto-detect size from sprite image if not explicitly set
        if self.width == 0 or self.height == 0:
            if hasattr(self.sprite, 'image') and self.sprite.image:
                width = self.sprite.image.get_width() * self.sprite.scale.x
                height = self.sprite.image.get_height() * self.sprite.scale.y
            else:
                width = 32  # Default size
                height = 32
        else:
            width = self.width
            height = self.height

        # Calculate position using sprite's origin point
        sprite_rect = self.sprite.get_rect()

        # Apply offset
        x = sprite_rect.x + self.offset_x
        y = sprite_rect.y + self.offset_y

        return pygame.Rect(x, y, width, height)

    def check_collision(self, other: 'BoxCollider') -> bool:
        """
        Check if this collider overlaps with another collider.

        Args:
            other: Another BoxCollider to check against

        Returns:
            True if colliding
        """
        rect1 = self.get_rect()
        rect2 = other.get_rect()

        return rect1.colliderect(rect2)

    def get_overlap(self, other: 'BoxCollider') -> tuple:
        """
        Get the overlap distance with another collider.

        Args:
            other: Another BoxCollider

        Returns:
            Tuple of (overlap_x, overlap_y) - positive means overlapping
        """
        rect1 = self.get_rect()
        rect2 = other.get_rect()

        # Calculate overlap on each axis
        overlap_x = 0
        overlap_y = 0

        # Check X axis overlap
        if rect1.right > rect2.left and rect1.left < rect2.right:
            # Overlapping on X
            if rect1.centerx < rect2.centerx:
                # rect1 is to the left
                overlap_x = rect1.right - rect2.left
            else:
                # rect1 is to the right
                overlap_x = -(rect2.right - rect1.left)

        # Check Y axis overlap
        if rect1.bottom > rect2.top and rect1.top < rect2.bottom:
            # Overlapping on Y
            if rect1.centery < rect2.centery:
                # rect1 is above
                overlap_y = rect1.bottom - rect2.top
            else:
                # rect1 is below
                overlap_y = -(rect2.bottom - rect1.top)

        return (overlap_x, overlap_y)

    def update(self, dt: float):
        """
        Update collision state.

        Args:
            dt: Delta time in seconds
        """
        # Clear previous frame's collisions
        # (Will be repopulated by collision detection system)
        pass

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'width': self.width,
            'height': self.height,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'is_trigger': self.is_trigger,
            'layer': self.layer
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'width' in data:
            self.width = data['width']
        if 'height' in data:
            self.height = data['height']
        if 'offset_x' in data:
            self.offset_x = data['offset_x']
        if 'offset_y' in data:
            self.offset_y = data['offset_y']
        if 'is_trigger' in data:
            self.is_trigger = data['is_trigger']
        if 'layer' in data:
            self.layer = data['layer']
