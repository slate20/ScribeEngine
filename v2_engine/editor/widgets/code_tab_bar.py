"""
Code Tab Bar - Smart tab widget for split view code editing.

Features:
- Visual distinction between instance code and shared behavior classes
- Warning banners for shared code editing
- Quick actions for instance-specific customization
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from v2_engine.editor.theme import EditorTheme


class CodeTabBar(QTabWidget):
    """
    Specialized tab widget for code editing with visual indicators.

    Features:
    - Instance code tab (object-specific)
    - Behavior class tabs (shared across instances)
    - Visual warnings and indicators
    - Quick actions for customization

    Signals:
        switch_to_instance_edit: Emitted when user wants to edit instance-only code
        behavior_file_changed: Emitted when behavior class file is modified
    """

    switch_to_instance_edit = pyqtSignal()
    behavior_file_changed = pyqtSignal(str)  # file_path

    def __init__(self, theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.current_sprite = None
        self.has_instance_overrides = False

        self._setup_styling()

    def _setup_styling(self):
        """Apply theme styling to tab bar."""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.theme.border_subtle};
                background-color: {self.theme.background_mid};
            }}
            QTabBar::tab {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                padding: 8px 16px;
                border: 1px solid {self.theme.border_subtle};
                border-bottom: none;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme.background_mid};
                border-bottom: 2px solid {self.theme.accent_primary};
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme.background_hover};
            }}
        """)

    def set_instance_tab(self, tab_widget: QWidget, has_overrides: bool = False):
        """
        Add/update the instance code tab.

        Args:
            tab_widget: Widget containing the code editor for instance code
            has_overrides: Whether this instance has custom overrides
        """
        # Remove existing instance tab if present
        if self.count() > 0 and self.tabText(0).startswith("[Obj]"):
            self.removeTab(0)

        # Create tab with indicator
        label = "[Obj] This Object"
        if has_overrides:
            label += " *"  # Asterisk indicates custom overrides

        self.insertTab(0, tab_widget, label)

        # Set tooltip
        tooltip = "Object-specific code (affects only this object)"
        if has_overrides:
            tooltip += "\n* Has custom overrides"
        self.setTabToolTip(0, tooltip)

        self.has_instance_overrides = has_overrides

    def add_behavior_tab(self, tab_widget: QWidget, behavior_name: str, file_path: str):
        """
        Add a behavior class tab with warning banner.

        Args:
            tab_widget: Widget containing the code editor for behavior class
            behavior_name: Name of the behavior class
            file_path: Path to the behavior file
        """
        # Create container with warning banner
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Warning banner
        banner = self._create_warning_banner(behavior_name)
        layout.addWidget(banner)

        # Code editor
        layout.addWidget(tab_widget)

        # Add tab with shared indicator
        label = f"[Class] {behavior_name} (Shared)"
        self.addTab(container, label)

        # Set tooltip
        self.setTabToolTip(
            self.count() - 1,
            f"Shared behavior class\nChanges affect ALL objects using {behavior_name}"
        )

        # Store file path for later
        container.setProperty("file_path", file_path)

    def _create_warning_banner(self, behavior_name: str) -> QWidget:
        """Create compact warning banner for shared behavior editing."""
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.warning};
                border-bottom: 1px solid {self.theme.error};
            }}
        """)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Warning icon and compact text
        warning_label = QLabel(f"Shared Class - affects all {behavior_name} instances")
        warning_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme.background_dark};
                font-weight: bold;
                font-size: {self.theme.font_size_small}px;
            }}
        """)
        layout.addWidget(warning_label, 1)

        # Compact action button
        edit_instance_btn = QPushButton("Edit Instance Instead")
        edit_instance_btn.clicked.connect(self._on_edit_instance_clicked)
        edit_instance_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_dark};
                color: white;
                border: none;
                border-radius: {self.theme.radius_small}px;
                padding: 4px 10px;
                font-size: {self.theme.font_size_small}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.background_light};
            }}
        """)
        layout.addWidget(edit_instance_btn)

        return banner

    def _on_edit_instance_clicked(self):
        """Handle 'Edit This Object Only' button click."""
        # Switch to instance tab
        self.setCurrentIndex(0)

        # Emit signal for additional handling (e.g., highlight code section)
        self.switch_to_instance_edit.emit()

    def clear_tabs(self):
        """Remove all tabs."""
        while self.count() > 0:
            self.removeTab(0)

    def get_current_file_path(self) -> str:
        """Get file path of currently selected tab."""
        current_widget = self.currentWidget()
        if current_widget:
            return current_widget.property("file_path") or ""
        return ""
