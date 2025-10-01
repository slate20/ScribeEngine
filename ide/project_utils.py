"""
Project utility functions for IDE.

Handles project type detection and metadata extraction.
"""

import os
import json


class ProjectType:
    """Enum for project types."""
    V1 = "v1"  # Text-based adventure engine
    V2 = "v2"  # Scene-based 2D game engine
    UNKNOWN = "unknown"


def detect_project_type(project_path: str) -> str:
    """
    Detect whether a project is V1 or V2.

    Args:
        project_path: Absolute path to project directory

    Returns:
        ProjectType constant (V1, V2, or UNKNOWN)
    """
    # Check for V2 project config
    v2_config = os.path.join(project_path, '2d_project.json')
    if os.path.exists(v2_config):
        return ProjectType.V2

    # Check for V1 project config
    v1_config = os.path.join(project_path, 'project.json')
    if os.path.exists(v1_config):
        return ProjectType.V1

    return ProjectType.UNKNOWN


def get_project_metadata(project_path: str) -> dict:
    """
    Get project metadata (title, version, etc).

    Args:
        project_path: Absolute path to project directory

    Returns:
        Dictionary with project metadata
    """
    project_type = detect_project_type(project_path)

    if project_type == ProjectType.V2:
        config_file = os.path.join(project_path, '2d_project.json')
    elif project_type == ProjectType.V1:
        config_file = os.path.join(project_path, 'project.json')
    else:
        return {
            'type': ProjectType.UNKNOWN,
            'title': os.path.basename(project_path),
            'version': 'unknown'
        }

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        return {
            'type': project_type,
            'title': config.get('title', 'Untitled'),
            'version': config.get('version', '1.0.0'),
            'engine_version': config.get('engine_version', 'unknown'),
            'config': config
        }
    except Exception as e:
        print(f"Error loading project metadata: {e}")
        return {
            'type': project_type,
            'title': os.path.basename(project_path),
            'version': 'unknown',
            'error': str(e)
        }


def list_projects(projects_root: str) -> list:
    """
    List all projects in the projects root directory.

    Args:
        projects_root: Path to directory containing projects

    Returns:
        List of dictionaries with project info
    """
    if not projects_root or not os.path.exists(projects_root):
        return []

    projects = []

    try:
        for item in os.listdir(projects_root):
            project_path = os.path.join(projects_root, item)

            # Skip non-directories
            if not os.path.isdir(project_path):
                continue

            # Get project metadata
            metadata = get_project_metadata(project_path)

            # Only include V1 and V2 projects
            if metadata['type'] != ProjectType.UNKNOWN:
                projects.append({
                    'name': item,
                    'path': project_path,
                    **metadata
                })

    except Exception as e:
        print(f"Error listing projects: {e}")

    return projects


def create_v2_project(project_path: str, title: str) -> bool:
    """
    Create a new V2 project with default structure.

    Args:
        project_path: Path where project should be created
        title: Project title

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create project directory
        os.makedirs(project_path, exist_ok=True)

        # Create subdirectories
        os.makedirs(os.path.join(project_path, 'scenes'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'assets', 'sprites'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'assets', 'sounds'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'assets', 'music'), exist_ok=True)

        # Create 2d_project.json
        config = {
            "title": title,
            "version": "1.0.0",
            "engine_version": "2.0.0",

            "window": {
                "width": 800,
                "height": 600,
                "fullscreen": False,
                "resizable": False,
                "title": title
            },

            "physics": {
                "gravity": {
                    "x": 0,
                    "y": 980
                },
                "pixels_per_meter": 100
            },

            "scenes": {
                "entry_scene": "main_menu",
                "scenes": [
                    {
                        "name": "main_menu",
                        "file": "scenes/main_menu.py",
                        "class": "MainMenuScene"
                    }
                ]
            },

            "assets": {
                "sprites": "assets/sprites/",
                "sounds": "assets/sounds/",
                "music": "assets/music/"
            }
        }

        config_path = os.path.join(project_path, '2d_project.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Create default main menu scene
        main_menu_content = '''"""
Main Menu Scene
"""

import pygame
from v2_engine.core.scene import Scene
from v2_engine.ui.button import Button
from v2_engine.ui.text import TextLabel


class MainMenuScene(Scene):
    """Main menu with title and start button."""

    def __init__(self, game):
        super().__init__(game)
        self.title = None
        self.start_button = None
        self.quit_button = None

    def on_enter(self):
        """Initialize menu when scene loads."""
        width = self.game.project_config['window']['width']
        height = self.game.project_config['window']['height']

        # Title
        self.title = TextLabel(width // 2, 100, "{}", font_size=64)
        self.title.align = "center"
        self.title.text_color = (255, 255, 0)

        # Start button
        self.start_button = Button(width // 2, height // 2, 200, 60, "START GAME")
        self.start_button.on_click = self.start_game

        # Quit button
        self.quit_button = Button(width // 2, height // 2 + 80, 200, 60, "QUIT")
        self.quit_button.on_click = self.quit_game

        self.ui_elements = [self.title, self.start_button, self.quit_button]

    def start_game(self):
        """Start button callback."""
        # TODO: Load first level
        print("Start game clicked")

    def quit_game(self):
        """Quit button callback."""
        self.game.quit()

    def handle_event(self, event):
        """Handle input events."""
        for element in self.ui_elements:
            element.handle_event(event)

    def update(self, dt):
        """Update menu."""
        for element in self.ui_elements:
            element.update(dt)

    def render(self, screen):
        """Render menu."""
        # Gradient background
        for y in range(screen.get_height()):
            progress = y / screen.get_height()
            color = (
                int(20 * (1 - progress)),
                int(30 * (1 - progress)),
                int(60 * (1 - progress))
            )
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))

        # Render UI
        for element in self.ui_elements:
            element.render(screen)
'''.format(title.upper())

        scene_path = os.path.join(project_path, 'scenes', 'main_menu.py')
        with open(scene_path, 'w') as f:
            f.write(main_menu_content)

        return True

    except Exception as e:
        print(f"Error creating V2 project: {e}")
        return False
