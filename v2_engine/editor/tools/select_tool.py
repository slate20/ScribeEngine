"""
Sprite selection tool for the editor.
"""

import pygame
from v2_engine.utils.math import Vector2


class SelectTool:
    """Click to select sprites in the scene."""

    def handle_click(self, world_pos: Vector2, scene):
        """
        Find and return sprite at world position.

        Args:
            world_pos: World coordinates to check
            scene: Current scene instance

        Returns:
            Sprite at position, or None if no sprite found
        """
        if not scene:
            return None

        # Check all sprite groups (reverse order for top-to-bottom selection)
        all_sprites = []
        for group_name, sprite_group in scene.sprite_groups.items():
            all_sprites.extend(sprite_group.sprites)

        # Check sprites in reverse order (last drawn = first selected)
        for sprite in reversed(all_sprites):
            if self._point_in_sprite(world_pos, sprite):
                return sprite

        return None

    def _point_in_sprite(self, world_pos: Vector2, sprite) -> bool:
        """
        Check if world position is inside sprite bounds.

        Args:
            world_pos: World coordinates to check
            sprite: Sprite to check against

        Returns:
            True if point is inside sprite
        """
        rect = sprite.get_rect()
        return rect.collidepoint(int(world_pos.x), int(world_pos.y))
