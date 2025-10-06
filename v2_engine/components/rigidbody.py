"""
RigidBody component for physics simulation.
"""

from v2_engine.components.component import Component
from v2_engine.utils.math import Vector2


class RigidBody(Component):
    """
    Component that adds physics behavior to a sprite.

    Handles velocity, acceleration, gravity, and collision response.
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Physics',
        'description': 'Physics simulation with gravity and forces',
        'icon': '⚙️',
        'properties_info': {
            'mass': 'Object mass (affects force response)',
            'gravity_scale': 'Gravity multiplier (1.0 = normal, 0 = no gravity)',
            'is_kinematic': 'If checked, not affected by forces',
            'friction': 'Ground friction coefficient',
            'air_resistance': 'Air drag coefficient'
        }
    }

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
        self.was_grounded = False  # Grounded state from previous frame
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

        # Apply gravity if NOT grounded (uses was_grounded from previous frame)
        # OR if jumping (negative Y velocity)
        if not self.was_grounded or self.velocity.y < 0:
            gravity_force = world_gravity * self.gravity_scale
            self.velocity = self.velocity + (gravity_force * dt)
        elif self.was_grounded and self.velocity.y > 0:
            # If was grounded with downward velocity, clamp it
            self.velocity.y = 0

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

        # Clamp very small velocities to zero (prevents micro-movements and vibration)
        if abs(self.velocity.x) < 0.5:
            self.velocity.x = 0
        if abs(self.velocity.y) < 0.5:
            self.velocity.y = 0

        # Don't move if grounded and velocity is zero (completely at rest)
        if self.was_grounded and abs(self.velocity.y) < 0.01 and abs(self.velocity.x) < 0.01:
            # Completely at rest - skip position update
            pass
        else:
            # Update position
            self.sprite.position = self.sprite.position + (self.velocity * dt)

        # Clear old collisions
        self.collisions.clear()

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'velocity': {'x': self.velocity.x, 'y': self.velocity.y},
            'gravity_scale': self.gravity_scale,
            'mass': self.mass,
            'is_kinematic': self.is_kinematic,
            'is_trigger': self.is_trigger,
            'friction': self.friction,
            'air_resistance': self.air_resistance,
            'grounded': self.grounded
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'velocity' in data:
            self.velocity.x = data['velocity']['x']
            self.velocity.y = data['velocity']['y']
        if 'gravity_scale' in data:
            self.gravity_scale = data['gravity_scale']
        if 'mass' in data:
            self.mass = data['mass']
        if 'is_kinematic' in data:
            self.is_kinematic = data['is_kinematic']
        if 'is_trigger' in data:
            self.is_trigger = data['is_trigger']
        if 'friction' in data:
            self.friction = data['friction']
        if 'air_resistance' in data:
            self.air_resistance = data['air_resistance']
        if 'grounded' in data:
            self.grounded = data['grounded']
            self.was_grounded = data['grounded']  # Sync both states
