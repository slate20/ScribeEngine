"""
BehaviorBrowserDialog - Modern visual browser for adding components to sprites.

Replaces simple dropdown with card-based UI featuring:
- Visual component cards with icons and descriptions
- Category filtering
- Search functionality
- Templates tab for behavior bundles
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTabWidget,
    QPushButton, QScrollArea, QWidget, QGridLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from v2_engine.components.component_registry import (
    get_component_registry, ComponentMetadata, ComponentCategory
)
from v2_engine.editor.theme import EditorTheme
from .behavior_card import BehaviorCard
from .category_filter import CategoryFilterBar


class BehaviorBrowserDialog(QDialog):
    """
    Modern dialog for browsing and adding behaviors (components) to sprites.

    Features:
    - Behaviors tab: Card grid of all components with filtering
    - Templates tab: Pre-configured behavior bundles
    - Search bar: Real-time filtering
    - Category filters: Color-coded pill buttons
    """

    # Signal emitted when new behavior is created (path: str)
    new_behavior_created = pyqtSignal(str)

    def __init__(self, parent, sprite, theme: EditorTheme, project_path: str = None):
        """
        Initialize behavior browser.

        Args:
            parent: Parent widget
            sprite: Sprite to add components to
            theme: Editor theme
            project_path: Path to project directory (for creating new behaviors)
        """
        super().__init__(parent)
        self.sprite = sprite
        self.theme = theme
        self.project_path = project_path
        self.registry = get_component_registry()
        self.selected_metadata = []  # Changed to list for multi-select
        self.current_cards = []

        # Initialize registry
        self.registry.initialize()

        self._setup_ui()
        self._populate_behaviors()

    def _setup_ui(self):
        """Create dialog layout."""
        self.setWindowTitle("Add Behavior")
        self.setModal(True)
        self.resize(800, 600)

        # Apply theme background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.background_mid};
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(self.theme.spacing_medium)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setSpacing(self.theme.spacing_small)

        search_icon = QLabel("🔍")
        search_font = QFont()
        search_font.setPointSize(14)
        search_icon.setFont(search_font)
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search behaviors...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px;
                font-size: {self.theme.font_size_normal}px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent_primary};
            }}
        """)
        search_layout.addWidget(self.search_input, 1)

        layout.addLayout(search_layout)

        # Category filter bar
        categories = self.registry.get_categories()
        self.category_filter = CategoryFilterBar(categories, self.theme)
        self.category_filter.filters_changed.connect(self._on_filters_changed)
        layout.addWidget(self.category_filter)

        # Tab widget (Behaviors / Templates)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
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
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme.background_mid};
                border-bottom: 2px solid {self.theme.accent_primary};
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme.background_hover};
            }}
        """)

        # Behaviors tab
        behaviors_tab = QWidget()
        behaviors_layout = QVBoxLayout(behaviors_tab)
        behaviors_layout.setContentsMargins(0, self.theme.spacing_medium, 0, 0)

        # Scrollable card grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme.background_mid};
            }}
        """)

        # Grid container
        self.card_container = QWidget()
        self.card_grid = QGridLayout(self.card_container)
        self.card_grid.setSpacing(self.theme.spacing_medium)
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll_area.setWidget(self.card_container)
        behaviors_layout.addWidget(scroll_area)

        self.tabs.addTab(behaviors_tab, "Behaviors")

        # Templates tab (placeholder for now)
        templates_tab = QWidget()
        templates_layout = QVBoxLayout(templates_tab)
        templates_label = QLabel("Templates coming in Phase 3...")
        templates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        templates_label.setStyleSheet(f"color: {self.theme.text_secondary};")
        templates_layout.addWidget(templates_label)
        self.tabs.addTab(templates_tab, "Templates")

        layout.addWidget(self.tabs, 1)

        # Footer buttons
        button_layout = QHBoxLayout()

        # New Behavior button (left side)
        new_behavior_btn = QPushButton("✨ New Behavior")
        new_behavior_btn.clicked.connect(self._on_new_behavior_clicked)
        new_behavior_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_light};
                color: {self.theme.accent_primary};
                border: 1px solid {self.theme.accent_primary};
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px 16px;
                font-size: {self.theme.font_size_normal}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_primary};
                color: white;
            }}
        """)
        button_layout.addWidget(new_behavior_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_strong};
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px 16px;
                font-size: {self.theme.font_size_normal}px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.background_hover};
            }}
        """)
        button_layout.addWidget(cancel_btn)

        self.add_btn = QPushButton("Add")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.accent_primary};
                color: white;
                border: none;
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px 16px;
                font-size: {self.theme.font_size_normal}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme.accent_hover};
            }}
            QPushButton:disabled {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_disabled};
            }}
        """)
        button_layout.addWidget(self.add_btn)

        layout.addLayout(button_layout)

    def _populate_behaviors(self):
        """Populate card grid with all behaviors."""
        components = self.registry.get_all_components()
        self._update_card_grid(components)

    def _update_card_grid(self, components: list[ComponentMetadata]):
        """
        Update card grid with filtered components.

        Args:
            components: List of components to display
        """
        # Clear existing cards
        for card in self.current_cards:
            card.deleteLater()
        self.current_cards.clear()

        # Add new cards
        col = 0
        row = 0
        cards_per_row = 3

        for metadata in components:
            # Check if sprite already has this component
            already_has = self.sprite.has_component(metadata.class_ref)

            card = BehaviorCard(metadata, self.theme)
            card.clicked.connect(self._on_card_clicked)
            card.double_clicked.connect(self._on_card_double_clicked)
            card.multi_select_clicked.connect(self._on_card_multi_select_clicked)

            # Disable if already has component
            if already_has:
                card.setEnabled(False)
                card.setStyleSheet(f"""
                    BehaviorCard {{
                        background-color: {self.theme.background_dark};
                        border: 2px solid {self.theme.border_subtle};
                        opacity: 0.5;
                    }}
                """)
                card.setToolTip(f"Sprite already has {metadata.name} component")

            self.card_grid.addWidget(card, row, col)
            self.current_cards.append(card)

            col += 1
            if col >= cards_per_row:
                col = 0
                row += 1

    def _on_card_clicked(self, metadata: ComponentMetadata):
        """Handle single card selection (clears other selections)."""
        # Deselect all cards
        for card in self.current_cards:
            card.set_selected(False)

        # Select clicked card
        self.selected_metadata = [metadata]
        for card in self.current_cards:
            if card.metadata == metadata:
                card.set_selected(True)
                break

        # Enable add button
        self.add_btn.setEnabled(True)
        self._update_add_button_text()

    def _on_card_multi_select_clicked(self, metadata: ComponentMetadata):
        """Handle multi-select toggle (Ctrl+Click)."""
        # Toggle selection for this metadata
        if metadata in self.selected_metadata:
            self.selected_metadata.remove(metadata)
        else:
            self.selected_metadata.append(metadata)

        # Update card visual states
        for card in self.current_cards:
            if card.metadata == metadata:
                card.set_selected(metadata in self.selected_metadata)
                break

        # Enable/disable add button based on selection
        self.add_btn.setEnabled(len(self.selected_metadata) > 0)
        self._update_add_button_text()

    def _update_add_button_text(self):
        """Update add button text to show count."""
        count = len(self.selected_metadata)
        if count == 0:
            self.add_btn.setText("Add")
        elif count == 1:
            self.add_btn.setText("Add")
        else:
            self.add_btn.setText(f"Add ({count})")

    def _on_card_double_clicked(self, metadata: ComponentMetadata):
        """Handle double-click to immediately add component."""
        self.selected_metadata = [metadata]
        self._on_add_clicked()

    def _on_search_changed(self, query: str):
        """Handle search input change."""
        # Get filtered components
        if query:
            components = self.registry.search_components(query)
        else:
            components = self.registry.get_all_components()

        # Apply category filter
        active_categories = self.category_filter.get_active_categories()
        components = [c for c in components if c.category in active_categories]

        self._update_card_grid(components)

    def _on_filters_changed(self, active_categories: list[ComponentCategory]):
        """Handle category filter change."""
        # Get search query
        query = self.search_input.text()

        # Get components matching search
        if query:
            components = self.registry.search_components(query)
        else:
            components = self.registry.get_all_components()

        # Apply category filter
        components = [c for c in components if c.category in active_categories]

        self._update_card_grid(components)

    def _on_add_clicked(self):
        """Handle add button click."""
        if not self.selected_metadata:
            return

        # Check if sprite already has any of the selected components
        duplicates = []
        for metadata in self.selected_metadata:
            if self.sprite.has_component(metadata.class_ref):
                duplicates.append(metadata.name)

        if duplicates:
            QMessageBox.warning(
                self,
                'Component Already Exists',
                f'Sprite already has the following component(s):\n' + '\n'.join(f'• {name}' for name in duplicates)
            )
            return

        # Components will be added by parent dialog handler
        self.accept()

    def get_selected_components(self) -> list[tuple]:
        """
        Get selected components to add.

        Returns:
            List of (component_class, properties_dict) tuples
        """
        if self.selected_metadata:
            return [(metadata.class_ref, {}) for metadata in self.selected_metadata]
        return []

    def _on_new_behavior_clicked(self):
        """Handle New Behavior button click."""
        if not self.project_path:
            QMessageBox.warning(
                self,
                "No Project",
                "Cannot create behavior: No project path specified."
            )
            return

        # Import here to avoid circular import
        from v2_engine.editor.new_behavior_dialog import NewBehaviorDialog

        # Open new behavior dialog
        dialog = NewBehaviorDialog(self.project_path, self.theme, self)

        if dialog.exec():
            # Behavior was created
            created_file = dialog.get_created_file_path()
            print(f"[BehaviorBrowser] New behavior created: {created_file}")

            # Emit signal so editor can open the file
            self.new_behavior_created.emit(created_file)

            # Refresh the behavior list to show new custom behavior
            from v2_engine.components.component_registry import get_component_registry
            registry = get_component_registry()
            registry.refresh_custom_behaviors(self.project_path)

            # Refresh the card grid to show the new behavior
            self._populate_behaviors()

            QMessageBox.information(
                self,
                "Behavior Created",
                f"Behavior created successfully!\n\n"
                f"The new behavior is now available in the Custom category."
            )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.add_btn.isEnabled():
                self._on_add_clicked()
        else:
            super().keyPressEvent(event)
