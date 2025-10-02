"""
Native Launcher for Scribe Engine V2 Editor

Simple startup window for creating/opening projects.
"""

import os
import sys
import pygame


class Button:
    """Simple button with hover state."""

    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.color = (60, 60, 65)
        self.hover_color = (70, 70, 75)
        self.text_color = (220, 220, 220)

    def draw(self, screen):
        """Draw the button."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 105), self.rect, 2, border_radius=5)

        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_mouse_motion(self, pos):
        """Update hover state."""
        self.hovered = self.rect.collidepoint(pos)

    def handle_click(self, pos):
        """Handle click event."""
        if self.rect.collidepoint(pos):
            return self.action()
        return None


class Launcher:
    """Main launcher window."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 500))
        pygame.display.set_caption("Scribe Engine V2 - Launcher")

        self.running = True
        self.clock = pygame.time.Clock()

        # Create buttons
        button_width = 400
        button_height = 60
        button_x = (600 - button_width) // 2
        start_y = 180

        self.buttons = [
            Button(button_x, start_y, button_width, button_height,
                   "New Project", self.new_project),
            Button(button_x, start_y + 80, button_width, button_height,
                   "Open Project", self.open_project),
            Button(button_x, start_y + 160, button_width, button_height,
                   "Quit", self.quit),
        ]

        self.result = None  # Will store 'new', 'open', or None

    def new_project(self):
        """Handle new project action."""
        print("[Launcher] New Project selected")
        self.result = 'new'
        self.running = False
        return 'new'

    def open_project(self):
        """Handle open project action."""
        print("[Launcher] Open Project selected")
        self.result = 'open'
        self.running = False
        return 'open'

    def quit(self):
        """Handle quit action."""
        print("[Launcher] Quit selected")
        self.result = None
        self.running = False
        return None

    def run(self):
        """Run the launcher loop."""
        while self.running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEMOTION:
                    for button in self.buttons:
                        button.handle_mouse_motion(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        for button in self.buttons:
                            result = button.handle_click(event.pos)
                            if result:
                                break

            # Render
            self.screen.fill((45, 45, 48))  # Dark grey background

            # Draw title
            font_large = pygame.font.Font(None, 64)
            title = font_large.render("Scribe Engine V2", True, (220, 220, 220))
            title_rect = title.get_rect(center=(300, 80))
            self.screen.blit(title, title_rect)

            # Draw subtitle
            font_small = pygame.font.Font(None, 24)
            subtitle = font_small.render("Visual 2D Game Development", True, (150, 150, 150))
            subtitle_rect = subtitle.get_rect(center=(300, 120))
            self.screen.blit(subtitle, subtitle_rect)

            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return self.result


def main():
    """Entry point for launcher."""
    launcher = Launcher()
    result = launcher.run()

    if result == 'new':
        print("[Launcher] Launching project wizard...")
        # TODO: Launch project wizard
        from v2_engine.editor.project_wizard import ProjectWizard
        wizard = ProjectWizard()
        project_path = wizard.run()

        if project_path:
            print(f"[Launcher] Opening editor with project: {project_path}")
            # Launch PyQt6 editor
            from v2_engine.editor.qt_editor import main as editor_main
            editor_main(project_path)

    elif result == 'open':
        print("[Launcher] Opening file browser...")
        # TODO: Launch file browser for project selection
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()

        project_path = filedialog.askdirectory(title="Select Project Directory")
        root.destroy()

        if project_path and os.path.exists(os.path.join(project_path, '2d_project.json')):
            print(f"[Launcher] Opening editor with project: {project_path}")
            # Launch PyQt6 editor
            from v2_engine.editor.qt_editor import main as editor_main
            editor_main(project_path)
        elif project_path:
            print(f"[Launcher] Error: Not a valid Scribe Engine V2 project")
        else:
            print("[Launcher] No project selected")

    else:
        print("[Launcher] Exiting")


if __name__ == '__main__':
    main()
