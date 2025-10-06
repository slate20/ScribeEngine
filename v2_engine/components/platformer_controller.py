"""
PlatformerController component for player movement.
"""

import pygame
from v2_engine.components.component import Component
from v2_engine.components.rigidbody import RigidBody
from v2_engine.components.box_collider import BoxCollider


class PlatformerController(Component):
    """
    Component that provides platformer-style movement controls.

    Requires: RigidBody and BoxCollider components.
    """

    # Metadata for behavior browser
    METADATA = {
        'category': 'Gameplay',
        'description': 'Player movement with jump and air control',
        'icon': '🎮',
        'properties_info': {
            'move_speed': 'Horizontal movement speed (pixels/second)',
            'jump_force': 'Jump velocity (negative = up)',
            'air_control': 'Movement control while airborne (0-1)',
            'can_double_jump': 'Allow double jump ability',
            'coyote_time': 'Grace period for jumping after leaving ground',
            'jump_buffer_time': 'Buffer window for early jump input'
        }
    }

    def __init__(self, sprite):
        """
        Initialize platformer controller.

        Args:
            sprite: Sprite this component is attached to
        """
        super().__init__(sprite)

        # Movement properties
        self.move_speed = 300.0  # Horizontal movement speed (pixels/second)
        self.jump_force = -500.0  # Jump velocity (negative = up)
        self.air_control = 0.8  # How much control in air (0-1, 1 = full control)

        # Jump properties
        self.can_double_jump = True
        self.has_double_jumped = False
        self.coyote_time = 0.1  # Seconds after leaving ground you can still jump
        self.jump_buffer_time = 0.1  # Seconds before landing that jump input is remembered

        # Internal state
        self._time_since_grounded = 0.0
        self._jump_buffer_timer = 0.0

    def update(self, dt: float):
        """
        Update platformer controls.

        Args:
            dt: Delta time in seconds
        """
        # Get required components
        rigidbody = self.sprite.get_component(RigidBody)
        if not rigidbody:
            print("[PlatformerController] Warning: RigidBody component required!")
            return

        # Get input from scene
        if not hasattr(self.sprite, 'scene') or not self.sprite.scene:
            return

        input_handler = self.sprite.scene.input

        if not input_handler:
            return

        # Update timers
        if rigidbody.grounded:
            self._time_since_grounded = 0.0
            self.has_double_jumped = False
        else:
            self._time_since_grounded += dt

        if self._jump_buffer_timer > 0:
            self._jump_buffer_timer -= dt

        # Horizontal movement
        move_input = 0.0
        if input_handler.is_key_down(pygame.K_LEFT) or input_handler.is_key_down(pygame.K_a):
            move_input -= 1.0
        if input_handler.is_key_down(pygame.K_RIGHT) or input_handler.is_key_down(pygame.K_d):
            move_input += 1.0

        # Apply movement
        if rigidbody.grounded or self.air_control > 0:
            control_factor = 1.0 if rigidbody.grounded else self.air_control
            target_velocity = move_input * self.move_speed * control_factor

            # Smooth acceleration (not instant)
            accel_rate = 20.0 if rigidbody.grounded else 10.0
            rigidbody.velocity.x += (target_velocity - rigidbody.velocity.x) * min(accel_rate * dt, 1.0)

        # Jump input
        jump_pressed = (input_handler.is_key_pressed(pygame.K_UP) or
                       input_handler.is_key_pressed(pygame.K_w) or
                       input_handler.is_key_pressed(pygame.K_SPACE))

        if jump_pressed:
            self._jump_buffer_timer = self.jump_buffer_time

        # Jump logic
        can_coyote_jump = self._time_since_grounded < self.coyote_time
        wants_jump = self._jump_buffer_timer > 0

        if wants_jump:
            # Ground jump (including coyote time)
            if rigidbody.grounded or can_coyote_jump:
                rigidbody.velocity.y = self.jump_force
                self._jump_buffer_timer = 0.0
                self._time_since_grounded = self.coyote_time  # Prevent coyote jump spam

            # Double jump
            elif self.can_double_jump and not self.has_double_jumped:
                rigidbody.velocity.y = self.jump_force
                self.has_double_jumped = True
                self._jump_buffer_timer = 0.0

        # Variable jump height (release jump key early = shorter jump)
        jump_released = (input_handler.is_key_released(pygame.K_UP) or
                        input_handler.is_key_released(pygame.K_w) or
                        input_handler.is_key_released(pygame.K_SPACE))

        if jump_released and rigidbody.velocity.y < 0:  # Moving upward
            rigidbody.velocity.y *= 0.5  # Cut jump short

    def to_dict(self) -> dict:
        """Serialize component state to dictionary."""
        return {
            'move_speed': self.move_speed,
            'jump_force': self.jump_force,
            'air_control': self.air_control,
            'can_double_jump': self.can_double_jump,
            'has_double_jumped': self.has_double_jumped,
            'coyote_time': self.coyote_time,
            'jump_buffer_time': self.jump_buffer_time
        }

    def from_dict(self, data: dict):
        """Restore component state from dictionary."""
        if 'move_speed' in data:
            self.move_speed = data['move_speed']
        if 'jump_force' in data:
            self.jump_force = data['jump_force']
        if 'air_control' in data:
            self.air_control = data['air_control']
        if 'can_double_jump' in data:
            self.can_double_jump = data['can_double_jump']
        if 'has_double_jumped' in data:
            self.has_double_jumped = data['has_double_jumped']
        if 'coyote_time' in data:
            self.coyote_time = data['coyote_time']
        if 'jump_buffer_time' in data:
            self.jump_buffer_time = data['jump_buffer_time']
