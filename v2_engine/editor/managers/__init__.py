"""
Editor Manager Classes

Modular manager components for the Scribe Engine V2 Editor.
"""

from v2_engine.editor.managers.selection_manager import SelectionManager
from v2_engine.editor.managers.playback_manager import PlaybackManager
from v2_engine.editor.managers.scene_manager_ui import SceneManagerUI

__all__ = [
    'SelectionManager',
    'PlaybackManager',
    'SceneManagerUI',
]

# TODO: Add as they are implemented
# from v2_engine.editor.managers.viewport_manager import ViewportManager
