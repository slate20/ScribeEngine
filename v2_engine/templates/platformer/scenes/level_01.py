"""
Level 01 - Platformer Demo

Simple platforming level with player movement, platforms, and collectibles.
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.sprites.sprite import Sprite
from v2_engine.sprites.group import SpriteGroup
from v2_engine.physics.rigidbody import RigidBody
from v2_engine.physics.collision import CollisionSystem
from v2_engine.core.camera import Camera
from v2_engine.utils.math import Vector2


class Player(Sprite):
    """Player character with platformer controls."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (placeholder - blue rectangle)
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 150, 255))
        self.layer = 10  # Render above platforms

        # Physics
        self.rigidbody = RigidBody(self)
        self.rigidbody.friction = 0.3
        self.add_component(self.rigidbody)

        # Movement parameters
        self.move_speed = 300.0
        self.jump_force = 500.0

        # Jump buffering and coyote time
        self.jump_buffer_time = 0.0
        self.jump_buffer_duration = 0.1  # 100ms
        self.coyote_time = 0.0
        self.coyote_duration = 0.15  # 150ms
        self.was_grounded = False

    def handle_input(self, input_handler, dt):
        """
        Handle player input.

        Args:
            input_handler: InputHandler instance
            dt: Delta time
        """
        # Horizontal movement
        move_x = 0
        if input_handler.is_key_down(pygame.K_LEFT) or input_handler.is_key_down(pygame.K_a):
            move_x = -1
        if input_handler.is_key_down(pygame.K_RIGHT) or input_handler.is_key_down(pygame.K_d):
            move_x = 1

        self.rigidbody.velocity.x = move_x * self.move_speed

        # Coyote time - allow jumping shortly after leaving ground
        if self.rigidbody.grounded:
            self.coyote_time = self.coyote_duration
            self.was_grounded = True
        elif self.was_grounded:
            self.coyote_time -= dt
            if self.coyote_time <= 0:
                self.was_grounded = False

        # Jump buffering - remember jump input for a short time
        if input_handler.is_key_pressed(pygame.K_SPACE) or input_handler.is_key_pressed(pygame.K_w):
            self.jump_buffer_time = self.jump_buffer_duration

        if self.jump_buffer_time > 0:
            self.jump_buffer_time -= dt

            # Execute jump if grounded or in coyote time
            if self.rigidbody.grounded or self.coyote_time > 0:
                self.rigidbody.velocity.y = -self.jump_force
                self.jump_buffer_time = 0  # Consume jump
                self.coyote_time = 0  # Consume coyote time
                self.was_grounded = False


class Platform(Sprite):
    """Static platform for player to stand on."""

    def __init__(self, x, y, width, height):
        super().__init__(x, y)

        # Visual (gray rectangle)
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.layer = 0  # Render behind player

        # Physics (kinematic = static, not affected by forces)
        self.rigidbody = RigidBody(self)
        self.rigidbody.is_kinematic = True
        self.rigidbody.gravity_scale = 0
        self.add_component(self.rigidbody)


class Collectible(Sprite):
    """Collectible coin/gem."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (yellow circle)
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 220, 0), (8, 8), 8)
        self.layer = 5

        # Trigger collider (no physics response)
        self.rigidbody = RigidBody(self)
        self.rigidbody.is_trigger = True
        self.rigidbody.is_kinematic = True
        self.rigidbody.gravity_scale = 0
        self.add_component(self.rigidbody)

        # Animation
        self.bob_offset = 0
        self.bob_speed = 2.0

    def update(self, dt):
        """Animate collectible."""
        super().update(dt)

        # Bob up and down
        self.bob_offset += dt * self.bob_speed
        import math
        self.position.y += math.sin(self.bob_offset) * 0.5


class Goal(Sprite):
    """Goal platform that completes the level."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (green rectangle with "GOAL" text)
        self.image = pygame.Surface((64, 64))
        self.image.fill((0, 200, 0))

        # Draw "GOAL" text
        try:
            font = pygame.font.Font(None, 20)
            text = font.render("GOAL", True, (255, 255, 255))
            text_rect = text.get_rect(center=(32, 32))
            self.image.blit(text, text_rect)
        except:
            pass

        self.layer = 5

        # Trigger collider
        self.rigidbody = RigidBody(self)
        self.rigidbody.is_trigger = True
        self.rigidbody.is_kinematic = True
        self.rigidbody.gravity_scale = 0
        self.add_component(self.rigidbody)


class Level01Scene(Scene):
    """First level - simple platforming."""

    def __init__(self, game):
        super().__init__(game)

        self.player = None
        self.platforms = []
        self.collectibles = []
        self.goal = None
        self.camera = None

        # Game state
        self.score = 0
        self.level_complete = False

        # Sprite groups (using base Scene sprite_groups dictionary for editor compatibility)
        self.sprite_groups['all'] = SpriteGroup("all")
        self.sprite_groups['solid'] = SpriteGroup("solid")  # Sprites with collision

        # Convenience references
        self.all_sprites = self.sprite_groups['all']
        self.solid_sprites = self.sprite_groups['solid']

    def on_enter(self):
        """Initialize level when scene loads."""
        print("[Level01] Creating level...")

        # Create camera
        screen_width = self.game.project_config['window']['width']
        screen_height = self.game.project_config['window']['height']
        self.camera = Camera(screen_width, screen_height)
        self.camera.set_bounds(0, 0, 1600, 600)  # Level bounds

        # Create player
        # [SCRIBE_SPRITE_START: player]
        self.player = Player(100, 300)
        # Properties: {"x": 150, "y": 300}
        # [SCRIBE_SPRITE_END: player]
        self.all_sprites.add(self.player)
        self.solid_sprites.add(self.player)

        # Create platforms
        platform_data = [
            (400, 550, 800, 50),   # Ground
            (200, 450, 150, 20),   # Platform 1
            (450, 350, 150, 20),   # Platform 2
            (700, 450, 150, 20),   # Platform 3
            (950, 350, 150, 20),   # Platform 4
            (1200, 450, 150, 20),  # Platform 5
            (1400, 350, 200, 20),  # Final platform
        ]

        for x, y, w, h in platform_data:
            platform = Platform(x, y, w, h)
            self.platforms.append(platform)
            self.all_sprites.add(platform)
            self.solid_sprites.add(platform)

        # Create collectibles
        collectible_positions = [
            (200, 400), (450, 300), (700, 400), (950, 300), (1200, 400)
        ]

        for x, y in collectible_positions:
            collectible = Collectible(x, y)
            self.collectibles.append(collectible)
            self.all_sprites.add(collectible)
            self.solid_sprites.add(collectible)

        # Create goal
        self.goal = Goal(1450, 300)
        self.all_sprites.add(self.goal)
        self.solid_sprites.add(self.goal)

        print(f"[Level01] Created {len(self.platforms)} platforms, {len(self.collectibles)} collectibles")

    def on_exit(self):
        """Called when scene exits."""
        print("[Level01] Scene exited")

    def update(self, dt):
        """Update level logic."""
        # Check for R key to return to menu
        if self.game.input_handler.is_key_pressed(pygame.K_r):
            print("[Level01] Returning to main menu...")
            self.game.scene_manager.load_scene("main_menu")
            return

        # Handle player input
        self.player.handle_input(self.game.input_handler, dt)

        # Apply physics to player
        world_gravity = Vector2(
            self.game.project_config['physics']['gravity']['x'],
            self.game.project_config['physics']['gravity']['y']
        )
        self.player.rigidbody.update(dt, world_gravity)

        # Update all sprites
        self.all_sprites.update(dt)

        # Collision detection and resolution
        collision_pairs = CollisionSystem.detect_collisions(list(self.solid_sprites))
        CollisionSystem.resolve_collisions(collision_pairs)

        # Check collectible pickups
        for collectible in self.collectibles[:]:
            if CollisionSystem.check_collision(self.player.get_rect(), collectible.get_rect()):
                self.score += 10
                self.collectibles.remove(collectible)
                self.all_sprites.remove(collectible)
                self.solid_sprites.remove(collectible)
                print(f"[Level01] Collected! Score: {self.score}")

        # Check goal reached
        if not self.level_complete and CollisionSystem.check_collision(
            self.player.get_rect(), self.goal.get_rect()
        ):
            self.level_complete = True
            print(f"[Level01] Level Complete! Final score: {self.score}")

        # Camera follow player
        self.camera.follow(self.player, lerp_factor=0.1)

    def render(self, screen):
        """Render level."""
        # Clear screen with sky blue
        screen.fill((135, 206, 235))

        # Render all sprites with camera
        self.all_sprites.render(screen, self.camera)

        # Render UI
        self._render_ui(screen)

    def _render_ui(self, screen):
        """Render UI elements."""
        try:
            font = pygame.font.Font(None, 36)

            # Score
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(topleft=(10, 10))

            # Draw text shadow
            shadow_rect = score_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            shadow = font.render(f"Score: {self.score}", True, (0, 0, 0))
            screen.blit(shadow, shadow_rect)
            screen.blit(score_text, score_rect)

            # Instructions
            inst_font = pygame.font.Font(None, 24)
            instructions = [
                "Arrow Keys / WASD: Move",
                "Space / W: Jump",
                "R: Return to Menu",
                "ESC: Quit"
            ]

            y_offset = screen.get_height() - 105
            for inst in instructions:
                inst_surface = inst_font.render(inst, True, (255, 255, 255))
                inst_rect = inst_surface.get_rect(topleft=(10, y_offset))

                # Shadow
                shadow_rect = inst_rect.copy()
                shadow_rect.x += 1
                shadow_rect.y += 1
                shadow = inst_font.render(inst, True, (0, 0, 0))
                screen.blit(shadow, shadow_rect)
                screen.blit(inst_surface, inst_rect)

                y_offset += 25

            # Level complete message
            if self.level_complete:
                complete_font = pygame.font.Font(None, 64)
                complete_text = complete_font.render("LEVEL COMPLETE!", True, (255, 255, 0))
                complete_rect = complete_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

                # Shadow
                shadow_rect = complete_rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                shadow = complete_font.render("LEVEL COMPLETE!", True, (0, 0, 0))
                screen.blit(shadow, shadow_rect)
                screen.blit(complete_text, complete_rect)

        except Exception as e:
            print(f"[Level01] Error rendering UI: {e}")
