"""
File Navigator widget for code editor.

Displays a tree view of project files with support for:
- Behaviors directory
- Engine components (read-only indicator)
- File icons and categorization
- Click to open files
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
    QLabel, QHBoxLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import os
from pathlib import Path

from v2_engine.editor.theme import EditorTheme


class FileNavigator(QWidget):
    """
    File navigator widget for browsing project files.

    Features:
    - Tree view of project structure
    - Behaviors folder
    - Engine components (read-only)
    - File filtering/search
    - Click to open files

    Signals:
        file_selected: Emitted when file is clicked (file_path: str)
    """

    file_selected = pyqtSignal(str)  # Emits file path

    def __init__(self, theme: EditorTheme, project_path: str = None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.project_path = project_path
        self.current_file = None

        self._setup_ui()
        if project_path:
            self.set_project_path(project_path)

    def _setup_ui(self):
        """Create navigator layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.theme.spacing_small)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(
            self.theme.padding_compact,
            self.theme.padding_compact,
            self.theme.padding_compact,
            self.theme.padding_compact
        )

        header_label = QLabel("Files")
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme.text_primary};
                font-size: {self.theme.font_size_normal}px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(header_label, 1)

        # Refresh button
        refresh_btn = QPushButton("R")
        refresh_btn.setFixedSize(24, 24)
        refresh_btn.setToolTip("Refresh file list")
        refresh_btn.clicked.connect(self.refresh)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.background_light};
                border: 1px solid {self.theme.border_subtle};
                border-radius: 3px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.background_hover};
            }}
        """)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Search/filter bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter files...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_small}px;
                padding: {self.theme.padding_compact}px;
                font-size: {self.theme.font_size_small}px;
                margin: 0px {self.theme.padding_compact}px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent_primary};
            }}
        """)
        layout.addWidget(self.search_input)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {self.theme.background_mid};
                color: {self.theme.text_primary};
                border: none;
                font-size: {self.theme.font_size_normal}px;
                outline: none;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-radius: 3px;
            }}
            QTreeWidget::item:hover {{
                background-color: {self.theme.background_hover};
            }}
            QTreeWidget::item:selected {{
                background-color: {self.theme.accent_primary};
                color: white;
            }}
            QTreeWidget::branch:has-children:closed {{
                image: none;
            }}
            QTreeWidget::branch:has-children:open {{
                image: none;
            }}
        """)
        layout.addWidget(self.tree)

    def set_project_path(self, project_path: str):
        """Set the project path and populate tree."""
        self.project_path = project_path
        self.refresh()

    def refresh(self):
        """Refresh the file tree."""
        self.tree.clear()

        if not self.project_path:
            return

        # Add project scenes folder
        scenes_path = os.path.join(self.project_path, 'scenes')
        if os.path.exists(scenes_path):
            scenes_item = QTreeWidgetItem(self.tree, ["Scenes (Project)"])
            scenes_item.setExpanded(True)
            self._populate_directory(scenes_item, scenes_path, editable=True)

        # Add project behaviors folder
        behaviors_path = os.path.join(self.project_path, 'behaviors')
        if os.path.exists(behaviors_path):
            behaviors_item = QTreeWidgetItem(self.tree, ["Behaviors (Project)"])
            behaviors_item.setExpanded(True)
            self._populate_directory(behaviors_item, behaviors_path, editable=True)

        # Add engine components folder (read-only)
        engine_path = os.path.join(os.path.dirname(__file__), '..', '..', 'components')
        engine_path = os.path.abspath(engine_path)
        if os.path.exists(engine_path):
            engine_item = QTreeWidgetItem(self.tree, ["Engine Components (Read-Only)"])
            engine_item.setExpanded(False)
            self._populate_directory(engine_item, engine_path, editable=False)

    def _populate_directory(self, parent_item: QTreeWidgetItem, directory: str, editable: bool = True):
        """Populate tree with directory contents."""
        try:
            # Get all Python files
            for item in sorted(os.listdir(directory)):
                item_path = os.path.join(directory, item)

                if os.path.isfile(item_path) and item.endswith('.py') and not item.startswith('_'):
                    # Add Python file
                    icon = "[W]" if editable else "[R]"
                    file_item = QTreeWidgetItem(parent_item, [f"{icon} {item}"])
                    file_item.setData(0, Qt.ItemDataRole.UserRole, item_path)

                    # Mark read-only files
                    if not editable:
                        font = file_item.font(0)
                        font.setItalic(True)
                        file_item.setFont(0, font)
                        file_item.setForeground(0, QColor(self.theme.text_secondary))

        except Exception as e:
            print(f"[FileNavigator] Error populating directory {directory}: {e}")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            self.current_file = file_path
            self.file_selected.emit(file_path)

    def _on_search_changed(self, query: str):
        """Handle search input change."""
        query_lower = query.lower()

        # Iterate through all items in tree
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            file_path = item.data(0, Qt.ItemDataRole.UserRole)

            if file_path:  # Only filter file items, not folder items
                visible = query_lower in os.path.basename(file_path).lower()
                item.setHidden(not visible)
            else:
                # Show folders if any children are visible
                has_visible_children = False
                for i in range(item.childCount()):
                    if not item.child(i).isHidden():
                        has_visible_children = True
                        break
                item.setHidden(not has_visible_children)

            iterator += 1

    def set_current_file(self, file_path: str):
        """Highlight the currently open file in the tree."""
        self.current_file = file_path

        # Find and select the item
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            item_path = item.data(0, Qt.ItemDataRole.UserRole)

            if item_path == file_path:
                self.tree.setCurrentItem(item)
                break

            iterator += 1
