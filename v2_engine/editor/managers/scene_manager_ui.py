"""
Scene Manager UI - Manages scene operations and UI updates.

Handles:
- Scene saving and loading
- Scene creation and switching
- Scene menu updates
- Scene configuration management
"""

import os
import json
import re
import importlib
import sys
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QInputDialog, QMessageBox


class SceneManagerUI(QObject):
    """
    Manages scene-related UI operations and file management.

    Signals:
        scene_switched: Emitted when scene changes (scene_name)
        scene_created: Emitted when new scene is created (scene_name)
        scene_saved: Emitted when scene is saved (scene_name)
    """

    # Signals
    scene_switched = pyqtSignal(str)  # scene_name
    scene_created = pyqtSignal(str)   # scene_name
    scene_saved = pyqtSignal(str)     # scene_name

    def __init__(self, editor):
        """
        Initialize the scene manager UI.

        Args:
            editor: Reference to EditorWindow
        """
        super().__init__()
        self.editor = editor

    def save_scene(self):
        """
        Save the current scene to file.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.editor.game.scene_manager or not self.editor.game.scene_manager.current_scene:
            print("[SceneManagerUI] No scene to save")
            return False

        scene_name = self.editor.game.scene_manager.current_scene
        scene = self.editor.game.scene_manager.scenes[scene_name]

        # Find scene file path from project config
        config_path = os.path.join(self.editor.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Find the scene file path
            scene_file = None
            for scene_info in config.get('scenes', {}).get('scenes', []):
                if scene_info['name'] == scene_name:
                    scene_file = os.path.join(self.editor.project_path, scene_info['file'])
                    break

            if not scene_file:
                # Fallback to guessing
                scene_file = os.path.join(self.editor.project_path, 'scenes', f'{scene_name}.py')
                print(f"[SceneManagerUI] Warning: Scene file not found in config, using: {scene_file}")

            # Save scene
            self.editor.scene_serializer.save_scene(scene, scene_file)
            print(f"[SceneManagerUI] Scene saved successfully: {scene_file}")

            # Optional: Save metadata
            metadata_file = scene_file.replace('.py', '.meta.json')
            self.editor.scene_serializer.save_scene_metadata(scene, metadata_file)

            # Emit signal
            self.scene_saved.emit(scene_name)

            return True

        except Exception as e:
            print(f"[SceneManagerUI] Error saving scene: {e}")
            import traceback
            traceback.print_exc()
            return False

    def reload_scene(self, scene_name):
        """
        Reload a scene from disk.

        Args:
            scene_name: Name of scene to reload
        """
        # Find the scene module
        scene_module_name = None
        for key in sys.modules.keys():
            if scene_name in key and 'scenes' in key:
                scene_module_name = key
                break

        if scene_module_name:
            # Reload the module
            module = sys.modules[scene_module_name]
            importlib.reload(module)
            print(f"[SceneManagerUI] Reloaded module: {scene_module_name}")

        # Re-register the scene
        self.editor.game.scene_manager.scenes.clear()
        self.editor.game._load_scenes()

        # Transition to reloaded scene
        self.editor.game.scene_manager.load_scene(scene_name)
        self.editor.game.scene_manager._perform_scene_transition()

    def reload_scene_from_file(self, scene_name):
        """
        Reload a scene module from disk (editor mode only).

        Args:
            scene_name: Name of scene to reload from file
        """
        # Find the scene file path
        config_path = os.path.join(self.editor.project_path, '2d_project.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Find the scene file
            scene_file = None
            scene_info = None
            for info in config.get('scenes', {}).get('scenes', []):
                if info['name'] == scene_name:
                    scene_file = info['file']
                    scene_info = info
                    break

            if not scene_file:
                print(f"[SceneManagerUI] Scene file not found for: {scene_name}")
                return

            # Convert file path to module name (e.g., "scenes/main_scene.py" -> "scenes.main_scene")
            module_name = scene_file.replace('/', '.').replace('\\', '.').replace('.py', '')

            # Reload the module if it's already loaded
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                print(f"[SceneManagerUI] Reloaded scene module: {module_name}")

            # Re-import and recreate the scene instance
            scene_module = importlib.import_module(module_name)
            scene_class = getattr(scene_module, scene_info['class'])

            # Replace the scene instance in the scene manager
            self.editor.game.scene_manager.scenes[scene_name] = scene_class(self.editor.game)
            print(f"[SceneManagerUI] Recreated scene instance: {scene_name}")

        except Exception as e:
            print(f"[SceneManagerUI] Error reloading scene {scene_name}: {e}")
            import traceback
            traceback.print_exc()

    def switch_to_scene(self, scene_name):
        """
        Switch to a different scene.

        Args:
            scene_name: Name of scene to switch to

        Returns:
            bool: True if switched successfully, False otherwise
        """
        if not self.editor.game.scene_manager:
            print("[SceneManagerUI] No scene manager available")
            return False

        if scene_name == self.editor.game.scene_manager.current_scene:
            print(f"[SceneManagerUI] Already viewing scene: {scene_name}")
            return False

        try:
            # Save current scene before switching
            if self.editor.game.scene_manager.current_scene:
                self.save_scene()
                print(f"[SceneManagerUI] Saved current scene before switching")

            # Reload the target scene from disk (editor mode only)
            self.reload_scene_from_file(scene_name)

            # Load and transition to the scene
            self.editor.game.scene_manager.load_scene(scene_name)
            self.editor.game.scene_manager._perform_scene_transition()

            # Emit signal
            self.scene_switched.emit(scene_name)

            print(f"[SceneManagerUI] Switched to scene: {scene_name}")
            return True

        except Exception as e:
            print(f"[SceneManagerUI] Error switching to scene '{scene_name}': {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_new_scene(self, parent_widget):
        """
        Create a new scene with dialog.

        Args:
            parent_widget: Parent widget for dialogs

        Returns:
            str: Name of created scene or None if cancelled
        """
        # Prompt for scene name
        scene_name, ok = QInputDialog.getText(
            parent_widget,
            'New Scene',
            'Enter scene name (e.g., "level_2", "menu"):',
            text='new_scene'
        )

        if not ok or not scene_name:
            return None

        # Validate scene name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', scene_name):
            QMessageBox.warning(
                parent_widget,
                'Invalid Name',
                'Scene name must start with a letter or underscore and contain only letters, numbers, and underscores.'
            )
            return None

        try:
            # Read project config
            config_path = os.path.join(self.editor.project_path, '2d_project.json')
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Check if scene already exists
            scenes = config.get('scenes', {}).get('scenes', [])
            for scene_info in scenes:
                if scene_info['name'] == scene_name:
                    QMessageBox.warning(
                        parent_widget,
                        'Scene Exists',
                        f'A scene named "{scene_name}" already exists.'
                    )
                    return None

            # Create scene file path
            class_name = ''.join(word.capitalize() for word in scene_name.split('_')) + 'Scene'
            scene_file = f'scenes/{scene_name}.py'
            scene_file_path = os.path.join(self.editor.project_path, scene_file)

            # Create scenes directory if it doesn't exist
            os.makedirs(os.path.dirname(scene_file_path), exist_ok=True)

            # Generate empty scene file
            scene_code = f'''"""
Scene: {class_name}
Generated by Scribe Engine V2 Editor
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.core.camera import Camera
from v2_engine.utils.math import Vector2
from v2_engine.sprites.sprite import Sprite

class {class_name}(Scene):
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

        # Add sprites here


    def render(self, screen):
        """Render all sprites with camera."""
        # Clear screen
        screen.fill((40, 40, 50))  # Dark gray background

        # Render all sprite groups
        self.sprite_groups["all"].render(screen, self.camera)

'''

            # Write scene file
            with open(scene_file_path, 'w') as f:
                f.write(scene_code)

            # Update project config
            scenes.append({
                'name': scene_name,
                'file': scene_file,
                'class': class_name
            })

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"[SceneManagerUI] Created new scene: {scene_name} at {scene_file}")

            # Reload project config and scenes
            self.editor.game.project_config = self.editor.game.load_project_config()

            # Import and register the new scene
            try:
                module_path = scene_file.replace('/', '.').replace('.py', '')
                module = importlib.import_module(module_path)
                SceneClass = getattr(module, class_name)
                scene_instance = SceneClass(self.editor.game)
                self.editor.game.scene_manager.register_scene(scene_name, scene_instance)
                print(f"[SceneManagerUI] Registered scene: {scene_name}")
            except Exception as e:
                print(f"[SceneManagerUI] Error registering scene: {e}")
                import traceback
                traceback.print_exc()

            # Emit signal
            self.scene_created.emit(scene_name)

            return scene_name

        except Exception as e:
            print(f"[SceneManagerUI] Error creating scene: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                parent_widget,
                'Error',
                f'Failed to create scene: {str(e)}'
            )
            return None

    def get_scenes_config(self):
        """
        Get scenes configuration from project config.

        Returns:
            list: List of scene info dictionaries
        """
        config_path = os.path.join(self.editor.project_path, '2d_project.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get('scenes', {}).get('scenes', [])
        except Exception as e:
            print(f"[SceneManagerUI] Error loading scenes config: {e}")
            return []

    def get_current_scene_name(self):
        """
        Get the current scene name.

        Returns:
            str: Current scene name or None
        """
        if self.editor.game.scene_manager:
            return self.editor.game.scene_manager.current_scene
        return None
