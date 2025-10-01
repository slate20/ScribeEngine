"""
Input handling for Scribe Engine V2.

Centralized input state management for keyboard and mouse.
"""

import pygame


class InputHandler:
    """
    Centralized input state management.

    Provides convenient methods for checking key/button states
    without directly processing pygame events everywhere.
    """

    def __init__(self):
        # Keyboard state
        self._keys_down = set()      # Currently held keys
        self._keys_pressed = set()   # Keys pressed this frame
        self._keys_released = set()  # Keys released this frame

        # Mouse state
        self._mouse_pos = (0, 0)
        self._mouse_buttons_down = set()
        self._mouse_buttons_pressed = set()
        self._mouse_buttons_released = set()

    def update(self, events: list):
        """
        Process pygame events and update input state.

        Args:
            events: List of pygame events from this frame
        """
        # Reset frame-specific states
        self._keys_pressed.clear()
        self._keys_released.clear()
        self._mouse_buttons_pressed.clear()
        self._mouse_buttons_released.clear()

        # Process events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._keys_down.add(event.key)
                self._keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self._keys_down.discard(event.key)
                self._keys_released.add(event.key)
            elif event.type == pygame.MOUSEMOTION:
                self._mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_buttons_down.add(event.button)
                self._mouse_buttons_pressed.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_buttons_down.discard(event.button)
                self._mouse_buttons_released.add(event.button)

    def is_key_down(self, key) -> bool:
        """
        Check if key is currently held down.

        Args:
            key: pygame key constant (e.g., pygame.K_SPACE)

        Returns:
            True if key is held down
        """
        return key in self._keys_down

    def is_key_pressed(self, key) -> bool:
        """
        Check if key was pressed this frame (once).

        Args:
            key: pygame key constant

        Returns:
            True if key was just pressed
        """
        return key in self._keys_pressed

    def is_key_released(self, key) -> bool:
        """
        Check if key was released this frame.

        Args:
            key: pygame key constant

        Returns:
            True if key was just released
        """
        return key in self._keys_released

    def get_mouse_pos(self) -> tuple:
        """
        Get current mouse position (x, y).

        Returns:
            Tuple of (x, y) screen coordinates
        """
        return self._mouse_pos

    def is_mouse_button_down(self, button: int) -> bool:
        """
        Check if mouse button is held down.

        Args:
            button: Mouse button number (1=left, 2=middle, 3=right)

        Returns:
            True if button is held
        """
        return button in self._mouse_buttons_down

    def is_mouse_button_pressed(self, button: int) -> bool:
        """
        Check if mouse button was clicked this frame.

        Args:
            button: Mouse button number

        Returns:
            True if button was just clicked
        """
        return button in self._mouse_buttons_pressed

    def is_mouse_button_released(self, button: int) -> bool:
        """
        Check if mouse button was released this frame.

        Args:
            button: Mouse button number

        Returns:
            True if button was just released
        """
        return button in self._mouse_buttons_released

    def reset_frame_state(self):
        """Clear frame-specific input states (pressed/released)."""
        self._keys_pressed.clear()
        self._keys_released.clear()
        self._mouse_buttons_pressed.clear()
        self._mouse_buttons_released.clear()
