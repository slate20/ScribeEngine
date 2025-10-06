"""
Visual editor gizmos for sprite manipulation.
"""

import pygame
from v2_engine.utils.math import Vector2


def draw_dashed_rect(screen: pygame.Surface, color: tuple, rect: pygame.Rect, thickness: int = 1, dash_length: int = 5):
    """
    Draw a dashed rectangle.

    Args:
        screen: Pygame surface to draw on
        color: RGB color tuple
        rect: Rectangle to draw
        thickness: Line thickness
        dash_length: Length of each dash segment
    """
    # Top edge
    x = rect.left
    while x < rect.right:
        end_x = min(x + dash_length, rect.right)
        pygame.draw.line(screen, color, (x, rect.top), (end_x, rect.top), thickness)
        x += dash_length * 2

    # Bottom edge
    x = rect.left
    while x < rect.right:
        end_x = min(x + dash_length, rect.right)
        pygame.draw.line(screen, color, (x, rect.bottom), (end_x, rect.bottom), thickness)
        x += dash_length * 2

    # Left edge
    y = rect.top
    while y < rect.bottom:
        end_y = min(y + dash_length, rect.bottom)
        pygame.draw.line(screen, color, (rect.left, y), (rect.left, end_y), thickness)
        y += dash_length * 2

    # Right edge
    y = rect.top
    while y < rect.bottom:
        end_y = min(y + dash_length, rect.bottom)
        pygame.draw.line(screen, color, (rect.right, y), (rect.right, end_y), thickness)
        y += dash_length * 2


def draw_grid(screen: pygame.Surface, camera, screen_size: tuple):
    """
    Draw editor grid.

    Args:
        screen: Pygame surface to draw on
        camera: EditorCamera instance
        screen_size: (width, height) of screen
    """
    # Create semi-transparent surface for grid
    grid_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    grid_color = (120, 120, 120, 80)  # Light gray with alpha for visibility
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
            pygame.draw.line(grid_surface, grid_color, (screen_x, 0), (screen_x, screen_size[1]), 1)
        x += grid_size

    # Draw horizontal lines
    y = start_y
    while y < end_y:
        screen_y = int((y - camera.position.y) * camera.zoom)
        if 0 <= screen_y < screen_size[1]:
            pygame.draw.line(grid_surface, grid_color, (0, screen_y), (screen_size[0], screen_y), 1)
        y += grid_size

    # Draw origin axes (brighter and more opaque)
    origin_color = (180, 180, 180, 150)
    origin_screen = camera.world_to_screen(Vector2(0, 0))

    # X axis
    if 0 <= origin_screen.x < screen_size[0]:
        pygame.draw.line(grid_surface, origin_color,
                        (int(origin_screen.x), 0),
                        (int(origin_screen.x), screen_size[1]), 2)

    # Y axis
    if 0 <= origin_screen.y < screen_size[1]:
        pygame.draw.line(grid_surface, origin_color,
                        (0, int(origin_screen.y)),
                        (screen_size[0], int(origin_screen.y)), 2)

    # Blit grid surface onto screen with alpha blending
    screen.blit(grid_surface, (0, 0))


def draw_sprite_gizmo(screen: pygame.Surface, sprite, camera, selected: bool = False):
    """
    Draw editor handles for a game object (sprite or logic object).

    Args:
        screen: Pygame surface to draw on
        sprite: GameObject (SpriteObject or LogicObject) to draw gizmo for
        camera: EditorCamera instance
        selected: Whether this object is currently selected
    """
    from v2_engine.sprites.sprite_object import SpriteObject
    from v2_engine.core.logic_object import LogicObject

    # Check if object is visible (for ghosting effect)
    is_visible = getattr(sprite, 'visible', True)

    # Draw position marker for all objects
    origin_world = sprite.position
    origin_screen = camera.world_to_screen(origin_world)

    if isinstance(sprite, SpriteObject):
        # SpriteObject: Draw bounding box + origin
        if hasattr(sprite, 'get_rect'):
            rect = sprite.get_rect()
            screen_rect = camera.world_to_screen_rect(rect)

            # Draw bounding box (ghosted if invisible)
            if is_visible:
                color = (0, 255, 0) if selected else (255, 255, 255)
            else:
                # Ghost effect - dimmed, dashed appearance
                color = (0, 128, 0) if selected else (128, 128, 128)

            thickness = 2 if selected else 1

            # Draw dashed rect for invisible objects
            if not is_visible:
                draw_dashed_rect(screen, color, screen_rect, thickness)
            else:
                pygame.draw.rect(screen, color, screen_rect, thickness)

        # Origin circle (magenta for visibility, ghosted if invisible)
        origin_color = (255, 0, 255) if is_visible else (128, 0, 128)
        pygame.draw.circle(screen, origin_color,
                          (int(origin_screen.x), int(origin_screen.y)), 5)

        # Origin crosshair
        crosshair_size = 8
        pygame.draw.line(screen, origin_color,
                         (int(origin_screen.x - crosshair_size), int(origin_screen.y)),
                         (int(origin_screen.x + crosshair_size), int(origin_screen.y)), 1)
        pygame.draw.line(screen, origin_color,
                         (int(origin_screen.x), int(origin_screen.y - crosshair_size)),
                         (int(origin_screen.x), int(origin_screen.y + crosshair_size)), 1)

    elif isinstance(sprite, LogicObject):
        # LogicObject: Draw yellow/gold circle indicator (no bounding box)
        # Ghosted if invisible
        if is_visible:
            color = (255, 200, 80) if selected else (200, 150, 60)  # Gold/yellow
        else:
            color = (128, 100, 40) if selected else (100, 75, 30)  # Dimmed gold

        circle_size = 8 if selected else 6

        # Draw circle
        pygame.draw.circle(screen, color,
                          (int(origin_screen.x), int(origin_screen.y)), circle_size, 2)

        # Draw center dot
        pygame.draw.circle(screen, color,
                          (int(origin_screen.x), int(origin_screen.y)), 2)

        # Draw directional arrow if rotated (shows rotation)
        if sprite.rotation != 0:
            import math
            angle_rad = math.radians(sprite.rotation)
            arrow_length = 15
            end_x = origin_screen.x + arrow_length * math.cos(angle_rad)
            end_y = origin_screen.y - arrow_length * math.sin(angle_rad)
            pygame.draw.line(screen, color,
                           (int(origin_screen.x), int(origin_screen.y)),
                           (int(end_x), int(end_y)), 2)

    # If selected, draw origin offset visualization
    if selected:
        sprite_origin = getattr(sprite, 'origin', Vector2(0.5, 0.5))

        # Only draw offset indicator if origin is not at center
        if sprite_origin.x != 0.5 or sprite_origin.y != 0.5:
            # Calculate where center would be
            if hasattr(sprite, 'image') and sprite.image:
                base_width = sprite.image.get_width()
                base_height = sprite.image.get_height()
                sprite_scale = getattr(sprite, 'scale', Vector2(1, 1))

                # Center position in world space
                center_offset_x = (0.5 - sprite_origin.x) * base_width * sprite_scale.x
                center_offset_y = (0.5 - sprite_origin.y) * base_height * sprite_scale.y
                center_world_x = origin_world.x + center_offset_x
                center_world_y = origin_world.y + center_offset_y
                center_screen = camera.world_to_screen(Vector2(center_world_x, center_world_y))

                # Draw line from origin to center
                pygame.draw.line(screen, (180, 0, 180, 100),
                               (int(origin_screen.x), int(origin_screen.y)),
                               (int(center_screen.x), int(center_screen.y)), 1)

                # Draw small circle at center
                pygame.draw.circle(screen, (180, 0, 180, 100),
                                 (int(center_screen.x), int(center_screen.y)), 3, 1)

        # Draw object name above object (use sprite.name if available, otherwise class name)
        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
        font = pygame.font.Font(None, 20)
        # Ghost the text color if invisible
        text_color = (255, 255, 0) if is_visible else (128, 128, 0)
        text = font.render(sprite_name, True, text_color)

        # Position text above the object
        # For SpriteObjects with bounding boxes, use screen_rect
        # For LogicObjects, use origin_screen position
        if isinstance(sprite, SpriteObject) and hasattr(sprite, 'get_rect'):
            rect = sprite.get_rect()
            screen_rect = camera.world_to_screen_rect(rect)
            text_pos = (int(screen_rect.x), int(screen_rect.y - 20))
        else:
            # LogicObject - position above the circle marker
            text_pos = (int(origin_screen.x - text.get_width() / 2), int(origin_screen.y - 25))

        screen.blit(text, text_pos)


def draw_rotate_gizmo(screen: pygame.Surface, sprite, camera):
    """
    Draw rotation gizmo - a circular handle around the sprite.

    Args:
        screen: Pygame surface to draw on
        sprite: Sprite object to draw gizmo for
        camera: EditorCamera instance
    """
    import math

    # Get sprite world position and convert to screen
    world_center = sprite.position
    screen_center = camera.world_to_screen(world_center)
    center_x = int(screen_center.x)
    center_y = int(screen_center.y)

    # Calculate radius based on sprite size
    rect = sprite.get_rect()
    screen_rect = camera.world_to_screen_rect(rect)
    radius = int(max(screen_rect.width, screen_rect.height) * 0.6) + 20

    # Draw circle guide
    pygame.draw.circle(screen, (100, 200, 255, 150), (center_x, center_y), radius, 2)

    # Get current rotation and calculate handle position
    current_rotation = getattr(sprite, 'rotation', 0)
    # Handle starts at top (-90°) and rotates with sprite
    handle_angle = -90 + current_rotation  # Add rotation (pygame measures counterclockwise from right)
    handle_x = center_x + int(radius * math.cos(math.radians(handle_angle)))
    handle_y = center_y + int(radius * math.sin(math.radians(handle_angle)))

    # Handle circle (clickable area)
    pygame.draw.circle(screen, (100, 200, 255), (handle_x, handle_y), 8)
    pygame.draw.circle(screen, (255, 255, 255), (handle_x, handle_y), 8, 2)

    # Draw rotation icon/arc indicators (rotate with sprite)
    arc_color = (100, 200, 255, 100)
    for offset_angle in [-30, -15, 15, 30]:
        angle_rad = math.radians(handle_angle + offset_angle)
        arc_x = center_x + int(radius * 0.9 * math.cos(angle_rad))
        arc_y = center_y + int(radius * 0.9 * math.sin(angle_rad))
        pygame.draw.line(screen, arc_color, (center_x, center_y), (arc_x, arc_y), 1)


def draw_scale_gizmo(screen: pygame.Surface, sprite, camera):
    """
    Draw scale gizmo - corner handles for resizing the sprite.

    Args:
        screen: Pygame surface to draw on
        sprite: Sprite object to draw gizmo for
        camera: EditorCamera instance
    """
    # Get sprite rect
    rect = sprite.get_rect()
    screen_rect = camera.world_to_screen_rect(rect)

    # Draw bounding box with thicker line
    pygame.draw.rect(screen, (255, 150, 0), screen_rect, 2)

    # Draw corner handles
    handle_size = 8
    corners = [
        (screen_rect.left, screen_rect.top),      # Top-left
        (screen_rect.right, screen_rect.top),     # Top-right
        (screen_rect.left, screen_rect.bottom),   # Bottom-left
        (screen_rect.right, screen_rect.bottom)   # Bottom-right
    ]

    for corner_x, corner_y in corners:
        # Draw filled square handle
        handle_rect = pygame.Rect(
            int(corner_x - handle_size / 2),
            int(corner_y - handle_size / 2),
            handle_size,
            handle_size
        )
        pygame.draw.rect(screen, (255, 150, 0), handle_rect)
        pygame.draw.rect(screen, (255, 255, 255), handle_rect, 1)

    # Draw edge handles (for non-uniform scaling)
    edge_handle_size = 6
    edges = [
        (screen_rect.centerx, screen_rect.top),     # Top
        (screen_rect.centerx, screen_rect.bottom),  # Bottom
        (screen_rect.left, screen_rect.centery),    # Left
        (screen_rect.right, screen_rect.centery)    # Right
    ]

    for edge_x, edge_y in edges:
        # Draw filled circle handle
        pygame.draw.circle(screen, (255, 150, 0), (int(edge_x), int(edge_y)), edge_handle_size)
        pygame.draw.circle(screen, (255, 255, 255), (int(edge_x), int(edge_y)), edge_handle_size, 1)


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


def draw_scale_feedback(screen: pygame.Surface, sprite, camera, mouse_x: int, mouse_y: int):
    """
    Draw scale percentage feedback during scaling.

    Args:
        screen: Pygame surface to draw on
        sprite: Sprite being scaled
        camera: EditorCamera instance
        mouse_x: Mouse X position (screen space)
        mouse_y: Mouse Y position (screen space)
    """
    # Get sprite scale
    sprite_scale = getattr(sprite, 'scale', (1, 1))
    if hasattr(sprite_scale, 'x'):
        scale_x = sprite_scale.x
        scale_y = sprite_scale.y
    else:
        scale_x, scale_y = sprite_scale

    # Format scale text
    scale_text = f"Scale: {scale_x:.2f}x, {scale_y:.2f}x"

    # Render text
    font = pygame.font.Font(None, 24)
    text_surface = font.render(scale_text, True, (255, 255, 255))

    # Position near mouse cursor (offset slightly to avoid covering sprite)
    text_x = mouse_x + 20
    text_y = mouse_y - 30

    # Draw background for text
    bg_rect = text_surface.get_rect()
    bg_rect.x = text_x - 5
    bg_rect.y = text_y - 3
    bg_rect.width += 10
    bg_rect.height += 6

    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    screen.blit(bg_surface, (bg_rect.x, bg_rect.y))

    # Draw text
    screen.blit(text_surface, (text_x, text_y))


def draw_viewport_bounds(screen: pygame.Surface, camera, viewport_size: tuple):
    """
    Draw viewport bounds rectangle showing game camera area.

    Args:
        screen: Pygame surface to draw on
        camera: EditorCamera instance
        viewport_size: (width, height) of game viewport
    """
    # Create semi-transparent surface
    bounds_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    # Calculate viewport bounds in world space
    viewport_world_rect = pygame.Rect(0, 0, viewport_size[0], viewport_size[1])

    # Convert to screen space
    viewport_screen_rect = camera.world_to_screen_rect(viewport_world_rect)

    # Draw border rectangle
    border_color = (255, 200, 0, 200)  # Orange with alpha
    pygame.draw.rect(bounds_surface, border_color, viewport_screen_rect, 3)

    # Draw corner markers
    corner_size = 20
    corners = [
        (viewport_screen_rect.left, viewport_screen_rect.top),  # Top-left
        (viewport_screen_rect.right, viewport_screen_rect.top),  # Top-right
        (viewport_screen_rect.left, viewport_screen_rect.bottom),  # Bottom-left
        (viewport_screen_rect.right, viewport_screen_rect.bottom)  # Bottom-right
    ]

    for corner_x, corner_y in corners:
        # Draw L-shaped corner marker
        # Horizontal line
        if corner_x == viewport_screen_rect.left:
            pygame.draw.line(bounds_surface, border_color,
                           (corner_x, corner_y),
                           (corner_x + corner_size, corner_y), 3)
        else:
            pygame.draw.line(bounds_surface, border_color,
                           (corner_x, corner_y),
                           (corner_x - corner_size, corner_y), 3)

        # Vertical line
        if corner_y == viewport_screen_rect.top:
            pygame.draw.line(bounds_surface, border_color,
                           (corner_x, corner_y),
                           (corner_x, corner_y + corner_size), 3)
        else:
            pygame.draw.line(bounds_surface, border_color,
                           (corner_x, corner_y),
                           (corner_x, corner_y - corner_size), 3)

    # Draw label
    font = pygame.font.Font(None, 24)
    label_text = f"Game Viewport ({viewport_size[0]}x{viewport_size[1]})"
    text_surface = font.render(label_text, True, (255, 200, 0, 255))

    # Position label at top-center of viewport bounds
    label_x = viewport_screen_rect.centerx - text_surface.get_width() // 2
    label_y = viewport_screen_rect.top - 30

    # Draw background for label
    label_bg = pygame.Surface((text_surface.get_width() + 10, text_surface.get_height() + 6), pygame.SRCALPHA)
    label_bg.fill((0, 0, 0, 180))
    bounds_surface.blit(label_bg, (label_x - 5, label_y - 3))
    bounds_surface.blit(text_surface, (label_x, label_y))

    # Blit to screen
    screen.blit(bounds_surface, (0, 0))
