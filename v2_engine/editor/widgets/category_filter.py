"""
CategoryFilterBar widget - Pill-based category filtering for Behavior Browser.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from v2_engine.components.component_registry import ComponentCategory
from v2_engine.editor.theme import EditorTheme


class CategoryFilterBar(QWidget):
    """
    Horizontal bar of clickable category filter pills.

    Features:
    - Toggle categories on/off (multi-select)
    - Color-coded pills (active state reinforces category colors)
    - "Clear Filters" button to deselect all categories
    - All categories start selected by default
    - Emits signal when filters change
    """

    filters_changed = pyqtSignal(list)  # Emits list of active categories

    def __init__(self, categories: list[ComponentCategory], theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.theme = theme
        self.active_categories = set(categories)  # Start with all active
        self.category_buttons = {}

        self._setup_ui()

    def _setup_ui(self):
        """Create filter pill buttons."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.theme.spacing_small)

        # "Clear Filters" button (shows all categories)
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self._on_clear_filters_clicked)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_strong};
                border-radius: {self.theme.radius_large}px;
                padding: 4px 12px;
                font-size: {self.theme.font_size_small}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.background_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.background_dark};
            }}
        """)
        clear_btn.setFixedHeight(28)
        layout.addWidget(clear_btn)
        self.clear_button = clear_btn

        # Category buttons
        for category in self.categories:
            btn = QPushButton(category.value)
            btn.setCheckable(True)
            btn.setChecked(True)  # Start active (all categories shown)
            btn.clicked.connect(lambda checked, c=category: self._on_category_clicked(c, checked))

            # Get category color
            color = self.theme.get_category_color(category.value)
            self._style_pill_button(btn, color, True)

            layout.addWidget(btn)
            self.category_buttons[category] = btn

        layout.addStretch()

    def _style_pill_button(self, button: QPushButton, color: str, active: bool):
        """
        Apply pill styling to button.

        Args:
            button: Button to style
            color: Category color
            active: Whether button is active
        """
        font = QFont()
        font.setPointSize(self.theme.font_size_small)
        button.setFont(font)
        button.setFixedHeight(28)

        if active:
            # Active: colored text, transparent bg, colored border
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color};
                    border: 1px solid {color};
                    border-radius: {self.theme.radius_large}px;
                    padding: 4px 12px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.background_hover};
                }}
                QPushButton:pressed {{
                    background-color: {self.theme.background_dark};
                }}
            """)
        else:
            # Inactive: grayed out with reduced opacity
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.theme.text_disabled};
                    border: 1px solid {self.theme.border_subtle};
                    border-radius: {self.theme.radius_large}px;
                    padding: 4px 12px;
                    opacity: 0.5;
                }}
                QPushButton:hover {{
                    background-color: {self.theme.background_hover};
                    opacity: 0.7;
                }}
            """)

    def _on_clear_filters_clicked(self):
        """Handle "Clear Filters" button click - deselect all categories."""
        self.active_categories = set()  # Clear all active categories

        # Uncheck all category buttons
        for category, btn in self.category_buttons.items():
            btn.setChecked(False)
            color = self.theme.get_category_color(category.value)
            self._style_pill_button(btn, color, False)

        self.filters_changed.emit(list(self.active_categories))

    def _on_category_clicked(self, category: ComponentCategory, checked: bool):
        """
        Handle category button toggle (multi-select).

        Args:
            category: Category that was clicked
            checked: New checked state
        """
        btn = self.category_buttons[category]
        color = self.theme.get_category_color(category.value)

        if checked:
            # Add to active categories
            self.active_categories.add(category)
            self._style_pill_button(btn, color, True)
        else:
            # Remove from active categories
            self.active_categories.discard(category)
            self._style_pill_button(btn, color, False)

        self.filters_changed.emit(list(self.active_categories))

    def get_active_categories(self) -> list[ComponentCategory]:
        """Get list of currently active categories."""
        return list(self.active_categories)
