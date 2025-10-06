"""
New Behavior Dialog - Create new custom behavior from template.
"""

import os
import shutil
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from v2_engine.editor.theme import EditorTheme


class NewBehaviorDialog(QDialog):
    """
    Dialog for creating new custom behavior from template.

    Features:
    - Select from available templates
    - Preview template code
    - Enter behavior name
    - Creates file in project/behaviors/ directory
    - Auto-opens in code editor
    """

    def __init__(self, project_path: str, theme: EditorTheme, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.theme = theme
        self.selected_template = None
        self.created_file_path = None

        self._setup_ui()
        self._load_templates()

    def _setup_ui(self):
        """Create dialog layout."""
        self.setWindowTitle("New Behavior")
        self.setModal(True)
        self.resize(700, 500)

        # Apply theme background
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme.background_mid};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(self.theme.spacing_medium)

        # Title
        title = QLabel("Create New Behavior")
        title_font = QFont()
        title_font.setPointSize(self.theme.font_size_large)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {self.theme.text_primary};")
        layout.addWidget(title)

        # Behavior name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Behavior Name:")
        name_label.setStyleSheet(f"color: {self.theme.text_primary}; font-size: {self.theme.font_size_normal}px;")
        name_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("MyCustomBehavior")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.name_input.setStyleSheet(f"""
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
        name_layout.addWidget(self.name_input, 1)

        layout.addLayout(name_layout)

        # Template selection and preview
        content_layout = QHBoxLayout()

        # Left: Template list
        left_panel = QVBoxLayout()
        templates_label = QLabel("Select Template:")
        templates_label.setStyleSheet(f"color: {self.theme.text_primary}; font-size: {self.theme.font_size_normal}px;")
        left_panel.addWidget(templates_label)

        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        self.template_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_small}px;
                font-size: {self.theme.font_size_normal}px;
            }}
            QListWidget::item {{
                padding: {self.theme.padding_compact}px;
            }}
            QListWidget::item:selected {{
                background-color: {self.theme.accent_primary};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {self.theme.background_hover};
            }}
        """)
        left_panel.addWidget(self.template_list)

        content_layout.addLayout(left_panel, 1)

        # Right: Preview
        right_panel = QVBoxLayout()
        preview_label = QLabel("Template Preview:")
        preview_label.setStyleSheet(f"color: {self.theme.text_primary}; font-size: {self.theme.font_size_normal}px;")
        right_panel.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme.background_light};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_subtle};
                border-radius: {self.theme.radius_small}px;
                font-family: {self.theme.font_family_code};
                font-size: {self.theme.font_size_normal}px;
            }}
        """)
        right_panel.addWidget(self.preview_text)

        content_layout.addLayout(right_panel, 2)

        layout.addLayout(content_layout, 1)

        # Footer buttons
        button_layout = QHBoxLayout()
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

        self.create_btn = QPushButton("Create")
        self.create_btn.setEnabled(False)
        self.create_btn.clicked.connect(self._on_create_clicked)
        self.create_btn.setStyleSheet(f"""
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
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

    def _load_templates(self):
        """Load available behavior templates."""
        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'editor', 'templates', 'scripts'
        )

        if not os.path.exists(templates_dir):
            print(f"[NewBehaviorDialog] Templates directory not found: {templates_dir}")
            return

        # Find all .py template files
        templates = []
        for filename in os.listdir(templates_dir):
            if filename.endswith('.py'):
                template_path = os.path.join(templates_dir, filename)
                template_name = filename[:-3].replace('_', ' ').title()
                templates.append((template_name, template_path))

        # Add to list
        for name, path in sorted(templates):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.template_list.addItem(item)

        # Select first template by default
        if templates:
            self.template_list.setCurrentRow(0)

    def _on_template_selected(self, current, previous):
        """Handle template selection change."""
        if not current:
            self.selected_template = None
            self.preview_text.clear()
            return

        # Get template path
        template_path = current.data(Qt.ItemDataRole.UserRole)
        self.selected_template = template_path

        # Load and display template content
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.preview_text.setPlainText(content)
        except Exception as e:
            self.preview_text.setPlainText(f"Error loading template: {e}")

        # Update create button state
        self._update_create_button()

    def _on_name_changed(self, text):
        """Handle behavior name input change."""
        self._update_create_button()

    def _update_create_button(self):
        """Update create button enabled state."""
        name = self.name_input.text().strip()
        has_template = self.selected_template is not None

        # Enable if name is valid and template selected
        is_valid = len(name) > 0 and has_template and name.isidentifier()
        self.create_btn.setEnabled(is_valid)

    def _on_create_clicked(self):
        """Handle create button click."""
        behavior_name = self.name_input.text().strip()

        if not behavior_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a behavior name.")
            return

        if not behavior_name.isidentifier():
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Behavior name must be a valid Python identifier\n"
                "(letters, numbers, underscores; cannot start with number)"
            )
            return

        if not self.selected_template:
            QMessageBox.warning(self, "No Template", "Please select a template.")
            return

        # Create behaviors directory if it doesn't exist
        behaviors_dir = os.path.join(self.project_path, 'behaviors')
        os.makedirs(behaviors_dir, exist_ok=True)

        # Create __init__.py if it doesn't exist
        init_file = os.path.join(behaviors_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Custom behaviors for this project."""\n')

        # Generate filename from behavior name
        filename = f"{behavior_name.lower()}.py"
        output_path = os.path.join(behaviors_dir, filename)

        # Check if file already exists
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self,
                "File Exists",
                f"A behavior file named '{filename}' already exists.\nOverwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            # Copy template to new file
            shutil.copy(self.selected_template, output_path)

            # Read the file content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace placeholder class name with actual behavior name
            # Look for common patterns like MyBehavior, PhysicsBehavior, AIBehavior
            import re
            content = re.sub(
                r'class \w+Behavior\(Component\):',
                f'class {behavior_name}(Component):',
                content
            )

            # Write back
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[NewBehaviorDialog] Created behavior: {output_path}")

            # Store created file path
            self.created_file_path = output_path

            # Success!
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create behavior file:\n{e}"
            )
            print(f"[NewBehaviorDialog] Error creating behavior: {e}")
            import traceback
            traceback.print_exc()

    def get_created_file_path(self) -> str:
        """Get the path to the created behavior file."""
        return self.created_file_path
