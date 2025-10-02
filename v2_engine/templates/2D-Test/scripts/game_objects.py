"""
Basic Game Object Classes

These are simple placeholder classes that you can customize.
Feel free to modify these or create your own!
"""

import pygame
from v2_engine.sprites.sprite import Sprite
from v2_engine.physics.rigidbody import RigidBody


class Player(Sprite):
    """Player character - customize with your own controls!"""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (placeholder - blue rectangle)
        self.image = pygame.Surface((32, 48))
        self.image.fill((0, 150, 255))
        self.layer = 10

        # Add physics if needed
        # self.rigidbody = RigidBody(self)
        # self.add_component(self.rigidbody)


class Platform(Sprite):
    """Static platform for objects to stand on."""

    def __init__(self, x, y, width, height):
        super().__init__(x, y)

        # Visual (gray rectangle)
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.layer = 0

        # Physics (static platform)
        self.rigidbody = RigidBody(self)
        self.rigidbody.is_kinematic = True
        self.rigidbody.gravity_scale = 0
        self.add_component(self.rigidbody)


class Collectible(Sprite):
    """Collectible item (coin, gem, powerup)."""

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


class Goal(Sprite):
    """Goal/exit point."""

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


class Enemy(Sprite):
    """Enemy character."""

    def __init__(self, x, y):
        super().__init__(x, y)

        # Visual (red rectangle)
        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 0, 0))
        self.layer = 10

        # Add physics if needed
        # self.rigidbody = RigidBody(self)
        # self.add_component(self.rigidbody)
