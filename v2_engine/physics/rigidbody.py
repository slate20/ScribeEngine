"""
RigidBody component for physics simulation.
"""

from v2_engine.sprites.components import Component
from v2_engine.utils.math import Vector2


class RigidBody(Component):
    """
    Component that adds physics behavior to a sprite.

    Handles velocity, acceleration, gravity, and collision response.
    """

    def __init__(self, sprite):
        """
        Initialize rigidbody.

        Args:
            sprite: Sprite this component is attached to
        """
        super().__init__(sprite)

        # Physics properties
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.gravity_scale = 1.0
        self.mass = 1.0

        # Collision properties
        self.is_kinematic = False  # If True, not affected by forces
        self.is_trigger = False    # If True, no collision response
        self.layer_mask = -1       # Which layers can collide with this

        # State
        self.grounded = False
        self.collisions = []  # Collisions this frame

        # Friction and drag
        self.friction = 0.1  # Ground friction
        self.air_resistance = 0.01  # Air drag

    def apply_force(self, force: Vector2):
        """
        Apply instantaneous force (F = ma).

        Args:
            force: Force vector to apply
        """
        if self.is_kinematic:
            return

        self.acceleration = self.acceleration + (force / self.mass)

    def apply_impulse(self, impulse: Vector2):
        """
        Apply velocity change directly.

        Args:
            impulse: Velocity change to apply
        """
        if self.is_kinematic:
            return

        self.velocity = self.velocity + impulse

    def update(self, dt: float, world_gravity: Vector2 = None):
        """
        Update physics simulation.

        Args:
            dt: Delta time in seconds
            world_gravity: World gravity vector (default: Vector2(0, 980))
        """
        if self.is_kinematic:
            return

        # Apply gravity
        if world_gravity is None:
            world_gravity = Vector2(0, 980)  # Default gravity

        gravity_force = world_gravity * self.gravity_scale
        self.velocity = self.velocity + (gravity_force * dt)

        # Apply acceleration
        self.velocity = self.velocity + (self.acceleration * dt)

        # Reset acceleration (forces are applied each frame)
        self.acceleration = Vector2(0, 0)

        # Apply air resistance
        if not self.grounded:
            self.velocity = self.velocity * (1.0 - self.air_resistance)

        # Apply friction when grounded
        if self.grounded and abs(self.velocity.x) > 0:
            friction_force = -self.velocity.x * self.friction
            self.velocity.x += friction_force

        # Update position
        self.sprite.position = self.sprite.position + (self.velocity * dt)

        # Reset grounded state (will be set by collision detection)
        self.grounded = False

        # Clear old collisions
        self.collisions.clear()
