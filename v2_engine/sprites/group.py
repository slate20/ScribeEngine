"""
Sprite groups for batch operations and rendering.
"""

from v2_engine.core.game_object import GameObject


class SpriteGroup:
    """
    Container for game objects (sprites and logic objects) with batch operations.

    Sprite groups organize game objects and provide efficient
    batch operations for updating and rendering.
    """

    def __init__(self, name: str = "default"):
        """
        Initialize sprite group.

        Args:
            name: Group identifier
        """
        self.name = name
        self.sprites = []  # Note: name kept as 'sprites' for backward compat

    def add(self, sprite: GameObject):
        """
        Add game object to group.

        Args:
            sprite: GameObject (SpriteObject or LogicObject) to add
        """
        if sprite not in self.sprites:
            self.sprites.append(sprite)

    def remove(self, sprite: GameObject):
        """
        Remove game object from group.

        Args:
            sprite: GameObject to remove
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
