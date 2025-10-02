"""
Main Scene - Empty starting scene

This is your starting point. Add objects using the visual editor!
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.core.camera import Camera
from v2_engine.sprites.group import SpriteGroup


class MainScene(Scene):
    """Main game scene - empty template ready for your game objects."""

    def __init__(self, game):
        super().__init__(game)

        self.camera = None

        # Sprite groups (using sprite_groups dict for editor compatibility)
        self.sprite_groups['all'] = SpriteGroup("all")

        # Convenience reference
        self.all_sprites = self.sprite_groups['all']

    def on_enter(self):
        """Initialize scene when it loads."""
        print("[MainScene] Scene loaded - Use the editor to add objects!")

        # Create camera at world origin
        # Camera position (0, 0) means viewport shows world (0, 0) at top-left of screen
        screen_width = self.game.project_config['window']['width']
        screen_height = self.game.project_config['window']['height']
        self.camera = Camera(screen_width, screen_height)

        # Add objects here using the visual editor!
        # Objects will appear between these markers:
        # [SCRIBE_OBJECTS_START]

        # Simple test sprite to verify editor rendering
        from v2_engine.sprites.sprite import Sprite
        from v2_engine.utils.math import Vector2

        test_sprite = Sprite(400, 300)  # Center of 800x600 screen
        test_sprite.image = pygame.Surface((64, 64))
        test_sprite.image.fill((100, 200, 255))  # Light blue rectangle
        test_sprite.origin = Vector2(0.5, 0.5)  # Center origin
        test_sprite.layer = 0

        self.all_sprites.add(test_sprite)

        # [SCRIBE_OBJECTS_END]

    def on_exit(self):
        """Called when scene exits."""
        print("[MainScene] Scene exited")

    def update(self, dt):
        """Update scene logic."""
        # Check for ESC key to return to menu
        if self.game.input_handler.is_key_pressed(pygame.K_ESCAPE):
            print("[MainScene] Exiting game...")
            self.game.quit()
            return

        # Update all sprites
        self.all_sprites.update(dt)

    def render(self, screen):
        """Render scene."""
        # Clear screen with background color
        screen.fill((135, 206, 235))  # Sky blue

        # Render all sprites with camera
        self.all_sprites.render(screen, self.camera)

        # Render UI
        self._render_ui(screen)

    def _render_ui(self, screen):
        """Render UI elements."""
        try:
            font = pygame.font.Font(None, 24)

            # Instructions
            instructions = [
                "Empty Scene - Add objects using the Visual Editor!",
                "ESC: Quit"
            ]

            y_offset = 10
            for inst in instructions:
                inst_surface = font.render(inst, True, (255, 255, 255))
                inst_rect = inst_surface.get_rect(topleft=(10, y_offset))

                # Shadow
                shadow_rect = inst_rect.copy()
                shadow_rect.x += 1
                shadow_rect.y += 1
                shadow = font.render(inst, True, (0, 0, 0))
                screen.blit(shadow, shadow_rect)
                screen.blit(inst_surface, inst_rect)

                y_offset += 30

        except Exception as e:
            print(f"[MainScene] Error rendering UI: {e}")
