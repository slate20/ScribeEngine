"""
Base sprite class for Scribe Engine V2.

Sprites are game objects with visual representation and behaviors.
"""

import pygame
from v2_engine.utils.math import Vector2


class Sprite:
    """
    Base class for all game objects with visual representation.

    Sprites have:
    - Transform (position, rotation, scale)
    - Visual representation (image, color)
    - Components (behaviors like RigidBody, Animator)
    - Lifecycle methods (update, render)
    """

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize sprite.

        Args:
            x: Initial x position
            y: Initial y position
        """
        # Transform
        self.position = Vector2(x, y)
        self.rotation = 0.0  # degrees
        self.scale = Vector2(1.0, 1.0)

        # Visual
        self.image = None  # pygame Surface
        self.color = (255, 255, 255)
        self.visible = True
        self.layer = 0  # Z-order for rendering

        # Components
        self.components = {}  # component_type -> component instance

        # Lifecycle
        self.active = True

    def add_component(self, component: 'Component'):
        """
        Add a behavior component to this sprite.

        Args:
            component: Component instance
        """
        component_type = type(component)
        self.components[component_type] = component

    def get_component(self, component_type: type) -> 'Component':
        """
        Get component by type.

        Args:
            component_type: Type of component to retrieve

        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_type)

    def has_component(self, component_type: type) -> bool:
        """
        Check if sprite has a component of given type.

        Args:
            component_type: Type of component to check

        Returns:
            True if component exists
        """
        return component_type in self.components

    def remove_component(self, component_type: type):
        """
        Remove component by type.

        Args:
            component_type: Type of component to remove
        """
        if component_type in self.components:
            component = self.components[component_type]
            component.on_destroy()
            del self.components[component_type]

    def update(self, dt: float):
        """
        Update sprite and all components.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        # Update all components
        for component in self.components.values():
            if component.enabled:
                component.update(dt)

    def render(self, screen, camera=None):
        """
        Render sprite to screen with camera offset.

        Args:
            screen: pygame Surface to render to
            camera: Camera instance for viewport transform (optional)
        """
        if not self.visible or not self.image:
            return

        # Calculate screen position
        if camera:
            screen_pos = camera.world_to_screen(self.position)
        else:
            screen_pos = self.position

        # Create transformed image if needed
        if self.rotation != 0 or self.scale != Vector2(1, 1):
            # Scale
            if self.scale != Vector2(1, 1):
                width = int(self.image.get_width() * self.scale.x)
                height = int(self.image.get_height() * self.scale.y)
                transformed = pygame.transform.scale(self.image, (width, height))
            else:
                transformed = self.image

            # Rotate
            if self.rotation != 0:
                transformed = pygame.transform.rotate(transformed, -self.rotation)

            render_image = transformed
        else:
            render_image = self.image

        # Center the image on the position
        rect = render_image.get_rect()
        rect.center = (int(screen_pos.x), int(screen_pos.y))

        # Render
        screen.blit(render_image, rect)

    def get_rect(self) -> pygame.Rect:
        """
        Get axis-aligned bounding box for collision.

        Returns:
            pygame.Rect representing sprite bounds
        """
        if self.image:
            width = self.image.get_width() * self.scale.x
            height = self.image.get_height() * self.scale.y
        else:
            width = 32  # Default size
            height = 32

        return pygame.Rect(
            self.position.x - width / 2,
            self.position.y - height / 2,
            width,
            height
        )

    def destroy(self):
        """Destroy sprite and cleanup components."""
        for component in list(self.components.values()):
            component.on_destroy()
        self.components.clear()
        self.active = False
