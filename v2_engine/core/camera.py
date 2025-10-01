"""
Camera system for viewport management.
"""

import pygame
from v2_engine.utils.math import Vector2, lerp


class Camera:
    """
    Camera controls viewport and provides world-to-screen transforms.

    The camera defines what portion of the game world is visible
    and provides coordinate conversion between world and screen space.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize camera.

        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.position = Vector2(0, 0)  # World position of camera center
        self.width = width
        self.height = height
        self.zoom = 1.0

        # Camera bounds (optional, for level boundaries)
        self.bounds = None  # pygame.Rect in world coordinates

    def follow(self, target, lerp_factor: float = 1.0):
        """
        Smoothly follow a target sprite.

        Args:
            target: Sprite or Vector2 to follow
            lerp_factor: Interpolation speed (1.0 = instant, 0.1 = smooth)
        """
        # Get target position
        if hasattr(target, 'position'):
            target_pos = target.position
        else:
            target_pos = target

        # Lerp camera position
        self.position.x = lerp(self.position.x, target_pos.x, lerp_factor)
        self.position.y = lerp(self.position.y, target_pos.y, lerp_factor)

        # Apply bounds if set
        self.apply_bounds()

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world position to screen coordinates.

        Args:
            world_pos: Position in world space

        Returns:
            Position in screen space
        """
        screen_x = (world_pos.x - self.position.x) * self.zoom + self.width / 2
        screen_y = (world_pos.y - self.position.y) * self.zoom + self.height / 2
        return Vector2(screen_x, screen_y)

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen position to world coordinates.

        Args:
            screen_pos: Position in screen space

        Returns:
            Position in world space
        """
        world_x = (screen_pos.x - self.width / 2) / self.zoom + self.position.x
        world_y = (screen_pos.y - self.height / 2) / self.zoom + self.position.y
        return Vector2(world_x, world_y)

    def is_visible(self, sprite) -> bool:
        """
        Check if sprite is within camera viewport (for culling).

        Args:
            sprite: Sprite to check

        Returns:
            True if sprite is visible
        """
        # Get sprite bounds
        sprite_rect = sprite.get_rect()

        # Calculate camera viewport in world space
        half_width = self.width / (2 * self.zoom)
        half_height = self.height / (2 * self.zoom)

        viewport = pygame.Rect(
            self.position.x - half_width,
            self.position.y - half_height,
            half_width * 2,
            half_height * 2
        )

        # Check intersection
        return viewport.colliderect(sprite_rect)

    def apply_bounds(self):
        """Clamp camera position to bounds if set."""
        if not self.bounds:
            return

        # Calculate how much of the world is visible
        half_width = self.width / (2 * self.zoom)
        half_height = self.height / (2 * self.zoom)

        # Clamp position
        self.position.x = max(self.bounds.left + half_width,
                              min(self.position.x, self.bounds.right - half_width))
        self.position.y = max(self.bounds.top + half_height,
                              min(self.position.y, self.bounds.bottom - half_height))

    def set_bounds(self, x: float, y: float, width: float, height: float):
        """
        Set camera bounds in world coordinates.

        Args:
            x, y: Top-left corner of bounds
            width, height: Size of bounds
        """
        self.bounds = pygame.Rect(x, y, width, height)

    def clear_bounds(self):
        """Remove camera bounds."""
        self.bounds = None
