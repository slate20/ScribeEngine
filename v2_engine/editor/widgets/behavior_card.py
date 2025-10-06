"""
BehaviorCard widget - Visual card for component in Behavior Browser.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor

from v2_engine.components.component_registry import ComponentMetadata
from v2_engine.editor.theme import EditorTheme


class BehaviorCard(QFrame):
    """
    Visual card widget representing a component in the behavior browser.

    Features:
    - Icon + name header
    - Category badge (color-coded)
    - Short description
    - Hover effects
    - Click to select
    """

    clicked = pyqtSignal(object)  # Emits ComponentMetadata when clicked
    double_clicked = pyqtSignal(object)  # Emits ComponentMetadata when double-clicked

    def __init__(self, metadata: ComponentMetadata, theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.metadata = metadata
        self.theme = theme
        self.selected = False

        self._setup_ui()
        self._setup_styling()

    def _setup_ui(self):
        """Create card layout and widgets."""
        # Card fixed size
        self.setFixedSize(200, 120)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.theme.padding_compact,
            self.theme.padding_compact,
            self.theme.padding_compact,
            self.theme.padding_compact
        )
        layout.setSpacing(self.theme.spacing_small)

        # Header row (icon + name)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(self.theme.spacing_small)

        # Icon label
        icon_label = QLabel(self.metadata.icon)
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)

        # Name label
        name_label = QLabel(self.metadata.name)
        name_font = QFont()
        name_font.setPointSize(self.theme.font_size_normal)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {self.theme.text_primary};")
        header_layout.addWidget(name_label, 1)

        layout.addLayout(header_layout)

        # Category badge
        category_badge = QLabel(self.metadata.category.value)
        category_font = QFont()
        category_font.setPointSize(self.theme.font_size_small)
        category_badge.setFont(category_font)

        # Get category color
        category_color = self.theme.get_category_color(self.metadata.category.value)
        category_badge.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {category_color};
                border: 1px solid {category_color};
                border-radius: {self.theme.radius_large}px;
                padding: 2px 6px;
            }}
        """)
        category_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        category_badge.setFixedWidth(80)

        layout.addWidget(category_badge)

        # Description label (2 lines max)
        desc_label = QLabel(self.metadata.description)
        desc_font = QFont()
        desc_font.setPointSize(self.theme.font_size_small)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet(f"color: {self.theme.text_secondary};")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(32)  # ~2 lines
        layout.addWidget(desc_label)

        layout.addStretch()

    def _setup_styling(self):
        """Apply theme styling to card."""
        self.setStyleSheet(f"""
            BehaviorCard {{
                background-color: {self.theme.background_light};
                border: 2px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_medium}px;
            }}
            BehaviorCard:hover {{
                background-color: {self.theme.background_hover};
                border-color: {self.theme.border_strong};
            }}
        """)

    def set_selected(self, selected: bool):
        """
        Set card selection state.

        Args:
            selected: Whether card is selected
        """
        self.selected = selected

        if selected:
            self.setStyleSheet(f"""
                BehaviorCard {{
                    background-color: {self.theme.background_hover};
                    border: 2px solid {self.theme.accent_primary};
                    border-radius: {self.theme.radius_medium}px;
                }}
            """)
        else:
            self._setup_styling()

    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.metadata)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to immediately add component."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.metadata)
        super().mouseDoubleClickEvent(event)

    def sizeHint(self):
        """Return preferred size."""
        return QSize(200, 120)
