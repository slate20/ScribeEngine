"""
AI State Machine Template

Template for behaviors with state-based AI logic.
Demonstrates state machine pattern for enemy AI, NPCs, etc.
"""

from v2_engine.components.component import Component
from v2_engine.utils.math import Vector2


class AIBehavior(Component):
    """
    State machine AI behavior component.

    This component demonstrates:
    - State machine pattern
    - State transitions
    - Per-state update logic
    - Target tracking
    """

    __metadata__ = {
        'category': 'AI',
        'icon': '🤖',
        'description': 'AI state machine template',
    }

    # Define available states
    STATE_IDLE = 'idle'
    STATE_PATROL = 'patrol'
    STATE_CHASE = 'chase'
    STATE_ATTACK = 'attack'

    def __init__(self, sprite):
        """
        Initialize the AI behavior.

        Args:
            sprite: The sprite this component is attached to
        """
        super().__init__(sprite)

        # Current state
        self.state = self.STATE_IDLE

        # State-specific properties
        self.idle_timer = 0
        self.idle_duration = 2.0  # Seconds

        self.patrol_speed = 50
        self.patrol_distance = 200
        self.patrol_start_x = sprite.position.x
        self.patrol_direction = 1

        self.chase_speed = 150
        self.chase_range = 300
        self.target = None  # Sprite to chase

        self.attack_range = 50
        self.attack_cooldown = 1.0
        self.attack_timer = 0

    def update(self, dt):
        """
        Update AI behavior based on current state.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Update timers
        self.attack_timer = max(0, self.attack_timer - dt)

        # State machine logic
        if self.state == self.STATE_IDLE:
            self._update_idle(dt)
        elif self.state == self.STATE_PATROL:
            self._update_patrol(dt)
        elif self.state == self.STATE_CHASE:
            self._update_chase(dt)
        elif self.state == self.STATE_ATTACK:
            self._update_attack(dt)

    def _update_idle(self, dt):
        """Idle state: Wait for a duration, then transition to patrol."""
        self.idle_timer += dt

        if self.idle_timer >= self.idle_duration:
            self.transition_to(self.STATE_PATROL)

        # Check for nearby targets
        if self._find_target():
            self.transition_to(self.STATE_CHASE)

    def _update_patrol(self, dt):
        """Patrol state: Move back and forth."""
        # Move
        self.sprite.position.x += self.patrol_speed * self.patrol_direction * dt

        # Check if reached patrol boundary
        distance_from_start = abs(self.sprite.position.x - self.patrol_start_x)
        if distance_from_start > self.patrol_distance:
            self.patrol_direction *= -1  # Reverse direction

        # Check for nearby targets
        if self._find_target():
            self.transition_to(self.STATE_CHASE)

    def _update_chase(self, dt):
        """Chase state: Follow the target."""
        if not self.target:
            self.transition_to(self.STATE_PATROL)
            return

        # Calculate direction to target
        direction = Vector2(
            self.target.position.x - self.sprite.position.x,
            self.target.position.y - self.sprite.position.y
        )
        distance = direction.length()

        # Check if in attack range
        if distance <= self.attack_range:
            self.transition_to(self.STATE_ATTACK)
            return

        # Check if target escaped
        if distance > self.chase_range * 1.5:  # Give up if too far
            self.target = None
            self.transition_to(self.STATE_PATROL)
            return

        # Move toward target
        if distance > 0:
            direction = direction.normalized()
            self.sprite.position.x += direction.x * self.chase_speed * dt
            self.sprite.position.y += direction.y * self.chase_speed * dt

    def _update_attack(self, dt):
        """Attack state: Attack the target."""
        if not self.target:
            self.transition_to(self.STATE_PATROL)
            return

        # Calculate distance to target
        direction = Vector2(
            self.target.position.x - self.sprite.position.x,
            self.target.position.y - self.sprite.position.y
        )
        distance = direction.length()

        # Check if target moved out of range
        if distance > self.attack_range * 1.2:
            self.transition_to(self.STATE_CHASE)
            return

        # Perform attack (if cooldown ready)
        if self.attack_timer <= 0:
            self._perform_attack()
            self.attack_timer = self.attack_cooldown

    def _find_target(self):
        """
        Look for a target in chase range.

        Returns:
            bool: True if target found, False otherwise
        """
        # Example: Find player sprite in scene
        # Customize this based on your game's needs
        if not self.sprite.scene:
            return False

        for sprite in self.sprite.scene.sprites:
            if sprite == self.sprite:
                continue  # Skip self

            # Check if this is a player (customize this check)
            if hasattr(sprite, 'name') and 'player' in sprite.name.lower():
                distance = (sprite.position - self.sprite.position).length()
                if distance <= self.chase_range:
                    self.target = sprite
                    return True

        return False

    def _perform_attack(self):
        """Execute attack logic."""
        print(f"[AI] {self.sprite.name} attacks {self.target.name}!")

        # Add your attack logic here
        # Examples:
        # - Deal damage to target
        # - Play attack animation
        # - Spawn projectile
        # - Apply knockback

    def transition_to(self, new_state):
        """
        Transition to a new state.

        Args:
            new_state: The state to transition to
        """
        print(f"[AI] {self.sprite.name}: {self.state} -> {new_state}")

        # Exit current state (cleanup)
        if self.state == self.STATE_IDLE:
            self.idle_timer = 0

        # Enter new state (initialization)
        if new_state == self.STATE_IDLE:
            self.idle_timer = 0
        elif new_state == self.STATE_PATROL:
            self.patrol_start_x = self.sprite.position.x

        self.state = new_state

    def on_collision(self, other):
        """
        Called when this sprite collides with another.

        Args:
            other: The other sprite involved in the collision
        """
        # Example: If colliding with target while in attack state, deal damage
        if self.state == self.STATE_ATTACK and other == self.target:
            if self.attack_timer <= 0:
                self._perform_attack()
                self.attack_timer = self.attack_cooldown
