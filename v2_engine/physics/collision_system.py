"""
Collision detection system for scenes.

Handles collision checking between sprites with BoxCollider components.
"""

from v2_engine.components.box_collider import BoxCollider
from v2_engine.components.rigidbody import RigidBody


class CollisionSystem:
    """
    System that detects and resolves collisions between sprites.
    """

    def __init__(self):
        """Initialize collision system."""
        pass

    def check_collisions(self, sprite_groups: dict):
        """
        Check collisions between all sprites with BoxColliders.

        Args:
            sprite_groups: Dictionary of sprite groups to check

        Returns:
            List of collision pairs [(sprite_a, sprite_b, overlap_x, overlap_y), ...]
        """
        collisions = []

        # Collect all sprites with BoxColliders
        all_sprites = []
        for group in sprite_groups.values():
            for sprite in group.sprites:
                if sprite.has_component(BoxCollider):
                    all_sprites.append(sprite)

        # Check each pair
        for i, sprite_a in enumerate(all_sprites):
            collider_a = sprite_a.get_component(BoxCollider)

            for sprite_b in all_sprites[i+1:]:
                collider_b = sprite_b.get_component(BoxCollider)

                # Check collision
                if collider_a.check_collision(collider_b):
                    overlap = collider_a.get_overlap(collider_b)
                    collisions.append((sprite_a, sprite_b, overlap[0], overlap[1]))

                    # Update collision state
                    if sprite_b not in collider_a.colliding_with:
                        collider_a.colliding_with.append(sprite_b)
                    if sprite_a not in collider_b.colliding_with:
                        collider_b.colliding_with.append(sprite_a)

        return collisions

    def resolve_collisions(self, collisions: list):
        """
        Resolve physical collisions (push apart overlapping sprites).

        Args:
            collisions: List of collision tuples from check_collisions()
        """
        for sprite_a, sprite_b, overlap_x, overlap_y in collisions:
            collider_a = sprite_a.get_component(BoxCollider)
            collider_b = sprite_b.get_component(BoxCollider)

            # Skip if either is a trigger (no physical response)
            if collider_a.is_trigger or collider_b.is_trigger:
                continue

            # Get rigidbodies (if they exist)
            rb_a = sprite_a.get_component(RigidBody)
            rb_b = sprite_b.get_component(RigidBody)

            # Determine which axis has less overlap (resolve on that axis)
            if abs(overlap_x) < abs(overlap_y):
                # Resolve on X axis
                self._resolve_x(sprite_a, sprite_b, overlap_x, rb_a, rb_b)
            else:
                # Resolve on Y axis
                self._resolve_y(sprite_a, sprite_b, overlap_y, rb_a, rb_b)

    def _resolve_x(self, sprite_a, sprite_b, overlap_x, rb_a, rb_b):
        """Resolve collision on X axis."""
        # Determine which sprites can move
        a_kinematic = rb_a.is_kinematic if rb_a else True
        b_kinematic = rb_b.is_kinematic if rb_b else True

        if not a_kinematic and not b_kinematic:
            # Both can move - split the difference
            sprite_a.position.x -= overlap_x / 2
            sprite_b.position.x += overlap_x / 2

            # Stop horizontal velocity
            if rb_a:
                rb_a.velocity.x = 0
            if rb_b:
                rb_b.velocity.x = 0

        elif not a_kinematic:
            # Only A can move
            sprite_a.position.x -= overlap_x
            if rb_a:
                rb_a.velocity.x = 0

        elif not b_kinematic:
            # Only B can move
            sprite_b.position.x += overlap_x
            if rb_b:
                rb_b.velocity.x = 0

    def _resolve_y(self, sprite_a, sprite_b, overlap_y, rb_a, rb_b):
        """Resolve collision on Y axis."""
        # Determine which sprites can move
        a_kinematic = rb_a.is_kinematic if rb_a else True
        b_kinematic = rb_b.is_kinematic if rb_b else True

        if not a_kinematic and not b_kinematic:
            # Both can move - split the difference
            sprite_a.position.y -= overlap_y / 2
            sprite_b.position.y += overlap_y / 2

            # Stop vertical velocity
            if rb_a:
                rb_a.velocity.y = 0
            if rb_b:
                rb_b.velocity.y = 0

            # Set grounded state
            if overlap_y > 0:  # A is above B
                if rb_a:
                    rb_a.grounded = True
            else:  # B is above A
                if rb_b:
                    rb_b.grounded = True

        elif not a_kinematic:
            # Only A can move
            sprite_a.position.y -= overlap_y

            if rb_a:
                # Stop velocity and set grounded
                if overlap_y > 0:  # A is above B (landing on top)
                    if rb_a.velocity.y > 0:  # Only stop downward velocity
                        rb_a.velocity.y = 0
                    rb_a.grounded = True
                else:  # A is below B (hitting ceiling)
                    if rb_a.velocity.y < 0:  # Only stop upward velocity
                        rb_a.velocity.y = 0

        elif not b_kinematic:
            # Only B can move
            sprite_b.position.y += overlap_y

            if rb_b:
                rb_b.velocity.y = 0
                if overlap_y < 0:  # B is above A (landing on top)
                    rb_b.grounded = True
