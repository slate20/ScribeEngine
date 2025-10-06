"""
EditorTheme - Centralized styling system for Scribe Engine V2 Editor

Provides consistent colors, spacing, typography, and styling throughout the Qt editor.
All visual styling should come from this theme, not hardcoded values.
"""

from dataclasses import dataclass, field
from typing import Dict
import json
import os


@dataclass
class EditorTheme:
    """
    Centralized theme configuration for Qt editor.

    All colors, spacing, typography defined in one place.
    Generates complete Qt stylesheet from these values.
    """

    # === Base Colors ===
    background_dark: str = "#1e1e1e"      # Main editor background
    background_mid: str = "#252526"       # Panel backgrounds
    background_light: str = "#2d2d30"     # Raised elements (buttons, cards)
    background_hover: str = "#3e3e42"     # Hover states

    border_subtle: str = "#3c3c41"        # Subtle separators
    border_strong: str = "#555555"        # Strong dividers

    text_primary: str = "#cccccc"         # Main text
    text_secondary: str = "#969696"       # Labels, hints
    text_disabled: str = "#6e6e6e"        # Disabled state

    accent_primary: str = "#0e639c"       # Selected items, focus
    accent_hover: str = "#1177bb"         # Hover on accented items
    accent_bright: str = "#4fc3f7"        # Highlights, links

    success: str = "#4ec9b0"              # Success states
    warning: str = "#ce9178"              # Warnings
    error: str = "#f48771"                # Errors
    info: str = "#3794ff"                 # Information

    # === Component Category Colors ===
    category_physics: str = "#ff9800"     # Orange - RigidBody, Colliders
    category_rendering: str = "#2196f3"   # Blue - Sprites, Cameras
    category_gameplay: str = "#4caf50"    # Green - Controllers, Logic
    category_ai: str = "#9c27b0"          # Purple - AI behaviors
    category_audio: str = "#00bcd4"       # Cyan - Audio sources
    category_interaction: str = "#ff5722" # Red-Orange - Triggers, Dialogue

    # === Spacing System ===
    spacing_tiny: int = 4       # Tight gaps (inside buttons)
    spacing_small: int = 8      # Standard gaps (between elements)
    spacing_medium: int = 12    # Section gaps
    spacing_large: int = 16     # Major section gaps
    spacing_xlarge: int = 24    # Panel gaps

    padding_compact: int = 6    # Button padding
    padding_normal: int = 10    # Panel padding
    padding_spacious: int = 16  # Card padding

    # === Typography ===
    font_family_ui: str = "Segoe UI, Arial, sans-serif"
    font_family_code: str = "Consolas, 'Courier New', monospace"

    font_size_small: int = 10   # Hints, captions
    font_size_normal: int = 11  # Standard UI text
    font_size_large: int = 13   # Headers, emphasis
    font_size_xlarge: int = 16  # Section titles

    # === Border Radius ===
    radius_small: int = 3       # Buttons, inputs
    radius_medium: int = 4      # Cards, panels
    radius_large: int = 6       # Modals, dialogs

    def get_category_color(self, category: str) -> str:
        """
        Get color for a component category.

        Args:
            category: Category name (e.g., "Physics", "Rendering")

        Returns:
            Hex color code
        """
        category_lower = category.lower()

        if "physics" in category_lower or "collision" in category_lower:
            return self.category_physics
        elif "render" in category_lower or "sprite" in category_lower or "camera" in category_lower:
            return self.category_rendering
        elif "gameplay" in category_lower or "controller" in category_lower or "input" in category_lower:
            return self.category_gameplay
        elif "ai" in category_lower or "behavior" in category_lower:
            return self.category_ai
        elif "audio" in category_lower or "sound" in category_lower:
            return self.category_audio
        elif "interaction" in category_lower or "trigger" in category_lower or "dialogue" in category_lower:
            return self.category_interaction
        else:
            return self.accent_primary  # Default

    def get_stylesheet(self) -> str:
        """
        Generate complete Qt stylesheet from theme values.

        Returns:
            Complete CSS-like stylesheet string for Qt
        """
        return f"""
            /* === Global Styles === */
            QMainWindow {{
                background-color: {self.background_dark};
                color: {self.text_primary};
                font-family: {self.font_family_ui};
                font-size: {self.font_size_normal}pt;
            }}

            QWidget {{
                color: {self.text_primary};
            }}

            /* === Dock Widgets === */
            QDockWidget {{
                background-color: {self.background_mid};
                border: 1px solid {self.border_subtle};
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }}

            QDockWidget::title {{
                background-color: {self.background_light};
                color: {self.text_secondary};
                padding: {self.spacing_small}px;
                border-bottom: 1px solid {self.border_subtle};
                font-weight: bold;
            }}

            /* === Buttons === */
            QPushButton {{
                background-color: {self.background_light};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: {self.radius_small}px;
                padding: {self.padding_compact}px {self.padding_normal}px;
                min-height: 24px;
            }}

            QPushButton:hover {{
                background-color: {self.background_hover};
                border-color: {self.accent_hover};
            }}

            QPushButton:pressed {{
                background-color: {self.accent_primary};
                border-color: {self.accent_bright};
            }}

            QPushButton:disabled {{
                background-color: {self.background_dark};
                color: {self.text_disabled};
                border-color: {self.border_subtle};
            }}

            /* Primary Action Buttons */
            QPushButton[primary="true"] {{
                background-color: {self.accent_primary};
                color: white;
                border: none;
                font-weight: bold;
            }}

            QPushButton[primary="true"]:hover {{
                background-color: {self.accent_hover};
            }}

            QPushButton[primary="true"]:pressed {{
                background-color: {self.accent_bright};
            }}

            /* Checkable Buttons (Tool Selection) */
            QPushButton:checkable {{
                background-color: {self.background_light};
                border: 2px solid {self.border_subtle};
            }}

            QPushButton:checked {{
                background-color: {self.accent_primary};
                color: white;
                border: 2px solid {self.accent_bright};
                font-weight: bold;
            }}

            QPushButton:checkable:hover {{
                border-color: {self.accent_hover};
            }}

            /* === Tree Widgets === */
            QTreeWidget {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border: none;
                outline: none;
                padding: {self.spacing_small}px;
            }}

            QTreeWidget::item {{
                padding: {self.spacing_tiny}px {self.spacing_small}px;
                border-radius: {self.radius_small}px;
                min-height: 24px;
            }}

            QTreeWidget::item:selected {{
                background-color: {self.accent_primary};
                color: white;
            }}

            QTreeWidget::item:hover {{
                background-color: {self.background_hover};
            }}

            QTreeWidget::branch {{
                background: transparent;
            }}

            QTreeWidget::branch:has-siblings:!adjoins-item {{
                border-image: none;
                image: none;
                background: transparent;
            }}

            QTreeWidget::branch:has-siblings:adjoins-item {{
                border-image: none;
                image: none;
                background: transparent;
            }}

            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
                border-image: none;
                image: none;
                background: transparent;
            }}

            QTreeWidget::indicator {{
                width: 0px;
                height: 0px;
            }}

            /* === Tab Widgets === */
            QTabWidget::pane {{
                border: 1px solid {self.border_subtle};
                background-color: {self.background_mid};
                border-top: none;
            }}

            QTabBar::tab {{
                background-color: {self.background_dark};
                color: {self.text_secondary};
                padding: {self.spacing_small}px {self.spacing_medium}px;
                border: 1px solid {self.border_subtle};
                border-bottom: none;
                border-top-left-radius: {self.radius_medium}px;
                border-top-right-radius: {self.radius_medium}px;
                margin-right: 2px;
                min-width: 80px;
            }}

            QTabBar::tab:selected {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border-bottom: 2px solid {self.accent_bright};
            }}

            QTabBar::tab:hover {{
                background-color: {self.background_hover};
                color: {self.text_primary};
            }}

            /* === Scroll Bars === */
            QScrollBar:vertical {{
                background-color: {self.background_dark};
                width: 12px;
                border: none;
            }}

            QScrollBar::handle:vertical {{
                background-color: {self.border_strong};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {self.text_disabled};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background-color: {self.background_dark};
                height: 12px;
                border: none;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {self.border_strong};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {self.text_disabled};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* === Input Fields === */
            QLineEdit, QTextEdit {{
                background-color: {self.background_dark};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: {self.radius_small}px;
                padding: {self.spacing_small}px;
                selection-background-color: {self.accent_primary};
            }}

            QLineEdit:focus, QTextEdit:focus {{
                border-color: {self.accent_bright};
            }}

            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {self.background_dark};
                color: {self.text_disabled};
            }}

            /* === Labels === */
            QLabel {{
                color: {self.text_primary};
                background-color: transparent;
            }}

            QLabel[type="header"] {{
                font-size: {self.font_size_large}pt;
                font-weight: bold;
                color: {self.text_primary};
            }}

            QLabel[type="caption"] {{
                font-size: {self.font_size_small}pt;
                color: {self.text_secondary};
            }}

            /* === Group Boxes === */
            QGroupBox {{
                border: 1px solid {self.border_subtle};
                border-radius: {self.radius_medium}px;
                margin-top: {self.spacing_medium}px;
                padding-top: {self.spacing_medium}px;
                background-color: {self.background_light};
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.spacing_medium}px;
                padding: 0 {self.spacing_small}px;
                color: {self.text_secondary};
            }}

            /* === Menus === */
            QMenuBar {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border-bottom: 1px solid {self.border_subtle};
                padding: 2px;
            }}

            QMenuBar::item {{
                background-color: transparent;
                padding: {self.spacing_small}px {self.spacing_medium}px;
            }}

            QMenuBar::item:selected {{
                background-color: {self.background_hover};
            }}

            QMenuBar::item:pressed {{
                background-color: {self.accent_primary};
            }}

            QMenu {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border: 1px solid {self.border_strong};
                padding: {self.spacing_tiny}px;
            }}

            QMenu::item {{
                padding: {self.spacing_small}px {self.spacing_large}px;
                border-radius: {self.radius_small}px;
            }}

            QMenu::item:selected {{
                background-color: {self.accent_primary};
                color: white;
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {self.border_subtle};
                margin: {self.spacing_tiny}px 0;
            }}

            /* === Splitters === */
            QSplitter::handle {{
                background-color: {self.border_subtle};
            }}

            QSplitter::handle:horizontal {{
                width: 1px;
            }}

            QSplitter::handle:vertical {{
                height: 1px;
            }}

            /* === Checkboxes === */
            QCheckBox {{
                spacing: {self.spacing_small}px;
                color: {self.text_primary};
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {self.border_strong};
                border-radius: {self.radius_small}px;
                background-color: {self.background_dark};
            }}

            QCheckBox::indicator:hover {{
                border-color: {self.accent_hover};
            }}

            QCheckBox::indicator:checked {{
                background-color: {self.accent_primary};
                border-color: {self.accent_primary};
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {self.accent_hover};
                border-color: {self.accent_hover};
            }}

            /* === Spin Boxes === */
            QSpinBox, QDoubleSpinBox {{
                background-color: {self.background_dark};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: {self.radius_small}px;
                padding: {self.spacing_tiny}px {self.spacing_small}px;
                min-height: 24px;
            }}

            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {self.accent_bright};
            }}

            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                background-color: {self.background_light};
                border: none;
                border-top-right-radius: {self.radius_small}px;
            }}

            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {self.background_light};
                border: none;
                border-bottom-right-radius: {self.radius_small}px;
            }}

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {self.background_hover};
            }}

            /* === Combo Boxes === */
            QComboBox {{
                background-color: {self.background_light};
                color: {self.text_primary};
                border: 1px solid {self.border_subtle};
                border-radius: {self.radius_small}px;
                padding: {self.spacing_tiny}px {self.spacing_small}px;
                min-height: 24px;
            }}

            QComboBox:hover {{
                border-color: {self.accent_hover};
            }}

            QComboBox:focus {{
                border-color: {self.accent_bright};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {self.background_mid};
                color: {self.text_primary};
                border: 1px solid {self.border_strong};
                selection-background-color: {self.accent_primary};
                selection-color: white;
            }}

            /* === Tool Tips === */
            QToolTip {{
                background-color: {self.background_light};
                color: {self.text_primary};
                border: 1px solid {self.border_strong};
                border-radius: {self.radius_small}px;
                padding: {self.spacing_small}px;
            }}
        """

    def to_dict(self) -> dict:
        """Convert theme to dictionary for saving."""
        return {
            'background_dark': self.background_dark,
            'background_mid': self.background_mid,
            'background_light': self.background_light,
            'background_hover': self.background_hover,
            'border_subtle': self.border_subtle,
            'border_strong': self.border_strong,
            'text_primary': self.text_primary,
            'text_secondary': self.text_secondary,
            'text_disabled': self.text_disabled,
            'accent_primary': self.accent_primary,
            'accent_hover': self.accent_hover,
            'accent_bright': self.accent_bright,
            'success': self.success,
            'warning': self.warning,
            'error': self.error,
            'info': self.info,
            'category_physics': self.category_physics,
            'category_rendering': self.category_rendering,
            'category_gameplay': self.category_gameplay,
            'category_ai': self.category_ai,
            'category_audio': self.category_audio,
            'category_interaction': self.category_interaction,
            'spacing_tiny': self.spacing_tiny,
            'spacing_small': self.spacing_small,
            'spacing_medium': self.spacing_medium,
            'spacing_large': self.spacing_large,
            'spacing_xlarge': self.spacing_xlarge,
            'padding_compact': self.padding_compact,
            'padding_normal': self.padding_normal,
            'padding_spacious': self.padding_spacious,
            'font_family_ui': self.font_family_ui,
            'font_family_code': self.font_family_code,
            'font_size_small': self.font_size_small,
            'font_size_normal': self.font_size_normal,
            'font_size_large': self.font_size_large,
            'font_size_xlarge': self.font_size_xlarge,
            'radius_small': self.radius_small,
            'radius_medium': self.radius_medium,
            'radius_large': self.radius_large,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'EditorTheme':
        """Create theme from dictionary."""
        return cls(**data)

    def save(self, path: str):
        """Save theme to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'EditorTheme':
        """Load theme from JSON file."""
        if not os.path.exists(path):
            return cls()  # Return default theme

        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Default global theme instance
_default_theme = EditorTheme()


def get_theme() -> EditorTheme:
    """Get the current global theme."""
    return _default_theme


def set_theme(theme: EditorTheme):
    """Set the global theme."""
    global _default_theme
    _default_theme = theme
