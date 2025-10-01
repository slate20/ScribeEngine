"""
Time management for Scribe Engine V2.

Handles delta time calculation and frame rate management.
"""

import time


class TimeManager:
    """
    Manages delta time and frame timing.

    Provides accurate delta time for physics and animations,
    and tracks FPS for debugging.
    """

    def __init__(self, target_fps: int = 60):
        """
        Initialize time manager.

        Args:
            target_fps: Target frames per second
        """
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps if target_fps > 0 else 0

        self._last_time = time.time()
        self._delta_time = 0.0
        self._frame_count = 0
        self._fps_timer = 0.0
        self._current_fps = 0

    def update(self) -> float:
        """
        Update time tracking and calculate delta time.

        Returns:
            Delta time in seconds since last frame
        """
        current_time = time.time()
        self._delta_time = current_time - self._last_time
        self._last_time = current_time

        # Track FPS
        self._frame_count += 1
        self._fps_timer += self._delta_time
        if self._fps_timer >= 1.0:
            self._current_fps = self._frame_count
            self._frame_count = 0
            self._fps_timer = 0.0

        return self._delta_time

    @property
    def delta_time(self) -> float:
        """Get delta time in seconds."""
        return self._delta_time

    @property
    def fps(self) -> int:
        """Get current FPS."""
        return self._current_fps

    def reset(self):
        """Reset time tracking (useful when resuming from pause)."""
        self._last_time = time.time()
        self._delta_time = 0.0
