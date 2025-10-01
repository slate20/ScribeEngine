"""
Math utilities for Scribe Engine V2.

Provides Vector2 class and common math helpers.
"""

import math


class Vector2:
    """2D vector for positions, velocities, and directions."""

    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        """Vector addition."""
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """Vector subtraction."""
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        """Scalar multiplication."""
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        """Scalar division."""
        if scalar == 0:
            raise ValueError("Cannot divide by zero")
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> 'Vector2':
        """Negate vector."""
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: 'Vector2') -> bool:
        """Check equality."""
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    def length(self) -> float:
        """Calculate vector magnitude."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self) -> float:
        """Calculate squared magnitude (faster than length())."""
        return self.x * self.x + self.y * self.y

    def normalized(self) -> 'Vector2':
        """Return unit vector in same direction."""
        mag = self.length()
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def normalize(self):
        """Normalize this vector in-place."""
        mag = self.length()
        if mag > 0:
            self.x /= mag
            self.y /= mag

    def dot(self, other: 'Vector2') -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: 'Vector2') -> float:
        """Calculate distance to another vector."""
        return (other - self).length()

    def lerp(self, other: 'Vector2', t: float) -> 'Vector2':
        """Linear interpolation to another vector."""
        t = max(0.0, min(1.0, t))  # Clamp to [0, 1]
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t
        )

    def copy(self) -> 'Vector2':
        """Create a copy of this vector."""
        return Vector2(self.x, self.y)

    def to_tuple(self) -> tuple:
        """Convert to tuple (x, y)."""
        return (self.x, self.y)

    @staticmethod
    def zero() -> 'Vector2':
        """Return zero vector."""
        return Vector2(0, 0)

    @staticmethod
    def one() -> 'Vector2':
        """Return vector of ones."""
        return Vector2(1, 1)

    @staticmethod
    def up() -> 'Vector2':
        """Return up direction vector."""
        return Vector2(0, -1)

    @staticmethod
    def down() -> 'Vector2':
        """Return down direction vector."""
        return Vector2(0, 1)

    @staticmethod
    def left() -> 'Vector2':
        """Return left direction vector."""
        return Vector2(-1, 0)

    @staticmethod
    def right() -> 'Vector2':
        """Return right direction vector."""
        return Vector2(1, 0)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(max_value, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t
