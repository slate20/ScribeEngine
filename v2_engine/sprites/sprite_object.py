"""
SpriteObject class for Scribe Engine V2.

Visual game objects with transform and rendering.
"""

import pygame
from v2_engine.utils.math import Vector2
from v2_engine.core.game_object import GameObject


class SpriteObject(GameObject):
    """
    Visual game object with transform and rendering capabilities.

    SpriteObjects have:
    - Transform (position, rotation, scale, origin)
    - Visual representation (image, color, visibility)
    - Component attachment (inherited from GameObject)
    - Update and render lifecycle
    """

    def __init__(self, x: float = 0, y: float = 0):
        """
        Initialize sprite object.

        Args:
            x: Initial x position
            y: Initial y position
        """
        super().__init__()

        # Transform
        self.position = Vector2(x, y)
        self.rotation = 0.0  # degrees
        self.scale = Vector2(1.0, 1.0)

        # Origin/Pivot point (normalized 0-1)
        # (0.5, 0.5) = center (default), (0, 0) = top-left, (0.5, 1) = bottom-center
        self.origin = Vector2(0.5, 0.5)

        # Visual
        self.image = None  # pygame Surface
        self.image_path = None  # Path to image file (for serialization)
        self.color = (255, 255, 255)
        self.visible = True
        self.layer = 0  # Z-order for rendering

    def render(self, screen, camera=None):
        """
        Render sprite to screen with camera offset.

        Args:
            screen: pygame Surface to render to
            camera: Camera instance for viewport transform (optional)
        """
        # Skip rendering if no image
        if not self.image:
            return

        # In editor mode, render invisible objects with transparency (ghosting)
        editor_ghost_mode = False
        if camera and hasattr(camera, 'editor_mode') and camera.editor_mode:
            if not self.visible:
                editor_ghost_mode = True
        else:
            # Runtime mode - don't render invisible objects at all
            if not self.visible:
                return

        import math

        # Calculate screen position
        if camera:
            screen_pos = camera.world_to_screen(self.position)
        else:
            screen_pos = self.position

        # Get original image dimensions
        orig_width = self.image.get_width()
        orig_height = self.image.get_height()

        if self.rotation != 0:
            # First scale the image
            if self.scale != Vector2(1, 1):
                width = int(orig_width * self.scale.x)
                height = int(orig_height * self.scale.y)
                # Check if image has alpha channel
                if self.image.get_flags() & pygame.SRCALPHA:
                    scaled_image = pygame.transform.scale(self.image, (width, height))
                else:
                    # Create temp surface with alpha for proper rotation
                    temp_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                    temp_surface.blit(self.image, (0, 0))
                    scaled_image = pygame.transform.scale(temp_surface, (width, height))
            else:
                # Check if image has alpha channel
                if self.image.get_flags() & pygame.SRCALPHA:
                    scaled_image = self.image
                else:
                    # Create temp surface with alpha for proper rotation
                    temp_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                    temp_surface.blit(self.image, (0, 0))
                    scaled_image = temp_surface

            # Calculate origin point in scaled image coordinates (pixels)
            scaled_width = scaled_image.get_width()
            scaled_height = scaled_image.get_height()
            origin_x_px = self.origin.x * scaled_width
            origin_y_px = self.origin.y * scaled_height

            # Rotate the scaled image (negate for clockwise rotation)
            render_image = pygame.transform.rotate(scaled_image, -self.rotation)

            # Calculate how the origin point moved due to rotation
            # Center of scaled image (rotation pivot point)
            center_x = scaled_width / 2
            center_y = scaled_height / 2

            # Vector from center to origin in scaled image
            dx = origin_x_px - center_x
            dy = origin_y_px - center_y

            # Rotate this vector to track where the origin point should be
            angle_rad = math.radians(self.rotation)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # 2D rotation matrix
            rotated_dx = dx * cos_a - dy * sin_a
            rotated_dy = dx * sin_a + dy * cos_a

            # Origin point in rotated image (relative to rotated image's center)
            rotated_rect = render_image.get_rect()
            rotated_center_x = rotated_rect.width / 2
            rotated_center_y = rotated_rect.height / 2

            rotated_origin_x = rotated_center_x + rotated_dx
            rotated_origin_y = rotated_center_y + rotated_dy

            # Position image so rotated origin point is at screen_pos
            topleft_x = screen_pos.x - rotated_origin_x
            topleft_y = screen_pos.y - rotated_origin_y

        else:
            # No rotation - simpler calculation
            if self.scale != Vector2(1, 1):
                width = int(orig_width * self.scale.x)
                height = int(orig_height * self.scale.y)
                render_image = pygame.transform.scale(self.image, (width, height))
            else:
                render_image = self.image

            image_rect = render_image.get_rect()

            # Calculate position: screen_pos is where the origin point should be
            topleft_x = screen_pos.x - (self.origin.x * image_rect.width)
            topleft_y = screen_pos.y - (self.origin.y * image_rect.height)

        # Blit to surface (with transparency for ghosted editor objects)
        if editor_ghost_mode:
            # Create a copy with alpha transparency for ghosting effect
            ghost_image = render_image.copy()
            ghost_image.set_alpha(100)  # 40% opacity for ghosted objects
            screen.blit(ghost_image, (int(topleft_x), int(topleft_y)))
        else:
            screen.blit(render_image, (int(topleft_x), int(topleft_y)))

    def get_rect(self) -> pygame.Rect:
        """
        Get axis-aligned bounding box for collision.

        Returns:
            pygame.Rect representing sprite bounds
        """
        import math

        if not self.image:
            width = 32  # Default size
            height = 32
            topleft_x = self.position.x - (self.origin.x * width)
            topleft_y = self.position.y - (self.origin.y * height)
            return pygame.Rect(topleft_x, topleft_y, width, height)

        # Get base dimensions with scale applied
        base_width = self.image.get_width() * self.scale.x
        base_height = self.image.get_height() * self.scale.y

        if self.rotation != 0:
            # Calculate the bounding box of the rotated rectangle
            # Convert rotation to radians
            angle_rad = math.radians(abs(self.rotation))

            # Calculate the expanded dimensions needed to contain rotated sprite
            cos_a = abs(math.cos(angle_rad))
            sin_a = abs(math.sin(angle_rad))

            rotated_width = base_width * cos_a + base_height * sin_a
            rotated_height = base_width * sin_a + base_height * cos_a

            # Calculate origin in the scaled image
            origin_x_px = self.origin.x * base_width
            origin_y_px = self.origin.y * base_height

            # Center of scaled image
            center_x = base_width / 2
            center_y = base_height / 2

            # Vector from center to origin
            dx = origin_x_px - center_x
            dy = origin_y_px - center_y

            # Rotate this vector
            angle_rad_signed = math.radians(self.rotation)
            cos_a_signed = math.cos(angle_rad_signed)
            sin_a_signed = math.sin(angle_rad_signed)

            rotated_dx = dx * cos_a_signed - dy * sin_a_signed
            rotated_dy = dx * sin_a_signed + dy * cos_a_signed

            # Origin in rotated bounding box
            rotated_center_x = rotated_width / 2
            rotated_center_y = rotated_height / 2

            rotated_origin_x = rotated_center_x + rotated_dx
            rotated_origin_y = rotated_center_y + rotated_dy

            # Top-left position
            topleft_x = self.position.x - rotated_origin_x
            topleft_y = self.position.y - rotated_origin_y

            return pygame.Rect(
                int(topleft_x),
                int(topleft_y),
                int(rotated_width),
                int(rotated_height)
            )
        else:
            # No rotation - simple calculation
            topleft_x = self.position.x - (self.origin.x * base_width)
            topleft_y = self.position.y - (self.origin.y * base_height)

            return pygame.Rect(
                int(topleft_x),
                int(topleft_y),
                int(base_width),
                int(base_height)
            )
