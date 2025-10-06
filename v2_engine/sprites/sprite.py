"""
Backward compatibility alias for Sprite -> SpriteObject.

DEPRECATED: Use SpriteObject directly in new code.
This file maintains compatibility with existing code.
"""

# Import SpriteObject and alias it as Sprite for backward compatibility
from v2_engine.sprites.sprite_object import SpriteObject as Sprite

# Re-export for convenience
__all__ = ['Sprite']
