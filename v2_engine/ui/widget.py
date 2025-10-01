"""
Base UI widget class.
"""

import pygame
from v2_engine.utils.math import Vector2


class Widget:
    """
    Base class for UI elements.

    Widgets are screen-space UI elements (buttons, labels, panels)
    that don't move with the camera.
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize widget.

        Args:
            x, y: Screen position
            width, height: Widget size
        """
        self.position = Vector2(x, y)
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

        # Colors
        self.bg_color = (50, 50, 50)
        self.border_color = (100, 100, 100)
        self.border_width = 2

        # Callbacks
        self.on_click = None

    def get_rect(self) -> pygame.Rect:
        """Get widget bounds as pygame.Rect."""
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside widget bounds."""
        rect = self.get_rect()
        return rect.collidepoint(x, y)

    def handle_event(self, event):
        """
        Handle pygame events.

        Args:
            event: pygame event object
        """
        if not self.enabled or not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos[0], event.pos[1]):
                if self.on_click:
                    self.on_click()

    def update(self, dt: float):
        """
        Update widget logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def render(self, screen):
        """
        Render widget to screen.

        Args:
            screen: pygame Surface
        """
        if not self.visible:
            return

        rect = self.get_rect()

        # Draw background
        pygame.draw.rect(screen, self.bg_color, rect)

        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, rect, self.border_width)
