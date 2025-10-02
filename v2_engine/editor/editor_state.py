"""
Editor state management for edit/play modes, camera, and selection.
"""

import pygame
from v2_engine.utils.math import Vector2


class EditorCamera:
    """Editor viewport camera (separate from game camera)."""

    def __init__(self):
        self.position = Vector2(0, 0)
        self.zoom = 1.0
        self.grid_size = 32
        self.snap_to_grid = True

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        return Vector2(
            screen_pos.x / self.zoom + self.position.x,
            screen_pos.y / self.zoom + self.position.y
        )

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Convert world coordinates to screen coordinates."""
        return Vector2(
            (world_pos.x - self.position.x) * self.zoom,
            (world_pos.y - self.position.y) * self.zoom
        )

    def world_to_screen_rect(self, world_rect: pygame.Rect) -> pygame.Rect:
        """Convert world rect to screen rect."""
        screen_pos = self.world_to_screen(Vector2(world_rect.x, world_rect.y))
        return pygame.Rect(
            int(screen_pos.x),
            int(screen_pos.y),
            int(world_rect.width * self.zoom),
            int(world_rect.height * self.zoom)
        )

    def snap_to_grid_value(self, value: float) -> float:
        """Snap a value to grid."""
        if self.snap_to_grid:
            return round(value / self.grid_size) * self.grid_size
        return value

    def pan(self, delta: Vector2):
        """Pan the camera by delta."""
        self.position.x -= delta.x / self.zoom
        self.position.y -= delta.y / self.zoom

    def zoom_at(self, screen_pos: Vector2, zoom_delta: float):
        """Zoom camera centered on a screen position."""
        # Get world position before zoom
        world_pos = self.screen_to_world(screen_pos)

        # Apply zoom
        self.zoom = max(0.1, min(10.0, self.zoom + zoom_delta))

        # Adjust position to keep world_pos under cursor
        new_world_pos = self.screen_to_world(screen_pos)
        self.position.x += world_pos.x - new_world_pos.x
        self.position.y += world_pos.y - new_world_pos.y

    def reset(self):
        """Reset camera to default position and zoom."""
        self.position = Vector2(0, 0)
        self.zoom = 1.0


class EditorState:
    """Main editor state container."""

    def __init__(self):
        self.mode = "edit"  # "edit" or "play"
        self.camera = EditorCamera()
        self.selected_sprite = None
        self.dragging_sprite = False
        self.drag_offset = Vector2(0, 0)
        self.panning = False
        self.pan_start = Vector2(0, 0)

    def enter_play_mode(self):
        """Switch to play mode."""
        self.mode = "play"
        self.selected_sprite = None

    def enter_edit_mode(self):
        """Switch to edit mode."""
        self.mode = "edit"
