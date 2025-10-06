"""
Physics-Aware Component Template

Template for behaviors that interact with physics system.
Demonstrates how to work with RigidBody and collision detection.
"""

from v2_engine.components.component import Component
from v2_engine.components.rigidbody import RigidBody
from v2_engine.components.box_collider import BoxCollider


class PhysicsBehavior(Component):
    """
    Physics-aware behavior component.

    This component demonstrates how to:
    - Check for other components
    - Modify physics properties
    - Respond to collision events
    - Access sprite physics state
    """

    __metadata__ = {
        'category': 'Physics',
        'icon': '⚙️',
        'description': 'Physics-aware behavior template',
    }

    def __init__(self, sprite):
        """
        Initialize the physics behavior.

        Args:
            sprite: The sprite this component is attached to
        """
        super().__init__(sprite)

        # Example properties
        self.bounce_force = 300
        self.max_speed = 500

        # Get references to physics components (if they exist)
        self.rigidbody = self.sprite.get_component(RigidBody)
        self.collider = self.sprite.get_component(BoxCollider)

    def update(self, dt):
        """
        Update physics behavior each frame.

        Args:
            dt: Delta time in seconds since last frame
        """
        if not self.rigidbody:
            return  # No physics component attached

        # Example: Cap maximum velocity
        if self.rigidbody.velocity.length() > self.max_speed:
            self.rigidbody.velocity = self.rigidbody.velocity.normalized() * self.max_speed

        # Example: Check if grounded
        if self.rigidbody.grounded:
            # Sprite is on the ground
            pass

    def on_collision(self, other):
        """
        Called when this sprite collides with another.

        Args:
            other: The other sprite involved in the collision
        """
        if not self.rigidbody:
            return

        # Example: Bounce on collision
        if self.rigidbody.grounded:
            # Apply upward force when hitting ground
            self.rigidbody.velocity.y = -self.bounce_force

        # Example: Check what we collided with
        if hasattr(other, 'name'):
            print(f"Collided with: {other.name}")
