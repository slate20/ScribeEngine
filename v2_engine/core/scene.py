"""
Scene management for Scribe Engine V2.

Provides Scene base class and SceneManager for organizing game states.
"""

import pygame


class Scene:
    """
    Base class for all game scenes.

    Scenes represent distinct game states (menu, gameplay, etc.)
    and manage their own sprites, UI, and logic.
    """

    def __init__(self, game: 'Game'):
        """
        Initialize the scene.

        Args:
            game: Reference to the main Game instance
        """
        self.game = game
        self.sprite_groups = {}  # Named sprite groups
        self.ui_elements = []
        self.camera = None

    def on_enter(self):
        """Called when scene becomes active."""
        pass

    def on_exit(self):
        """Called when scene becomes inactive."""
        pass

    def handle_event(self, event):
        """
        Handle pygame events.

        Args:
            event: pygame event object
        """
        pass

    def update(self, dt: float):
        """
        Update scene logic.

        Args:
            dt: Delta time in seconds
        """
        pass

    def render(self, screen):
        """
        Render scene to screen.

        Args:
            screen: pygame Surface to render to
        """
        pass


class SceneManager:
    """
    Manages scene loading, switching, and lifecycle.
    """

    def __init__(self, game: 'Game'):
        """
        Initialize scene manager.

        Args:
            game: Reference to main Game instance
        """
        self.game = game
        self.scenes = {}  # scene_name -> Scene instance
        self.current_scene = None
        self.next_scene = None

    def register_scene(self, name: str, scene: Scene):
        """
        Register a scene for later use.

        Args:
            name: Unique scene identifier
            scene: Scene instance
        """
        self.scenes[name] = scene
        print(f"[SceneManager] Registered scene: {name}")

    def load_scene(self, name: str):
        """
        Switch to a different scene.

        Args:
            name: Name of scene to load
        """
        if name not in self.scenes:
            print(f"[SceneManager] Error: Scene '{name}' not found")
            return

        self.next_scene = name
        print(f"[SceneManager] Queued scene transition: {self.current_scene} -> {name}")

    def update(self, dt: float):
        """
        Update current scene.

        Args:
            dt: Delta time in seconds
        """
        # Perform pending scene transition
        if self.next_scene is not None:
            self._perform_scene_transition()

        # Update current scene
        if self.current_scene:
            scene = self.scenes[self.current_scene]
            scene.update(dt)

    def render(self, screen):
        """
        Render current scene.

        Args:
            screen: pygame Surface to render to
        """
        if self.current_scene:
            scene = self.scenes[self.current_scene]
            scene.render(screen)

    def handle_event(self, event):
        """
        Pass event to current scene.

        Args:
            event: pygame event object
        """
        if self.current_scene:
            scene = self.scenes[self.current_scene]
            scene.handle_event(event)

    def _perform_scene_transition(self):
        """Execute pending scene transition."""
        # Exit current scene
        if self.current_scene:
            old_scene = self.scenes[self.current_scene]
            old_scene.on_exit()
            print(f"[SceneManager] Exited scene: {self.current_scene}")

        # Enter new scene
        self.current_scene = self.next_scene
        self.next_scene = None

        new_scene = self.scenes[self.current_scene]
        new_scene.on_enter()
        print(f"[SceneManager] Entered scene: {self.current_scene}")
