"""
PygameWidget: A PyQt6 widget that displays a Pygame surface.
"""

import pygame
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from v2_engine.utils.math import Vector2
from v2_engine.editor.theme import get_theme


class PygameWidget(QLabel):
    """Widget that displays a Pygame surface as a QImage."""

    def __init__(self, parent=None, editor_window=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Styled by global theme - viewport background
        theme = get_theme()
        self.setStyleSheet(f"background-color: {theme.background_light}; border: 1px solid {theme.border_strong};")
        self.setMouseTracking(True)  # Enable mouse tracking for hover events

        # Store reference to editor window for event callbacks
        self.editor_window = editor_window

        # Initialize Pygame without display (render to surface only)
        pygame.init()
        self.pygame_surface = pygame.Surface((800, 600))

        # Mouse state
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.middle_mouse_pressed = False
        self.space_held = False

    def get_surface(self):
        """Get the Pygame surface for rendering."""
        return self.pygame_surface

    def update_from_surface(self):
        """Convert Pygame surface to QPixmap and display it."""
        # Convert pygame surface to QImage
        width, height = self.pygame_surface.get_size()
        data = pygame.image.tostring(self.pygame_surface, 'RGB')
        qimage = QImage(data, width, height, width * 3, QImage.Format.Format_RGB888)

        # Convert to pixmap and display
        pixmap = QPixmap.fromImage(qimage)
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        size = self.size()
        self.pygame_surface = pygame.Surface((size.width(), size.height()))

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_pos = Vector2(event.pos().x(), event.pos().y())
            # Notify editor window of mouse press
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_press'):
                self.editor_window.on_viewport_mouse_press(event.pos().x(), event.pos().y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = True
            self.last_mouse_pos = Vector2(event.pos().x(), event.pos().y())

    def mouseDoubleClickEvent(self, event):
        """Handle mouse double-click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Notify editor window of double-click
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_double_click'):
                self.editor_window.on_viewport_double_click(event.pos().x(), event.pos().y())

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        current_pos = Vector2(event.pos().x(), event.pos().y())

        # Update cursor position in status bar
        if self.editor_window and hasattr(self.editor_window, 'update_cursor_position'):
            self.editor_window.update_cursor_position(current_pos.x, current_pos.y)

        # Middle mouse drag OR Space + left mouse drag - pan camera
        if (self.middle_mouse_pressed or (self.space_held and self.mouse_pressed)) and self.last_mouse_pos:
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_camera_pan'):
                delta = current_pos - self.last_mouse_pos
                self.editor_window.on_viewport_camera_pan(delta.x, delta.y)

        # Left mouse drag (without space) - move sprite
        elif self.mouse_pressed and not self.space_held and self.last_mouse_pos:
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_drag'):
                self.editor_window.on_viewport_mouse_drag(current_pos.x, current_pos.y)

        self.last_mouse_pos = current_pos

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False
            # Notify editor window that drag ended (with position for box selection)
            if self.editor_window and hasattr(self.editor_window, 'on_viewport_mouse_release'):
                pos = event.position()
                self.editor_window.on_viewport_mouse_release(pos.x(), pos.y())
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.middle_mouse_pressed = False

    def wheelEvent(self, event):
        """Handle mouse wheel events for zoom."""
        if self.editor_window and hasattr(self.editor_window, 'on_viewport_wheel'):
            delta = event.angleDelta().y()
            pos = event.position()  # Use position() instead of pos() in PyQt6
            self.editor_window.on_viewport_wheel(delta, pos.x(), pos.y())
