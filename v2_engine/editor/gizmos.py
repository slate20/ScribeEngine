"""
Visual editor gizmos for sprite manipulation.
"""

import pygame
from v2_engine.utils.math import Vector2


def draw_grid(screen: pygame.Surface, camera, screen_size: tuple):
    """
    Draw editor grid.

    Args:
        screen: Pygame surface to draw on
        camera: EditorCamera instance
        screen_size: (width, height) of screen
    """
    grid_color = (40, 40, 40)
    grid_size = camera.grid_size

    # Calculate visible grid range
    start_x = int(camera.position.x / grid_size) * grid_size
    start_y = int(camera.position.y / grid_size) * grid_size
    end_x = start_x + int(screen_size[0] / camera.zoom) + grid_size
    end_y = start_y + int(screen_size[1] / camera.zoom) + grid_size

    # Draw vertical lines
    x = start_x
    while x < end_x:
        screen_x = int((x - camera.position.x) * camera.zoom)
        if 0 <= screen_x < screen_size[0]:
            pygame.draw.line(screen, grid_color, (screen_x, 0), (screen_x, screen_size[1]), 1)
        x += grid_size

    # Draw horizontal lines
    y = start_y
    while y < end_y:
        screen_y = int((y - camera.position.y) * camera.zoom)
        if 0 <= screen_y < screen_size[1]:
            pygame.draw.line(screen, grid_color, (0, screen_y), (screen_size[0], screen_y), 1)
        y += grid_size

    # Draw origin axes (brighter)
    origin_color = (80, 80, 80)
    origin_screen = camera.world_to_screen(Vector2(0, 0))

    # X axis
    if 0 <= origin_screen.x < screen_size[0]:
        pygame.draw.line(screen, origin_color,
                        (int(origin_screen.x), 0),
                        (int(origin_screen.x), screen_size[1]), 2)

    # Y axis
    if 0 <= origin_screen.y < screen_size[1]:
        pygame.draw.line(screen, origin_color,
                        (0, int(origin_screen.y)),
                        (screen_size[0], int(origin_screen.y)), 2)


def draw_sprite_gizmo(screen: pygame.Surface, sprite, camera, selected: bool = False):
    """
    Draw editor handles for a sprite.

    Args:
        screen: Pygame surface to draw on
        sprite: Sprite object to draw gizmo for
        camera: EditorCamera instance
        selected: Whether this sprite is currently selected
    """
    # Get sprite rect
    rect = sprite.get_rect()
    screen_rect = camera.world_to_screen_rect(rect)

    # Draw bounding box
    color = (0, 255, 0) if selected else (255, 255, 255)
    thickness = 2 if selected else 1
    pygame.draw.rect(screen, color, screen_rect, thickness)

    # Draw origin point
    origin_world = sprite.position
    origin_screen = camera.world_to_screen(origin_world)

    # Origin circle
    pygame.draw.circle(screen, (255, 0, 255),
                      (int(origin_screen.x), int(origin_screen.y)), 5)

    # Origin crosshair
    crosshair_size = 8
    pygame.draw.line(screen, (255, 0, 255),
                     (int(origin_screen.x - crosshair_size), int(origin_screen.y)),
                     (int(origin_screen.x + crosshair_size), int(origin_screen.y)), 1)
    pygame.draw.line(screen, (255, 0, 255),
                     (int(origin_screen.x), int(origin_screen.y - crosshair_size)),
                     (int(origin_screen.x), int(origin_screen.y + crosshair_size)), 1)

    # If selected, draw additional info
    if selected:
        # Draw sprite name above sprite (use sprite.name if available, otherwise class name)
        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
        font = pygame.font.Font(None, 20)
        text = font.render(sprite_name, True, (255, 255, 0))
        text_pos = (int(screen_rect.x), int(screen_rect.y - 20))
        screen.blit(text, text_pos)


def draw_selection_box(screen: pygame.Surface, start_pos: Vector2, end_pos: Vector2):
    """
    Draw selection box for multi-select.

    Args:
        screen: Pygame surface to draw on
        start_pos: Screen position where selection started
        end_pos: Current screen position
    """
    rect = pygame.Rect(
        min(start_pos.x, end_pos.x),
        min(start_pos.y, end_pos.y),
        abs(end_pos.x - start_pos.x),
        abs(end_pos.y - start_pos.y)
    )
    pygame.draw.rect(screen, (100, 150, 255), rect, 2)
