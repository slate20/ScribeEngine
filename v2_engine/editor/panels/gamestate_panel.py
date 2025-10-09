"""
GameState Panel for Scribe Engine V2 Editor

Displays global game state including variables, persistent entities, and scene states.
"""

from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from v2_engine.core.game_state import get_game_state


class GameStatePanel(QDockWidget):
    """
    GameState debug panel showing:
    - Global variables
    - Persistent entities
    - Scene states
    """

    def __init__(self, parent, theme):
        super().__init__("Game State", parent)
        self.theme = theme
        self.editor = parent

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )

        self._setup_ui()

    def _setup_ui(self):
        """Setup the game state panel UI."""
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        info_label = QLabel("Global game state and persistent entities")
        info_label.setProperty("type", "caption")  # Uses theme caption style
        layout.addWidget(info_label)

        # Tree widget to display state
        self.gamestate_tree = QTreeWidget()
        self.gamestate_tree.setHeaderLabels(["Key", "Value"])
        self.gamestate_tree.setAlternatingRowColors(True)
        layout.addWidget(self.gamestate_tree)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.update)
        layout.addWidget(refresh_btn)

        self.setWidget(container)

    def update(self):
        """Update the GameState panel with current state."""
        game_state = get_game_state()
        self.gamestate_tree.clear()

        # Add variables section
        variables_item = QTreeWidgetItem(
            self.gamestate_tree,
            ["Variables", f"({len(game_state.variables)} total)"]
        )
        variables_item.setExpanded(True)

        for key, value in sorted(game_state.variables.items()):
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            QTreeWidgetItem(variables_item, [key, value_str])

        # Add persistent entities section
        entities_item = QTreeWidgetItem(
            self.gamestate_tree,
            ["Persistent Entities", f"({len(game_state.persistent_entities)} total)"]
        )
        entities_item.setExpanded(True)

        for entity_id, sprite in sorted(game_state.persistent_entities.items()):
            sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)
            sprite_pos = getattr(sprite, 'position', None)
            if sprite_pos:
                info = f"{sprite_name} at ({sprite_pos.x:.1f}, {sprite_pos.y:.1f})"
            else:
                info = sprite_name
            QTreeWidgetItem(entities_item, [entity_id, info])

        # Add scene states section
        scene_states_item = QTreeWidgetItem(
            self.gamestate_tree,
            ["Scene States", f"({len(game_state.scene_states)} scenes)"]
        )
        scene_states_item.setExpanded(False)  # Collapsed by default

        for scene_name, scene_data in sorted(game_state.scene_states.items()):
            scene_item = QTreeWidgetItem(
                scene_states_item,
                [scene_name, f"({len(scene_data)} objects)"]
            )
            for object_id, object_data in sorted(scene_data.items()):
                object_item = QTreeWidgetItem(
                    scene_item,
                    [object_id, f"({len(object_data)} properties)"]
                )
                for key, value in sorted(object_data.items()):
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    QTreeWidgetItem(object_item, [key, value_str])
