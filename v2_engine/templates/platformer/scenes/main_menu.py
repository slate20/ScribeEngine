"""
Main Menu Scene for Platformer Demo
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.ui.button import Button
from v2_engine.ui.text import TextLabel
from v2_engine.ui.panel import Panel


class MainMenuScene(Scene):
    """Main menu with start game and quit options."""

    def __init__(self, game):
        super().__init__(game)

        self.title_label = None
        self.start_button = None
        self.quit_button = None
        self.instructions_panel = None

    def on_enter(self):
        """Initialize menu UI."""
        print("[MainMenu] Scene entered")

        screen_width = self.game.project_config['window']['width']
        screen_height = self.game.project_config['window']['height']

        # Title
        self.title_label = TextLabel(
            screen_width // 2,
            100,
            "PLATFORMER DEMO",
            font_size=64
        )
        self.title_label.align = "center"
        self.title_label.text_color = (255, 255, 100)

        # Start button
        self.start_button = Button(
            screen_width // 2,
            screen_height // 2 - 40,
            200,
            60,
            "START GAME",
            font_size=28
        )
        self.start_button.on_click = self.start_game

        # Quit button
        self.quit_button = Button(
            screen_width // 2,
            screen_height // 2 + 40,
            200,
            60,
            "QUIT",
            font_size=28
        )
        self.quit_button.on_click = self.quit_game

        # Instructions panel
        self.instructions_panel = Panel(
            screen_width // 2 - 200,
            screen_height - 200,
            400,
            150
        )

        # Add instruction labels to panel
        instructions = [
            "Controls:",
            "Arrow Keys / WASD - Move",
            "Space / W - Jump",
            "Collect all coins to win!"
        ]

        y_offset = screen_height - 185
        for i, text in enumerate(instructions):
            label = TextLabel(screen_width // 2, y_offset + i * 30, text, font_size=20)
            label.align = "center"
            if i == 0:
                label.text_color = (255, 255, 100)
            self.instructions_panel.add_widget(label)

        self.ui_elements = [
            self.title_label,
            self.start_button,
            self.quit_button,
            self.instructions_panel
        ]

    def on_exit(self):
        """Clean up menu."""
        print("[MainMenu] Scene exited")

    def start_game(self):
        """Start the game - load level 01."""
        print("[MainMenu] Starting game...")
        self.game.scene_manager.load_scene("level_01")

    def quit_game(self):
        """Quit the application."""
        print("[MainMenu] Quitting...")
        self.game.quit()

    def handle_event(self, event):
        """Handle menu input."""
        # Pass events to UI elements
        for element in self.ui_elements:
            element.handle_event(event)

    def update(self, dt):
        """Update menu."""
        # Update UI elements
        for element in self.ui_elements:
            element.update(dt)

    def render(self, screen):
        """Render menu."""
        # Background gradient (dark blue to black)
        for y in range(screen.get_height()):
            progress = y / screen.get_height()
            color = (
                int(20 * (1 - progress)),
                int(30 * (1 - progress)),
                int(60 * (1 - progress))
            )
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))

        # Render UI elements
        for element in self.ui_elements:
            element.render(screen)

        # Version info
        try:
            font = pygame.font.Font(None, 18)
            version_text = font.render("Scribe Engine V2 - Phase 1 Demo", True, (100, 100, 100))
            version_rect = version_text.get_rect(bottomright=(screen.get_width() - 10, screen.get_height() - 10))
            screen.blit(version_text, version_rect)
        except:
            pass
