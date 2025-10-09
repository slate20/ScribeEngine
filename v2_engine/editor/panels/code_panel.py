"""
Code Panel - Code editor with file navigation and split view support.

This panel encapsulates:
- Code tab with file navigator and editor
- Split view code tabs (instance/behavior editing)
- Scene code loading and refresh
- File selection handling
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from v2_engine.editor.code_editor import CodeEditor


class CodePanel(QWidget):
    """
    Code panel containing file navigator and code editor for Code tab.

    Signals:
        file_saved: Emitted when a file is saved (str: file_path)
        file_saved_and_reload: Emitted when a file is saved with reload request (str: file_path)
        file_selected: Emitted when a file is selected in navigator (str: file_path)
    """

    # Signals
    file_saved = pyqtSignal(str)
    file_saved_and_reload = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    def __init__(self, editor, theme, project_path):
        """
        Initialize the code panel.

        Args:
            editor: Reference to EditorWindow
            theme: EditorTheme instance
            project_path: Path to the project directory
        """
        super().__init__()
        self.editor = editor
        self.theme = theme
        self.project_path = project_path
        self.current_scene_file = None

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the code panel UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create splitter for resizable panels
        code_splitter = QSplitter(Qt.Orientation.Horizontal)

        # File navigator on the left
        from v2_engine.editor.widgets.file_navigator import FileNavigator
        self.file_navigator = FileNavigator(self.theme, self.project_path)
        self.file_navigator.file_selected.connect(self._on_file_selected)
        self.file_navigator.setMinimumWidth(150)
        code_splitter.addWidget(self.file_navigator)

        # Code editor on the right
        self.code_editor = CodeEditor(self.theme)
        self.code_editor.file_saved.connect(self._on_file_saved)
        self.code_editor.file_saved_and_reload.connect(self._on_file_saved_and_reload)
        code_splitter.addWidget(self.code_editor)

        # Set initial sizes (250px for navigator, rest for editor)
        code_splitter.setSizes([250, 800])

        layout.addWidget(code_splitter)

    # Signal handlers (internal)

    def _on_file_selected(self, file_path):
        """Handle file selection from file navigator."""
        self.file_selected.emit(file_path)

    def _on_file_saved(self, file_path):
        """Handle file saved event."""
        self.file_saved.emit(file_path)

    def _on_file_saved_and_reload(self, file_path):
        """Handle file saved with reload request."""
        self.file_saved_and_reload.emit(file_path)

    # Public API

    def refresh_scene_code(self, game):
        """
        Load and display the current scene file in code view.

        Args:
            game: Game instance with scene_manager
        """
        if not game.scene_manager or not game.scene_manager.current_scene:
            self.code_editor.setPlainText("# No scene loaded")
            self.current_scene_file = None
            return

        scene_name = game.scene_manager.current_scene

        # Find scene file path from config
        import json
        config_path = os.path.join(self.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            scene_file = None
            for scene_info in config.get('scenes', {}).get('scenes', []):
                if scene_info['name'] == scene_name:
                    scene_file = os.path.join(self.project_path, scene_info['file'])
                    break

            if scene_file and os.path.exists(scene_file):
                # Store current scene file path
                self.current_scene_file = scene_file

                # Load scene file in Code view
                self.code_editor.load_file(scene_file)

                # Update file navigator to highlight scene file
                if hasattr(self, 'file_navigator'):
                    self.file_navigator.set_current_file(scene_file)
            else:
                self.current_scene_file = None
                error_msg = f"# Scene file not found: {scene_file}"
                self.code_editor.setPlainText(error_msg)

        except Exception as e:
            self.current_scene_file = None
            error_msg = f"# Error loading scene code: {str(e)}"
            self.code_editor.setPlainText(error_msg)
            print(f"[CodePanel] Error loading scene code: {e}")

    def load_file(self, file_path):
        """
        Load a file into the code editor.

        Args:
            file_path: Path to the file to load
        """
        if os.path.exists(file_path):
            self.code_editor.load_file(file_path)
            if hasattr(self, 'file_navigator'):
                self.file_navigator.set_current_file(file_path)
        else:
            self.code_editor.setPlainText(f"# File not found: {file_path}")

    def get_current_scene_file(self):
        """Get the currently loaded scene file path."""
        return self.current_scene_file if self.current_scene_file else ""


class SplitCodePanel(QWidget):
    """
    Split view code panel with sprite-specific code editing.

    This panel manages the code editor in Split view with support for:
    - Instance code editing (sprite-specific sections)
    - Behavior/component code editing
    - Dynamic tab management based on selection
    """

    # Signals
    file_saved = pyqtSignal(str)
    file_saved_and_reload = pyqtSignal(str)
    switch_to_instance_requested = pyqtSignal()

    def __init__(self, editor, theme, project_path):
        """
        Initialize the split code panel.

        Args:
            editor: Reference to EditorWindow
            theme: EditorTheme instance
            project_path: Path to the project directory
        """
        super().__init__()
        self.editor = editor
        self.theme = theme
        self.project_path = project_path

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the split code panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Import CodeTabBar
        from v2_engine.editor.widgets.code_tab_bar import CodeTabBar

        # Code tab bar with instance and behavior tabs
        self.split_code_tabs = CodeTabBar(self.theme)
        self.split_code_tabs.switch_to_instance_edit.connect(self._on_switch_to_instance)
        self.split_code_tabs.currentChanged.connect(self._on_tab_changed)

        # Add placeholder tab
        self.split_code_tabs.addTab(
            QLabel("Select a sprite to edit its code", alignment=Qt.AlignmentFlag.AlignCenter),
            "No Selection"
        )

        layout.addWidget(self.split_code_tabs)

    # Signal handlers (internal)

    def _on_switch_to_instance(self):
        """Handle switch to instance editing signal."""
        self.switch_to_instance_requested.emit()

    def _on_tab_changed(self, index):
        """Handle tab change."""
        # Could add additional logic here if needed
        pass

    def _on_file_saved(self, file_path):
        """Handle file saved event."""
        self.file_saved.emit(file_path)

    def _on_file_saved_and_reload(self, file_path):
        """Handle file saved with reload request."""
        self.file_saved_and_reload.emit(file_path)

    # Public API

    def update_tabs(self, sprite, current_scene_file):
        """
        Update split view code tabs based on sprite selection.

        Args:
            sprite: Selected sprite object or None
            current_scene_file: Path to current scene file
        """
        # Clear existing tabs
        self.split_code_tabs.clear_tabs()

        if not sprite:
            # No selection - show full scene code
            scene_editor = CodeEditor(self.theme)
            scene_editor.file_saved.connect(self._on_file_saved)
            scene_editor.file_saved_and_reload.connect(self._on_file_saved_and_reload)

            if current_scene_file and os.path.exists(current_scene_file):
                scene_editor.load_file(current_scene_file)

            self.split_code_tabs.addTab(scene_editor, "Scene Code")
            return

        sprite_name = getattr(sprite, 'name', sprite.__class__.__name__)

        # Create instance code editor
        instance_editor = CodeEditor(self.theme)
        instance_editor.file_saved.connect(self._on_file_saved)
        instance_editor.file_saved_and_reload.connect(self._on_file_saved_and_reload)

        # Load scene file and extract sprite section
        if current_scene_file and os.path.exists(current_scene_file):
            from v2_engine.editor.scene_code_extractor import SceneCodeExtractor

            extractor = SceneCodeExtractor(current_scene_file)
            section_info = extractor.find_sprite_section(sprite_name)

            print(f"[SplitCodePanel] Looking for sprite: '{sprite_name}' in {current_scene_file}")
            print(f"[SplitCodePanel] Extraction result: {section_info is not None}")

            if section_info:
                start_line, end_line, code_section = section_info

                # Show extracted section with context
                context_lines = 2
                context_start = max(0, start_line - context_lines)
                context_end = min(extractor.get_line_count() - 1, end_line + context_lines)

                # Get full context
                full_lines = extractor.scene_code.split('\n')
                context_code = '\n'.join(full_lines[context_start:context_end + 1])

                # Add helpful comment at top
                header = f"# Sprite: {sprite_name} (Lines {start_line + 1}-{end_line + 1})\n"
                header += "# Edit this sprite's instance code below:\n\n"

                instance_editor.setPlainText(header + context_code)

                # Detect overrides
                has_overrides = extractor.has_custom_overrides(sprite_name)
            else:
                # Couldn't find sprite - show full scene
                instance_editor.load_file(current_scene_file)
                has_overrides = False
        else:
            has_overrides = False

        # Add instance tab
        self.split_code_tabs.set_instance_tab(instance_editor, has_overrides)

        # Add behavior class tabs
        if hasattr(sprite, 'components'):
            for component in sprite.components.values():
                behavior_name = component.__class__.__name__

                # Create behavior editor
                behavior_editor = CodeEditor(self.theme)
                behavior_editor.file_saved.connect(self._on_file_saved)
                behavior_editor.file_saved_and_reload.connect(self._on_file_saved_and_reload)

                # Load behavior file
                import inspect
                try:
                    behavior_file = inspect.getfile(component.__class__)
                    if os.path.exists(behavior_file):
                        behavior_editor.load_file(behavior_file)
                        self.split_code_tabs.add_behavior_tab(behavior_editor, behavior_name, behavior_file)
                except:
                    pass

    def switch_to_instance_tab(self):
        """Switch to first tab (instance code)."""
        if hasattr(self, 'split_code_tabs'):
            self.split_code_tabs.setCurrentIndex(0)
