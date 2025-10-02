"""
Main game controller for Scribe Engine V2.

Handles pygame initialization, game loop, and core engine services.
"""

import os
import sys
import json
import pygame

from v2_engine.core.scene import SceneManager
from v2_engine.core.input import InputHandler
from v2_engine.core.time import TimeManager


class Game:
    """
    Main game controller for Scribe Engine V2.

    Handles pygame initialization, game loop, scene management,
    and core engine services.
    """

    def __init__(self, project_path: str, editor_mode: bool = False):
        """
        Initialize the game engine.

        Args:
            project_path: Path to the game project directory
            editor_mode: If True, game is running inside the editor
        """
        self.project_path = os.path.abspath(project_path)
        self.project_config = None
        self.screen = None
        self.clock = None
        self.running = False
        self.editor_mode = editor_mode

        # Core systems
        self.scene_manager = None
        self.input_handler = None
        self.time_manager = None

        print(f"[Game] Initialized with project: {self.project_path}")
        if editor_mode:
            print("[Game] Running in editor mode")

    def initialize(self) -> bool:
        """
        Initialize pygame and core engine systems.

        Returns:
            True if initialization successful, False otherwise
        """
        print("[Game] Initializing engine...")

        # Load project configuration
        try:
            self.project_config = self.load_project_config()
        except Exception as e:
            print(f"[Game] Error loading project config: {e}")
            return False

        # Initialize pygame
        try:
            pygame.init()
            print("[Game] Pygame initialized")
        except Exception as e:
            print(f"[Game] Error initializing pygame: {e}")
            return False

        # Create game window (unless in editor mode, where editor controls the window)
        if not self.editor_mode:
            try:
                window_config = self.project_config.get('window', {})
                width = window_config.get('width', 800)
                height = window_config.get('height', 600)
                title = window_config.get('title', 'Scribe Engine V2 Game')
                fullscreen = window_config.get('fullscreen', False)

                flags = pygame.DOUBLEBUF
                if fullscreen:
                    flags |= pygame.FULLSCREEN

                self.screen = pygame.display.set_mode((width, height), flags)
                pygame.display.set_caption(title)
                print(f"[Game] Created window: {width}x{height} - {title}")
            except Exception as e:
                print(f"[Game] Error creating window: {e}")
                return False
        else:
            # In editor mode, use the editor's screen
            self.screen = pygame.display.get_surface()
            print(f"[Game] Using editor's window")

        # Initialize clock
        self.clock = pygame.time.Clock()

        # Initialize core systems
        self.scene_manager = SceneManager(self)
        self.input_handler = InputHandler()
        self.time_manager = TimeManager(target_fps=60)
        print("[Game] Core systems initialized")

        # Add project directory to Python path for scene imports
        if self.project_path not in sys.path:
            sys.path.insert(0, self.project_path)

        # Load and register scenes
        try:
            self._load_scenes()
        except Exception as e:
            print(f"[Game] Error loading scenes: {e}")
            return False

        return True

    def load_project_config(self) -> dict:
        """
        Load and validate 2d_project.json configuration.

        Returns:
            Project configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config is invalid JSON
        """
        config_path = os.path.join(self.project_path, '2d_project.json')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Project config not found: {config_path}")

        with open(config_path, 'r') as f:
            config = json.load(f)

        print(f"[Game] Loaded project config: {config.get('title', 'Unknown')}")
        return config

    def run(self):
        """
        Start the main game loop.

        Game loop handles:
        - Event processing
        - Fixed timestep updates
        - Variable framerate rendering
        - Scene management
        """
        self.running = True
        print("[Game] Starting game loop...")

        while self.running:
            # Calculate delta time
            dt = self.time_manager.update()

            # Cap delta time to prevent spiral of death
            dt = min(dt, 0.1)  # Max 100ms per frame

            # Process events
            self._process_events()

            # Update game state
            self._update(dt)

            # Render frame
            self._render()

            # Maintain target frame rate
            self.clock.tick(60)

        print("[Game] Game loop ended")

    def quit(self):
        """Clean shutdown of pygame and engine systems."""
        print("[Game] Shutting down...")
        self.running = False
        pygame.quit()

    # Internal methods

    def _process_events(self):
        """Process pygame events and update input handler."""
        events = pygame.event.get()

        for event in events:
            # Handle quit event
            if event.type == pygame.QUIT:
                self.quit()
                return

            # Handle ESC key to quit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit()
                return

            # Pass event to scene
            if self.scene_manager:
                self.scene_manager.handle_event(event)

        # Update input handler
        if self.input_handler:
            self.input_handler.update(events)

    def _update(self, dt: float):
        """
        Update current scene with delta time.

        Args:
            dt: Delta time in seconds
        """
        if self.scene_manager:
            self.scene_manager.update(dt)

    def _render(self):
        """Render current scene to screen."""
        if not self.running:
            return

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Render scene
        if self.scene_manager:
            self.scene_manager.render(self.screen)

        # Display FPS in window title (debug)
        fps = self.time_manager.fps
        if fps > 0:
            title = self.project_config.get('window', {}).get('title', 'Scribe Engine V2')
            pygame.display.set_caption(f"{title} - {fps} FPS")

        # Flip display
        pygame.display.flip()

    def _load_scenes(self):
        """Load and register all scenes from project config."""
        scenes_config = self.project_config.get('scenes', {})
        entry_scene = scenes_config.get('entry_scene')
        scene_list = scenes_config.get('scenes', [])

        if not scene_list:
            print("[Game] Warning: No scenes defined in project config")
            return

        print(f"[Game] Loading {len(scene_list)} scene(s)...")

        # Import and instantiate each scene
        for scene_config in scene_list:
            scene_name = scene_config.get('name')
            scene_file = scene_config.get('file')
            scene_class = scene_config.get('class')

            if not all([scene_name, scene_file, scene_class]):
                print(f"[Game] Warning: Invalid scene config: {scene_config}")
                continue

            try:
                # Import scene module
                module_path = scene_file.replace('/', '.').replace('.py', '')
                module = __import__(module_path, fromlist=[scene_class])

                # Get scene class
                SceneClass = getattr(module, scene_class)

                # Instantiate and register scene
                scene_instance = SceneClass(self)
                self.scene_manager.register_scene(scene_name, scene_instance)

            except Exception as e:
                print(f"[Game] Error loading scene '{scene_name}': {e}")
                import traceback
                traceback.print_exc()

        # Load entry scene
        if entry_scene:
            print(f"[Game] Loading entry scene: {entry_scene}")
            self.scene_manager.load_scene(entry_scene)
        else:
            print("[Game] Warning: No entry scene specified")


def main():
    """CLI entry point for running a game."""
    import argparse

    parser = argparse.ArgumentParser(description='Scribe Engine V2 Game Runner')
    parser.add_argument('project_path', help='Path to the game project directory')

    args = parser.parse_args()

    # Create and run game
    game = Game(args.project_path)

    if not game.initialize():
        print("[Game] Failed to initialize game")
        sys.exit(1)

    try:
        game.run()
    except KeyboardInterrupt:
        print("\n[Game] Interrupted by user")
    except Exception as e:
        print(f"[Game] Error during game execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        game.quit()


if __name__ == '__main__':
    main()
