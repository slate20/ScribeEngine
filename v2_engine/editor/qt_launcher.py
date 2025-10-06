"""
Qt-based Launcher for Scribe Engine V2

Modern launcher with recent projects, new project wizard, and project browser.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

# Add parent directories to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.utils.config_manager import get_recent_projects, add_recent_project, remove_recent_project
from v2_engine.editor.theme import EditorTheme


class LauncherWindow(QMainWindow):
    """
    Main launcher window for Scribe Engine V2.

    Features:
    - Recent projects list (clickable)
    - New project button
    - Open project button (file browser)
    - Clean, modern UI matching editor theme
    """

    def __init__(self):
        super().__init__()
        self.selected_project = None
        self.theme = EditorTheme()

        self.setup_ui()
        self.load_recent_projects()

        # Apply theme
        self.setStyleSheet(self.theme.get_stylesheet())

    def setup_ui(self):
        """Setup the launcher UI."""
        self.setWindowTitle("Scribe Engine V2 - Launcher")
        self.setFixedSize(800, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(self.theme.spacing_xlarge, self.theme.spacing_xlarge,
                                 self.theme.spacing_xlarge, self.theme.spacing_xlarge)
        layout.setSpacing(self.theme.spacing_large)

        # === Header ===
        header_layout = QVBoxLayout()
        header_layout.setSpacing(self.theme.spacing_small)

        title = QLabel("Scribe Engine V2")
        title.setFont(QFont(self.theme.font_family_ui, self.theme.font_size_xlarge * 2, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Visual 2D Game Development")
        subtitle.setProperty("type", "caption")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)
        layout.addSpacing(self.theme.spacing_large)

        # === Recent Projects Section ===
        recent_label = QLabel("Recent Projects")
        recent_label.setProperty("type", "header")
        layout.addWidget(recent_label)

        # Recent projects list
        self.recent_list = QListWidget()
        self.recent_list.setAlternatingRowColors(True)
        self.recent_list.itemDoubleClicked.connect(self.on_recent_project_double_clicked)
        self.recent_list.itemClicked.connect(self.on_recent_project_clicked)
        layout.addWidget(self.recent_list, 1)  # Stretch to fill space

        # === Action Buttons ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(self.theme.spacing_medium)

        # New Project button
        new_btn = QPushButton("New Project")
        new_btn.setProperty("primary", "true")
        new_btn.setMinimumHeight(50)
        new_btn.clicked.connect(self.new_project)
        button_layout.addWidget(new_btn)

        # Open Project button
        open_btn = QPushButton("Open Project...")
        open_btn.setMinimumHeight(50)
        open_btn.clicked.connect(self.open_project)
        button_layout.addWidget(open_btn)

        # Quit button
        quit_btn = QPushButton("Quit")
        quit_btn.setMinimumHeight(50)
        quit_btn.clicked.connect(self.close)
        button_layout.addWidget(quit_btn)

        layout.addLayout(button_layout)

    def load_recent_projects(self):
        """Load and display recent projects."""
        self.recent_list.clear()
        recent_projects = get_recent_projects()

        if not recent_projects:
            # Show helpful message
            item = QListWidgetItem("No recent projects")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
            item.setForeground(QColor(self.theme.text_secondary))
            self.recent_list.addItem(item)
            return

        for project_path in recent_projects:
            # Verify project still exists
            if not os.path.exists(project_path):
                continue

            # Get project name (directory name)
            project_name = os.path.basename(project_path)

            # Create list item
            item = QListWidgetItem(f"{project_name}")
            item.setData(Qt.ItemDataRole.UserRole, project_path)  # Store full path
            item.setToolTip(project_path)  # Show full path on hover

            # Add path as secondary text
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(self.theme.spacing_small, self.theme.spacing_tiny,
                                          self.theme.spacing_small, self.theme.spacing_tiny)
            item_layout.setSpacing(2)

            name_label = QLabel(project_name)
            name_label.setFont(QFont(self.theme.font_family_ui, self.theme.font_size_normal, QFont.Weight.Bold))
            item_layout.addWidget(name_label)

            path_label = QLabel(project_path)
            path_label.setProperty("type", "caption")
            path_label.setWordWrap(True)
            item_layout.addWidget(path_label)

            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, item_widget)
            item.setSizeHint(item_widget.sizeHint())

    def on_recent_project_clicked(self, item):
        """Handle single click on recent project (selection)."""
        project_path = item.data(Qt.ItemDataRole.UserRole)
        if project_path:
            self.selected_project = project_path

    def on_recent_project_double_clicked(self, item):
        """Handle double-click on recent project (open immediately)."""
        project_path = item.data(Qt.ItemDataRole.UserRole)
        if project_path and os.path.exists(project_path):
            self.launch_editor(project_path)
        elif project_path:
            QMessageBox.warning(
                self,
                "Project Not Found",
                f"The project no longer exists:\n{project_path}\n\nIt will be removed from recent projects."
            )
            remove_recent_project(project_path)
            self.load_recent_projects()

    def new_project(self):
        """Create a new project."""
        from v2_engine.editor.project_wizard import ProjectWizard

        wizard = ProjectWizard()
        project_path = wizard.run()

        if project_path:
            self.launch_editor(project_path)

    def open_project(self):
        """Open existing project via file browser."""
        project_path = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )

        if not project_path:
            return

        # Verify it's a valid project
        if not os.path.exists(os.path.join(project_path, '2d_project.json')):
            QMessageBox.warning(
                self,
                "Invalid Project",
                f"The selected directory is not a valid Scribe Engine V2 project.\n\nMissing: 2d_project.json"
            )
            return

        self.launch_editor(project_path)

    def launch_editor(self, project_path):
        """
        Launch the editor with the specified project.

        Args:
            project_path: Path to project directory
        """
        # Add to recent projects
        add_recent_project(project_path)

        # Close launcher
        self.close()

        # Launch Qt editor
        from v2_engine.editor.qt_editor import EditorWindow

        self.editor = EditorWindow(project_path)
        self.editor.show()


def main():
    """Entry point for Qt launcher."""
    app = QApplication(sys.argv)
    app.setApplicationName("Scribe Engine V2")

    launcher = LauncherWindow()
    launcher.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
