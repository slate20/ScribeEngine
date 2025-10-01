"""
Component base class for sprite behaviors.

Components add modular functionality to sprites (physics, animation, etc).
"""


class Component:
    """
    Base class for sprite components.

    Components are behaviors that can be attached to sprites
    to add functionality like physics, animation, AI, etc.
    """

    def __init__(self, sprite: 'Sprite'):
        """
        Initialize component.

        Args:
            sprite: The sprite this component is attached to
        """
        self.sprite = sprite
        self.enabled = True

    def update(self, dt: float):
        """
        Update component logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def on_destroy(self):
        """Called when component is removed or sprite is destroyed."""
        pass
