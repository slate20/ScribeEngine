"""
Edit Scope Indicator - Visual widget showing what code edits will affect.

Helps users understand whether they're editing:
- Instance-specific code (one object)
- Shared behavior class (all objects using this behavior)
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from v2_engine.editor.theme import EditorTheme


class EditScopeIndicator(QWidget):
    """
    Visual indicator showing the scope of current code edits.

    Displays:
    - What you're editing (instance vs shared)
    - Impact radius (this object vs all objects)
    - Visual color coding
    """

    def __init__(self, theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.current_scope = "instance"  # "instance" or "shared"

        self._setup_ui()

    def _setup_ui(self):
        """Create indicator UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Indicator bar
        self.indicator_frame = QFrame()
        indicator_layout = QHBoxLayout(self.indicator_frame)
        indicator_layout.setContentsMargins(
            self.theme.padding_compact,
            self.theme.padding_compact // 2,
            self.theme.padding_compact,
            self.theme.padding_compact // 2
        )

        # Icon
        self.icon_label = QLabel("[Obj]")
        self.icon_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        indicator_layout.addWidget(self.icon_label)

        # Text
        self.text_label = QLabel("Editing: This Object Only")
        self.text_label.setFont(QFont(self.theme.font_family_ui, self.theme.font_size_small))
        indicator_layout.addWidget(self.text_label, 1)

        # Count label (for shared)
        self.count_label = QLabel("")
        self.count_label.setFont(QFont(self.theme.font_family_ui, self.theme.font_size_small, QFont.Weight.Bold))
        indicator_layout.addWidget(self.count_label)

        layout.addWidget(self.indicator_frame)

        # Update styling
        self.set_scope("instance")

    def set_scope(self, scope: str, behavior_name: str = "", instance_count: int = 0):
        """
        Update the indicator to show current edit scope.

        Args:
            scope: "instance" or "shared"
            behavior_name: Name of behavior being edited (for shared scope)
            instance_count: Number of instances using this behavior (for shared scope)
        """
        self.current_scope = scope

        if scope == "instance":
            self.icon_label.setText("[Obj]")
            self.text_label.setText("Editing: This Object Only")
            self.count_label.setText("")
            self.indicator_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme.accent_primary};
                    border-radius: {self.theme.radius_small}px;
                }}
                QLabel {{
                    color: white;
                }}
            """)
        else:  # shared
            self.icon_label.setText("[Class]")
            self.text_label.setText(f"Editing: {behavior_name} (Shared Class)")
            self.count_label.setText(f"Affects {instance_count} object(s)")
            self.indicator_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.theme.warning};
                    border-radius: {self.theme.radius_small}px;
                }}
                QLabel {{
                    color: {self.theme.background_dark};
                    font-weight: bold;
                }}
            """)

    def get_scope(self) -> str:
        """Get current edit scope."""
        return self.current_scope
