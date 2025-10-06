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

        # Input reference (convenient access to game.input_handler)
        self.input = game.input_handler if game else None

        # Background settings
        self.background_color = (40, 40, 50)  # Default dark gray
        self.background_image = None  # Path to background image
        self.background_surface = None  # Loaded background surface

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

    def change_scene(self, name: str):
        """
        Alias for load_scene() - switch to a different scene.

        Args:
            name: Name of scene to load
        """
        self.load_scene(name)

    def reload_current_scene(self):
        """
        Reload the current scene (useful after loading a save).
        This re-triggers on_enter to apply loaded state.
        """
        if self.current_scene:
            print(f"[SceneManager] Reloading current scene: {self.current_scene}")
            scene = self.scenes[self.current_scene]
            # Just call on_enter again to reapply state
            scene.on_enter()

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
        print(f"[SceneManager] _perform_scene_transition() called - transitioning from {self.current_scene} to {self.next_scene}")

        from v2_engine.core.game_state import get_game_state
        game_state = get_game_state()

        # Detach persistent entities from current scene (don't destroy them)
        # BUT: Keep entities in their home scene
        persistent_entities_detached = []
        if self.current_scene:
            old_scene = self.scenes[self.current_scene]

            # Find and remove persistent entities from scene groups (except in their home scene)
            for entity_id, entity in game_state.persistent_entities.items():
                # Check if this is the entity's home scene
                home_scene = getattr(entity, '_home_scene', None)
                if home_scene == self.current_scene:
                    # This is the home scene - keep the entity here
                    print(f"[SceneManager] Keeping persistent entity in home scene: {entity_id}")
                    continue

                # Not the home scene - detach it
                for group in old_scene.sprite_groups.values():
                    if entity in group.sprites:
                        group.sprites.remove(entity)
                        persistent_entities_detached.append((entity_id, entity))
                        print(f"[SceneManager] Detached persistent entity: {entity_id}")

            # Exit current scene
            old_scene.on_exit()
            print(f"[SceneManager] Exited scene: {self.current_scene}")

        # Enter new scene
        self.current_scene = self.next_scene
        self.next_scene = None

        new_scene = self.scenes[self.current_scene]
        print(f"[SceneManager] Calling on_enter() for scene: {self.current_scene} (instance id: {id(new_scene)})")
        new_scene.on_enter()

        # Register any persistent entities from the new scene that aren't already registered
        # If a persistent entity already exists in GameState, remove the scene's duplicate
        for group in new_scene.sprite_groups.values():
            for sprite in list(group.sprites):
                if getattr(sprite, 'is_persistent', False) and getattr(sprite, 'entity_id', None):
                    if sprite.entity_id in game_state.persistent_entities:
                        # Entity already registered - check if this is its home scene
                        # Get home_scene from the existing entity in GameState (it might not be on the fresh sprite)
                        existing_entity = game_state.persistent_entities[sprite.entity_id]
                        home_scene = getattr(existing_entity, '_home_scene', None)
                        if home_scene == self.current_scene:
                            # This IS the home scene - update GameState with fresh instance from file
                            # (Important for editor mode when scenes are reloaded)
                            game_state.persistent_entities[sprite.entity_id] = sprite
                            sprite._home_scene = home_scene  # Preserve home scene marker
                            print(f"[SceneManager] Updated persistent entity in home scene: {sprite.entity_id}")
                        else:
                            # Not the home scene - remove duplicate (spawn point will re-add if needed)
                            group.sprites.remove(sprite)
                            print(f"[SceneManager] Removed duplicate persistent entity from scene: {sprite.entity_id}")
                    else:
                        # First time seeing this entity - register it with this scene as home
                        game_state.register_persistent(sprite, sprite.entity_id, home_scene=self.current_scene)
                        print(f"[SceneManager] Registered persistent entity from scene: {sprite.entity_id} (home: {self.current_scene})")

        # Trigger spawn points to position persistent entities
        from v2_engine.components.spawn_point import SpawnPoint
        for group in new_scene.sprite_groups.values():
            for sprite in list(group.sprites):  # Use list() to avoid modification during iteration
                spawn_point = sprite.get_component(SpawnPoint)
                if spawn_point:
                    spawn_point.on_scene_enter()

        print(f"[SceneManager] Entered scene: {self.current_scene} - sprite count: {sum(len(g.sprites) for g in new_scene.sprite_groups.values())}")
