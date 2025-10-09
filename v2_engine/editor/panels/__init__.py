"""
Editor UI Panels

Modular panel components for the Scribe Engine V2 Editor.
"""

from v2_engine.editor.panels.hierarchy_panel import HierarchyPanel
from v2_engine.editor.panels.gamestate_panel import GameStatePanel
from v2_engine.editor.panels.properties_panel import PropertiesPanel
from v2_engine.editor.panels.viewport_panel import ViewportPanel
from v2_engine.editor.panels.code_panel import CodePanel, SplitCodePanel

__all__ = [
    'HierarchyPanel',
    'GameStatePanel',
    'PropertiesPanel',
    'ViewportPanel',
    'CodePanel',
    'SplitCodePanel',
]
