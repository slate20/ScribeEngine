"""
Sprite groups for batch operations and rendering.
"""

from v2_engine.sprites.sprite import Sprite


class SpriteGroup:
    """
    Container for sprites with batch update and render.

    Sprite groups organize sprites and provide efficient
    batch operations for updating and rendering.
    """

    def __init__(self, name: str = "default"):
        """
        Initialize sprite group.

        Args:
            name: Group identifier
        """
        self.name = name
        self.sprites = []

    def add(self, sprite: Sprite):
        """
        Add sprite to group.

        Args:
            sprite: Sprite to add
        """
        if sprite not in self.sprites:
            self.sprites.append(sprite)

    def remove(self, sprite: Sprite):
        """
        Remove sprite from group.

        Args:
            sprite: Sprite to remove
        """
        if sprite in self.sprites:
            self.sprites.remove(sprite)

    def clear(self):
        """Remove all sprites from group."""
        self.sprites.clear()

    def update(self, dt: float):
        """
        Update all sprites in group.

        Args:
            dt: Delta time in seconds
        """
        for sprite in self.sprites:
            if sprite.active:
                sprite.update(dt)

    def render(self, screen, camera=None):
        """
        Render all sprites in group sorted by layer.

        Args:
            screen: pygame Surface to render to
            camera: Camera instance for viewport transform
        """
        # Sort by layer (lower layers render first)
        sorted_sprites = sorted(self.sprites, key=lambda s: s.layer)

        for sprite in sorted_sprites:
            if sprite.visible:
                sprite.render(screen, camera)

    def __len__(self):
        """Get number of sprites in group."""
        return len(self.sprites)

    def __iter__(self):
        """Iterate over sprites in group."""
        return iter(self.sprites)
