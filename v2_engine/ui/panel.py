"""
Panel container widget for grouping UI elements.
"""

import pygame
from v2_engine.ui.widget import Widget


class Panel(Widget):
    """
    Container panel for grouping widgets.
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize panel.

        Args:
            x, y: Screen position
            width, height: Panel size
        """
        super().__init__(x, y, width, height)

        self.widgets = []
        self.bg_color = (40, 40, 40, 200)  # Semi-transparent dark gray
        self.border_color = (100, 100, 100)
        self.border_width = 2

    def add_widget(self, widget: Widget):
        """
        Add widget to panel.

        Args:
            widget: Widget to add
        """
        self.widgets.append(widget)

    def remove_widget(self, widget: Widget):
        """
        Remove widget from panel.

        Args:
            widget: Widget to remove
        """
        if widget in self.widgets:
            self.widgets.remove(widget)

    def clear(self):
        """Remove all widgets from panel."""
        self.widgets.clear()

    def handle_event(self, event):
        """Handle events for panel and child widgets."""
        if not self.enabled or not self.visible:
            return

        # Pass events to child widgets
        for widget in self.widgets:
            widget.handle_event(event)

    def update(self, dt: float):
        """Update panel and child widgets."""
        if not self.visible:
            return

        for widget in self.widgets:
            widget.update(dt)

    def render(self, screen):
        """Render panel and child widgets."""
        if not self.visible:
            return

        # Draw panel background with alpha
        rect = self.get_rect()
        if len(self.bg_color) == 4:  # Has alpha
            # Create surface with alpha
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surface.fill(self.bg_color)
            screen.blit(surface, (self.position.x, self.position.y))
        else:
            pygame.draw.rect(screen, self.bg_color, rect)

        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, rect, self.border_width)

        # Render child widgets
        for widget in self.widgets:
            widget.render(screen)
