"""
Main Scene - Empty starting scene

This is your starting point. Add objects using the visual editor!
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.core.camera import Camera
from v2_engine.sprites.group import SpriteGroup
from scripts.game_objects import Platform


class MainScene(Scene):
    """Main game scene - empty template ready for your game objects."""

    def __init__(self, game):
        super().__init__(game)

        self.camera = None

        # Sprite groups
        self.all_sprites = SpriteGroup("all")
        self.solid_sprites = SpriteGroup("solid_sprites")

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
        # [SCRIBE_OBJECT_START: platform]
        self.platform = Platform(0, 0, 200, 32)
        # Properties: {"x": 0, "y": 0, "width": 200, "height": 32}
        # [SCRIBE_OBJECT_END: platform]
        self.all_sprites.add(self.platform)
        self.solid_sprites.add(self.platform)

        # Debug: Print sprite info
        print(f"[MainScene] Created platform at ({self.platform.position.x}, {self.platform.position.y})")
        print(f"[MainScene] Platform image size: {self.platform.image.get_size() if self.platform.image else 'None'}")
        print(f"[MainScene] all_sprites count: {len(self.all_sprites.sprites)}")

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
            sprite_count = len(self.all_sprites.sprites)
            instructions = [
                f"Objects in scene: {sprite_count}",
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
