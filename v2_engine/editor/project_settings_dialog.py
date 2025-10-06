"""
Project Settings Dialog for Scribe Engine V2 Editor.

Provides UI for editing 2d_project.json configuration.
"""

import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QLabel, QMessageBox, QGroupBox, QListWidget,
    QInputDialog
)
from PyQt6.QtCore import Qt


class ProjectSettingsDialog(QDialog):
    """Dialog for editing project configuration."""

    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.config_path = os.path.join(project_path, '2d_project.json')
        self.config = None

        self.setWindowTitle("Project Settings")
        self.setModal(True)
        self.resize(600, 500)

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Create the UI layout."""
        layout = QVBoxLayout(self)

        # Tab widget for different setting categories
        tabs = QTabWidget()

        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")

        # Window tab
        window_tab = self.create_window_tab()
        tabs.addTab(window_tab, "Window")

        # Physics tab
        physics_tab = self.create_physics_tab()
        tabs.addTab(physics_tab, "Physics")

        # Assets tab
        assets_tab = self.create_assets_tab()
        tabs.addTab(assets_tab, "Assets")

        # Scenes tab
        scenes_tab = self.create_scenes_tab()
        tabs.addTab(scenes_tab, "Scenes")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def create_general_tab(self):
        """Create General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        # Project title
        self.title_edit = QLineEdit()
        form.addRow("Project Title:", self.title_edit)

        # Version
        self.version_edit = QLineEdit()
        form.addRow("Version:", self.version_edit)

        # Engine version (read-only)
        self.engine_version_label = QLabel()
        form.addRow("Engine Version:", self.engine_version_label)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def create_window_tab(self):
        """Create Window settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        # Resolution presets
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QVBoxLayout(resolution_group)

        resolution_form = QFormLayout()

        # Width
        self.window_width = QSpinBox()
        self.window_width.setRange(320, 7680)
        self.window_width.setSingleStep(10)
        resolution_form.addRow("Width:", self.window_width)

        # Height
        self.window_height = QSpinBox()
        self.window_height.setRange(240, 4320)
        self.window_height.setSingleStep(10)
        resolution_form.addRow("Height:", self.window_height)

        # Common presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))

        preset_720p = QPushButton("720p")
        preset_720p.clicked.connect(lambda: self.set_resolution(1280, 720))
        preset_layout.addWidget(preset_720p)

        preset_1080p = QPushButton("1080p")
        preset_1080p.clicked.connect(lambda: self.set_resolution(1920, 1080))
        preset_layout.addWidget(preset_1080p)

        preset_4k = QPushButton("4K")
        preset_4k.clicked.connect(lambda: self.set_resolution(3840, 2160))
        preset_layout.addWidget(preset_4k)

        preset_layout.addStretch()

        resolution_layout.addLayout(resolution_form)
        resolution_layout.addLayout(preset_layout)

        layout.addWidget(resolution_group)

        # Display options
        display_group = QGroupBox("Display")
        display_form = QFormLayout(display_group)

        self.window_title = QLineEdit()
        display_form.addRow("Window Title:", self.window_title)

        self.fullscreen = QCheckBox()
        display_form.addRow("Fullscreen:", self.fullscreen)

        self.resizable = QCheckBox()
        display_form.addRow("Resizable:", self.resizable)

        layout.addWidget(display_group)
        layout.addStretch()

        return widget

    def create_physics_tab(self):
        """Create Physics settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        # Gravity
        gravity_group = QGroupBox("Gravity")
        gravity_layout = QFormLayout(gravity_group)

        self.gravity_x = QSpinBox()
        self.gravity_x.setRange(-10000, 10000)
        self.gravity_x.setSingleStep(10)
        gravity_layout.addRow("X:", self.gravity_x)

        self.gravity_y = QSpinBox()
        self.gravity_y.setRange(-10000, 10000)
        self.gravity_y.setSingleStep(10)
        gravity_layout.addRow("Y:", self.gravity_y)

        # Gravity presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Presets:"))

        preset_none = QPushButton("None")
        preset_none.clicked.connect(lambda: self.set_gravity(0, 0))
        preset_layout.addWidget(preset_none)

        preset_earth = QPushButton("Earth")
        preset_earth.clicked.connect(lambda: self.set_gravity(0, 980))
        preset_layout.addWidget(preset_earth)

        preset_moon = QPushButton("Moon")
        preset_moon.clicked.connect(lambda: self.set_gravity(0, 162))
        preset_layout.addWidget(preset_moon)

        preset_layout.addStretch()

        gravity_layout.addRow("", preset_layout)

        layout.addWidget(gravity_group)

        # Pixels per meter
        physics_group = QGroupBox("Physics Scale")
        physics_form = QFormLayout(physics_group)

        self.pixels_per_meter = QSpinBox()
        self.pixels_per_meter.setRange(1, 1000)
        self.pixels_per_meter.setValue(100)
        physics_form.addRow("Pixels per Meter:", self.pixels_per_meter)

        layout.addWidget(physics_group)
        layout.addStretch()

        return widget

    def create_assets_tab(self):
        """Create Assets paths tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form = QFormLayout()

        info_label = QLabel("Asset folder paths (relative to project root)")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.sprites_path = QLineEdit()
        form.addRow("Sprites:", self.sprites_path)

        self.sounds_path = QLineEdit()
        form.addRow("Sounds:", self.sounds_path)

        self.music_path = QLineEdit()
        form.addRow("Music:", self.music_path)

        self.fonts_path = QLineEdit()
        form.addRow("Fonts:", self.fonts_path)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def create_scenes_tab(self):
        """Create Scenes management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info label
        info_label = QLabel("Manage game scenes and set entry scene")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Scenes list
        scenes_group = QGroupBox("Scenes")
        scenes_layout = QVBoxLayout(scenes_group)

        self.scenes_list = QListWidget()
        scenes_layout.addWidget(self.scenes_list)

        # Scene buttons
        scene_buttons = QHBoxLayout()

        add_scene_btn = QPushButton("Add Scene")
        add_scene_btn.clicked.connect(self.add_scene)
        scene_buttons.addWidget(add_scene_btn)

        remove_scene_btn = QPushButton("Remove Scene")
        remove_scene_btn.clicked.connect(self.remove_scene)
        scene_buttons.addWidget(remove_scene_btn)

        scene_buttons.addStretch()

        scenes_layout.addLayout(scene_buttons)
        layout.addWidget(scenes_group)

        # Entry scene
        entry_group = QGroupBox("Entry Scene")
        entry_layout = QFormLayout(entry_group)

        self.entry_scene_combo = QComboBox()
        entry_layout.addRow("Start Scene:", self.entry_scene_combo)

        layout.addWidget(entry_group)
        layout.addStretch()

        return widget

    def add_scene(self):
        """Add a new scene to the project."""
        scene_name, ok = QInputDialog.getText(
            self,
            "Add Scene",
            "Enter scene name:"
        )

        if ok and scene_name:
            # Create scene file path
            scene_file = f"scenes/{scene_name.lower()}.py"
            scene_class = scene_name

            # Add to config
            scenes_config = self.config.get('scenes', {})
            scene_list = scenes_config.get('scenes', [])

            # Check if scene already exists
            for scene in scene_list:
                if scene['name'] == scene_name:
                    QMessageBox.warning(
                        self,
                        "Scene Exists",
                        f"Scene '{scene_name}' already exists."
                    )
                    return

            # Add new scene
            scene_list.append({
                'name': scene_name,
                'file': scene_file,
                'class': scene_class
            })

            scenes_config['scenes'] = scene_list
            self.config['scenes'] = scenes_config

            # Create scene file
            self.create_scene_file(scene_name, scene_file, scene_class)

            # Refresh UI
            self.load_scenes_list()

    def remove_scene(self):
        """Remove selected scene from project."""
        current_item = self.scenes_list.currentItem()
        if not current_item:
            return

        scene_name = current_item.text()

        reply = QMessageBox.question(
            self,
            "Remove Scene",
            f"Remove scene '{scene_name}'?\n\nNote: Scene file will not be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from config
            scenes_config = self.config.get('scenes', {})
            scene_list = scenes_config.get('scenes', [])

            scene_list = [s for s in scene_list if s['name'] != scene_name]

            scenes_config['scenes'] = scene_list
            self.config['scenes'] = scenes_config

            # If this was the entry scene, clear it
            if scenes_config.get('entry_scene') == scene_name:
                scenes_config['entry_scene'] = ''

            # Refresh UI
            self.load_scenes_list()

    def create_scene_file(self, scene_name, scene_file, scene_class):
        """Create a new scene Python file."""
        scene_path = os.path.join(self.project_path, scene_file)

        # Create scenes directory if it doesn't exist
        os.makedirs(os.path.dirname(scene_path), exist_ok=True)

        # Check if file already exists
        if os.path.exists(scene_path):
            return  # Don't overwrite existing file

        # Create basic scene template
        template = f'''"""
Scene: {scene_name}
Generated by Scribe Engine V2 Editor
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.core.camera import Camera
from v2_engine.utils.math import Vector2

# Sprite imports
from v2_engine.sprites.sprite import Sprite

class {scene_class}(Scene):
    """Auto-generated scene."""

    def __init__(self, game):
        super().__init__(game)

        # Initialize sprite groups
        from v2_engine.sprites.group import SpriteGroup
        self.sprite_groups["all"] = SpriteGroup("all")

    def on_enter(self):
        """Called when scene becomes active."""
        super().on_enter()

        # Initialize camera
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()
        self.camera = Camera(screen_width, screen_height)

        # Background settings
        self.background_color = (36, 31, 49)

    def update(self, dt):
        """Update all sprites and components."""
        super().update(dt)

    def render(self, screen):
        """Render all sprites with camera."""
        # Draw background
        screen.fill(self.background_color)

        # Render all sprite groups
        self.sprite_groups["all"].render(screen, self.camera)
'''

        with open(scene_path, 'w') as f:
            f.write(template)

        print(f"[ProjectSettings] Created scene file: {scene_path}")

    def load_scenes_list(self):
        """Load scenes into the list widget."""
        self.scenes_list.clear()
        self.entry_scene_combo.clear()

        scenes_config = self.config.get('scenes', {})
        scene_list = scenes_config.get('scenes', [])

        for scene in scene_list:
            scene_name = scene.get('name', '')
            self.scenes_list.addItem(scene_name)
            self.entry_scene_combo.addItem(scene_name)

        # Set current entry scene
        entry_scene = scenes_config.get('entry_scene', '')
        index = self.entry_scene_combo.findText(entry_scene)
        if index >= 0:
            self.entry_scene_combo.setCurrentIndex(index)

    def set_resolution(self, width, height):
        """Set resolution to preset values."""
        self.window_width.setValue(width)
        self.window_height.setValue(height)

    def set_gravity(self, x, y):
        """Set gravity to preset values."""
        self.gravity_x.setValue(x)
        self.gravity_y.setValue(y)

    def load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

            # General
            self.title_edit.setText(self.config.get('title', ''))
            self.version_edit.setText(self.config.get('version', '1.0.0'))
            self.engine_version_label.setText(self.config.get('engine_version', '2.0.0'))

            # Window
            window_config = self.config.get('window', {})
            self.window_width.setValue(window_config.get('width', 800))
            self.window_height.setValue(window_config.get('height', 600))
            self.window_title.setText(window_config.get('title', ''))
            self.fullscreen.setChecked(window_config.get('fullscreen', False))
            self.resizable.setChecked(window_config.get('resizable', False))

            # Physics
            physics_config = self.config.get('physics', {})
            gravity = physics_config.get('gravity', {'x': 0, 'y': 980})
            self.gravity_x.setValue(gravity.get('x', 0))
            self.gravity_y.setValue(gravity.get('y', 980))
            self.pixels_per_meter.setValue(physics_config.get('pixels_per_meter', 100))

            # Assets
            assets_config = self.config.get('assets', {})
            self.sprites_path.setText(assets_config.get('sprites', 'assets/sprites/'))
            self.sounds_path.setText(assets_config.get('sounds', 'assets/sounds/'))
            self.music_path.setText(assets_config.get('music', 'assets/music/'))
            self.fonts_path.setText(assets_config.get('fonts', 'assets/fonts/'))

            # Scenes
            self.load_scenes_list()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Error Loading Config',
                f'Failed to load project configuration:\n{str(e)}'
            )

    def save_config(self):
        """Save configuration to JSON file."""
        try:
            # Update config dictionary
            self.config['title'] = self.title_edit.text()
            self.config['version'] = self.version_edit.text()

            # Window settings
            self.config['window'] = {
                'width': self.window_width.value(),
                'height': self.window_height.value(),
                'title': self.window_title.text(),
                'fullscreen': self.fullscreen.isChecked(),
                'resizable': self.resizable.isChecked()
            }

            # Physics settings
            self.config['physics'] = {
                'gravity': {
                    'x': self.gravity_x.value(),
                    'y': self.gravity_y.value()
                },
                'pixels_per_meter': self.pixels_per_meter.value()
            }

            # Assets settings
            self.config['assets'] = {
                'sprites': self.sprites_path.text(),
                'sounds': self.sounds_path.text(),
                'music': self.music_path.text(),
                'fonts': self.fonts_path.text()
            }

            # Scenes settings
            if 'scenes' not in self.config:
                self.config['scenes'] = {}
            self.config['scenes']['entry_scene'] = self.entry_scene_combo.currentText()

            # Write to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            QMessageBox.information(
                self,
                'Settings Saved',
                'Project settings have been saved successfully.'
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Error Saving Config',
                f'Failed to save project configuration:\n{str(e)}'
            )
