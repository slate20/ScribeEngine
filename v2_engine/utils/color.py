"""
Color utilities for Scribe Engine V2.

Common color constants and utilities.
"""

# Common colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# UI colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
PLATFORM_GRAY = (100, 100, 100)


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex string like "#FF0000" or "FF0000"

    Returns:
        Tuple of (r, g, b) values
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex string.

    Args:
        r, g, b: Color components (0-255)

    Returns:
        Hex string like "#FF0000"
    """
    return f"#{r:02x}{g:02x}{b:02x}"
