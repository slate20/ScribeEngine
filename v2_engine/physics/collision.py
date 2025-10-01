"""
AABB collision detection and resolution.
"""

import pygame
from v2_engine.utils.math import Vector2
from v2_engine.physics.rigidbody import RigidBody


class Collision:
    """Information about a collision between two sprites."""

    def __init__(self, sprite_a, sprite_b, normal: Vector2, penetration: float):
        """
        Initialize collision info.

        Args:
            sprite_a: First sprite in collision
            sprite_b: Second sprite in collision
            normal: Collision normal (direction to separate)
            penetration: How much the sprites overlap
        """
        self.sprite_a = sprite_a
        self.sprite_b = sprite_b
        self.normal = normal
        self.penetration = penetration


class CollisionSystem:
    """
    Handles AABB collision detection and resolution.
    """

    @staticmethod
    def check_collision(rect_a: pygame.Rect, rect_b: pygame.Rect) -> bool:
        """
        Check if two rectangles overlap.

        Args:
            rect_a: First rectangle
            rect_b: Second rectangle

        Returns:
            True if rectangles overlap
        """
        return rect_a.colliderect(rect_b)

    @staticmethod
    def get_collision_info(sprite_a, sprite_b) -> Collision:
        """
        Get detailed collision information between two sprites.

        Args:
            sprite_a: First sprite
            sprite_b: Second sprite

        Returns:
            Collision object with normal and penetration
        """
        rect_a = sprite_a.get_rect()
        rect_b = sprite_b.get_rect()

        # Calculate overlap on each axis
        overlap_x = min(rect_a.right, rect_b.right) - max(rect_a.left, rect_b.left)
        overlap_y = min(rect_a.bottom, rect_b.bottom) - max(rect_a.top, rect_b.top)

        # Determine collision normal (direction to separate)
        if overlap_x < overlap_y:
            # Separate horizontally
            if sprite_a.position.x < sprite_b.position.x:
                normal = Vector2(-1, 0)  # Push A left
            else:
                normal = Vector2(1, 0)   # Push A right
            penetration = overlap_x
        else:
            # Separate vertically
            if sprite_a.position.y < sprite_b.position.y:
                normal = Vector2(0, -1)  # Push A up
            else:
                normal = Vector2(0, 1)   # Push A down
            penetration = overlap_y

        return Collision(sprite_a, sprite_b, normal, penetration)

    @staticmethod
    def resolve_collision(sprite_a, sprite_b):
        """
        Resolve collision between two sprites with RigidBody components.

        Applies collision response (separation and velocity changes).

        Args:
            sprite_a: First sprite
            sprite_b: Second sprite
        """
        # Get rigidbody components
        rb_a = sprite_a.get_component(RigidBody)
        rb_b = sprite_b.get_component(RigidBody)

        if not rb_a and not rb_b:
            return  # No physics on either sprite

        # Get collision info
        collision = CollisionSystem.get_collision_info(sprite_a, sprite_b)

        # Check for trigger colliders
        if (rb_a and rb_a.is_trigger) or (rb_b and rb_b.is_trigger):
            # Trigger collision - no physical response, just notify
            if rb_a:
                rb_a.collisions.append(collision)
            if rb_b:
                rb_b.collisions.append(collision)
            return

        # Separate sprites
        if rb_a and not rb_a.is_kinematic and rb_b and not rb_b.is_kinematic:
            # Both dynamic - split separation
            separation = collision.normal * (collision.penetration / 2)
            sprite_a.position = sprite_a.position + separation
            sprite_b.position = sprite_b.position - separation
        elif rb_a and not rb_a.is_kinematic:
            # Only A is dynamic
            separation = collision.normal * collision.penetration
            sprite_a.position = sprite_a.position + separation
        elif rb_b and not rb_b.is_kinematic:
            # Only B is dynamic
            separation = collision.normal * collision.penetration
            sprite_b.position = sprite_b.position - separation

        # Apply velocity response
        if rb_a and not rb_a.is_kinematic:
            # Stop velocity in collision normal direction
            velocity_along_normal = rb_a.velocity.dot(collision.normal)
            if velocity_along_normal < 0:  # Moving into collision
                rb_a.velocity = rb_a.velocity - (collision.normal * velocity_along_normal)

            # Set grounded if collision from above
            if collision.normal.y < -0.5:  # Normal pointing up
                rb_a.grounded = True

            # Record collision
            rb_a.collisions.append(collision)

        if rb_b and not rb_b.is_kinematic:
            # Stop velocity in opposite direction
            velocity_along_normal = rb_b.velocity.dot(collision.normal * -1)
            if velocity_along_normal < 0:
                rb_b.velocity = rb_b.velocity + (collision.normal * velocity_along_normal)

            # Set grounded if collision from above
            if collision.normal.y > 0.5:  # Normal pointing down (from B's perspective)
                rb_b.grounded = True

            # Record collision (flip normal for B's perspective)
            flipped = Collision(sprite_b, sprite_a, collision.normal * -1, collision.penetration)
            rb_b.collisions.append(flipped)

    @staticmethod
    def detect_collisions(sprites: list) -> list:
        """
        Broad-phase collision detection.

        Args:
            sprites: List of sprites to check

        Returns:
            List of (sprite_a, sprite_b) collision pairs
        """
        collisions = []

        # Simple O(n^2) collision detection
        # TODO: Add spatial partitioning (quadtree) for better performance
        for i in range(len(sprites)):
            for j in range(i + 1, len(sprites)):
                sprite_a = sprites[i]
                sprite_b = sprites[j]

                if CollisionSystem.check_collision(sprite_a.get_rect(), sprite_b.get_rect()):
                    collisions.append((sprite_a, sprite_b))

        return collisions

    @staticmethod
    def resolve_collisions(collision_pairs: list):
        """
        Resolve multiple collisions.

        Args:
            collision_pairs: List of (sprite_a, sprite_b) tuples
        """
        for sprite_a, sprite_b in collision_pairs:
            CollisionSystem.resolve_collision(sprite_a, sprite_b)
