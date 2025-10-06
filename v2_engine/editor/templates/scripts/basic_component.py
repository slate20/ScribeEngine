"""
Basic Component Template

A minimal component template for custom sprite behaviors.
"""

from v2_engine.components.component import Component


class MyBehavior(Component):
    """
    Custom behavior component.

    TODO: Add description of what this behavior does.
    """

    # Optional metadata for Behavior Browser
    __metadata__ = {
        'category': 'Custom',
        'icon': '⭐',
        'description': 'Custom behavior - edit description here',
    }

    def __init__(self, sprite):
        """
        Initialize the behavior.

        Args:
            sprite: The sprite this component is attached to
        """
        super().__init__(sprite)

        # Add your custom properties here
        self.speed = 100
        self.example_property = "Hello"

    def update(self, dt):
        """
        Update the behavior each frame.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Add your update logic here
        pass

    def on_collision(self, other):
        """
        Called when this sprite collides with another.

        Args:
            other: The other sprite involved in the collision
        """
        # Add collision response logic here
        pass
