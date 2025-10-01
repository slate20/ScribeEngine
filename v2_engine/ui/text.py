"""
Text rendering widget.
"""

import pygame
from v2_engine.ui.widget import Widget


class TextLabel(Widget):
    """
    Simple text label widget.
    """

    def __init__(self, x: float, y: float, text: str, font_size: int = 24):
        """
        Initialize text label.

        Args:
            x, y: Screen position
            text: Text to display
            font_size: Font size in pixels
        """
        # Calculate size from text
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, (255, 255, 255))
        width = text_surface.get_width()
        height = text_surface.get_height()

        super().__init__(x, y, width, height)

        self.text = text
        self.font_size = font_size
        self.font = font
        self.text_color = (255, 255, 255)
        self.bg_color = None  # Transparent background by default
        self.border_width = 0

        # Alignment
        self.align = "left"  # "left", "center", "right"

    def set_text(self, text: str):
        """Update label text."""
        self.text = text

        # Recalculate size
        text_surface = self.font.render(text, True, self.text_color)
        self.width = text_surface.get_width()
        self.height = text_surface.get_height()

    def render(self, screen):
        """Render text label."""
        if not self.visible:
            return

        # Draw background if set
        if self.bg_color:
            super().render(screen)

        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)

        # Calculate position based on alignment
        if self.align == "center":
            x = self.position.x - text_surface.get_width() / 2
            y = self.position.y - text_surface.get_height() / 2
        elif self.align == "right":
            x = self.position.x - text_surface.get_width()
            y = self.position.y
        else:  # left
            x = self.position.x
            y = self.position.y

        screen.blit(text_surface, (x, y))
