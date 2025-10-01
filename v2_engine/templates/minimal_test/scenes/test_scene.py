"""
Minimal test scene to verify engine functionality.
"""

import pygame
from v2_engine.core.scene import Scene


class TestScene(Scene):
    """Minimal test scene with colored rectangle."""

    def __init__(self, game):
        super().__init__(game)
        self.message = "Scribe Engine V2 - Core Systems Working!"
        self.color_index = 0
        self.colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
        ]
        self.timer = 0

    def on_enter(self):
        """Called when scene loads."""
        print("[TestScene] Scene entered")

    def on_exit(self):
        """Called when scene exits."""
        print("[TestScene] Scene exited")

    def update(self, dt):
        """Update scene."""
        # Cycle through colors every second
        self.timer += dt
        if self.timer >= 1.0:
            self.timer = 0
            self.color_index = (self.color_index + 1) % len(self.colors)

    def render(self, screen):
        """Render scene."""
        # Fill background
        screen.fill((20, 20, 30))

        # Draw animated rectangle
        color = self.colors[self.color_index]
        rect_size = 200
        rect_x = (screen.get_width() - rect_size) // 2
        rect_y = (screen.get_height() - rect_size) // 2
        pygame.draw.rect(screen, color, (rect_x, rect_y, rect_size, rect_size))

        # Draw text
        try:
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.message, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 50))
            screen.blit(text_surface, text_rect)

            # Draw instructions
            inst_font = pygame.font.Font(None, 24)
            instructions = [
                "Core systems initialized successfully!",
                "Press ESC to quit",
                f"FPS: {self.game.time_manager.fps}",
                f"Color changes every second"
            ]
            y_offset = 150
            for inst in instructions:
                inst_surface = inst_font.render(inst, True, (200, 200, 200))
                inst_rect = inst_surface.get_rect(center=(screen.get_width() // 2, y_offset))
                screen.blit(inst_surface, inst_rect)
                y_offset += 30
        except Exception as e:
            print(f"[TestScene] Error rendering text: {e}")
