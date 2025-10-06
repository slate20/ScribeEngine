"""
Button widget with hover and click states.
"""

import pygame
from v2_engine.ui.widget import Widget


class Button(Widget):
    """
    Clickable button widget with text label.
    """

    def __init__(self, x: float, y: float, width: float, height: float, text: str, font_size: int = 24):
        """
        Initialize button.

        Args:
            x, y: Screen position (centered on these coordinates)
            width, height: Button size
            text: Button label text
            font_size: Font size in pixels
        """
        super().__init__(x - width / 2, y - height / 2, width, height)

        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)

        # Colors
        self.bg_color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.active_color = (50, 50, 50)
        self.disabled_color = (40, 40, 40)
        self.text_color = (255, 255, 255)
        self.disabled_text_color = (100, 100, 100)
        self.border_color = (150, 150, 150)
        self.disabled_border_color = (80, 80, 80)
        self.border_width = 2

        # State
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event):
        """Handle mouse events for button interaction."""
        if not self.enabled or not self.visible:
            return

        # Check hover state
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.contains_point(event.pos[0], event.pos[1])

        # Handle click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains_point(event.pos[0], event.pos[1]):
                self.is_pressed = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.contains_point(event.pos[0], event.pos[1]):
                if self.on_click:
                    self.on_click()
            self.is_pressed = False

    def render(self, screen):
        """Render button with current state."""
        if not self.visible:
            return

        rect = self.get_rect()

        # Choose colors based on enabled state
        if not self.enabled:
            bg_color = self.disabled_color
            border_color = self.disabled_border_color
            text_color = self.disabled_text_color
        elif self.is_pressed:
            bg_color = self.active_color
            border_color = self.border_color
            text_color = self.text_color
        elif self.is_hovered:
            bg_color = self.hover_color
            border_color = self.border_color
            text_color = self.text_color
        else:
            bg_color = self.bg_color
            border_color = self.border_color
            text_color = self.text_color

        # Draw background
        pygame.draw.rect(screen, bg_color, rect)

        # Draw border
        pygame.draw.rect(screen, border_color, rect, self.border_width)

        # Draw text centered
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
