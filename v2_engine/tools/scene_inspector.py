"""
Scene Inspector - Extract sprite data from running scenes for IDE integration

Runs the V2 engine in headless mode and provides an API to inspect scene contents.
"""

import os
import sys
import json
from flask import Flask, jsonify, request
from threading import Thread

# Initialize headless pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from v2_engine.core.game import Game


class SceneInspector:
    """
    Runs a game in headless mode and provides inspection API.
    """

    def __init__(self, project_path: str, port: int = 5555):
        self.project_path = project_path
        self.port = port
        self.game = None
        self.app = Flask(__name__)
        self.current_scene_name = None

        # Setup Flask routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask API routes."""

        @self.app.route('/health')
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'running', 'scene': self.current_scene_name})

        @self.app.route('/scene/<scene_name>/load', methods=['POST'])
        def load_scene(scene_name):
            """Load a scene and reload its Python module to pick up code changes."""
            try:
                if self.game:
                    # CRITICAL: Reload modules to pick up file changes
                    import sys
                    import importlib

                    # Reload game_objects module first (dependency)
                    for module_name in list(sys.modules.keys()):
                        if 'scripts.game_objects' in module_name:
                            print(f"[SceneInspector] Reloading module: {module_name}")
                            importlib.reload(sys.modules[module_name])

                    # Find and reload the scene module
                    scene_module_name = None
                    for module_name in list(sys.modules.keys()):
                        if 'scenes.' in module_name and scene_name in module_name:
                            scene_module_name = module_name
                            break

                    if scene_module_name and scene_module_name in sys.modules:
                        print(f"[SceneInspector] Reloading module: {scene_module_name}")
                        importlib.reload(sys.modules[scene_module_name])

                        # Re-register the scene with the scene manager
                        # Need to re-instantiate the scene class
                        scene_module = sys.modules[scene_module_name]

                        # Find the scene class in the module
                        for attr_name in dir(scene_module):
                            attr = getattr(scene_module, attr_name)
                            if (isinstance(attr, type) and
                                hasattr(attr, '__mro__') and
                                any('Scene' in base.__name__ for base in attr.__mro__) and
                                attr.__name__ != 'Scene'):
                                # Found the scene class, re-register it
                                scene_class = attr
                                self.game.scene_manager.scenes[scene_name] = scene_class(self.game)
                                print(f"[SceneInspector] Re-registered scene: {scene_name}")
                                break

                    # Queue the scene load
                    self.game.scene_manager.load_scene(scene_name)

                    # Trigger the actual scene transition by calling update
                    self.game.scene_manager.update(0.016)

                    self.current_scene_name = scene_name
                    return jsonify({'success': True, 'scene': scene_name})
                else:
                    return jsonify({'error': 'Game not initialized'}), 500
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500

        @self.app.route('/scene/inspect', methods=['GET'])
        def inspect_scene():
            """Get current scene sprite data."""
            if not self.game:
                return jsonify({'error': 'Game not initialized'}), 400

            if not self.game.scene_manager:
                return jsonify({'error': 'Scene manager not initialized'}), 400

            if not self.game.scene_manager.current_scene:
                return jsonify({'error': f'No scene loaded (current_scene_name={self.current_scene_name})'}), 400

            # current_scene is the scene NAME (string), get actual scene object from scenes dict
            scene_name = self.game.scene_manager.current_scene
            scene = self.game.scene_manager.scenes[scene_name]
            sprites = self._extract_sprites(scene)

            return jsonify({
                'scene_name': self.current_scene_name,
                'sprites': sprites
            })

        @self.app.route('/shutdown', methods=['POST'])
        def shutdown():
            """Shutdown the inspector."""
            func = request.environ.get('werkzeug.server.shutdown')
            if func:
                func()
            return jsonify({'success': True})

    def _extract_sprites(self, scene) -> list:
        """
        Extract sprite data from a scene.

        Args:
            scene: Scene instance

        Returns:
            List of sprite dictionaries with position, size, type info
        """
        sprites = []

        # Debug logging to file
        with open('/tmp/inspector_debug.log', 'a') as f:
            f.write(f"\n=== Extracting sprites from {type(scene).__name__} ===\n")
            f.write(f"Scene attributes: {[a for a in dir(scene) if not a.startswith('_')]}\n")

        # Get all sprite groups
        sprite_groups = []
        if hasattr(scene, 'all_sprites'):
            with open('/tmp/inspector_debug.log', 'a') as f:
                f.write(f"Found all_sprites: {scene.all_sprites}\n")
                f.write(f"all_sprites has 'sprites' attr: {hasattr(scene.all_sprites, 'sprites')}\n")
                if hasattr(scene.all_sprites, 'sprites'):
                    f.write(f"all_sprites.sprites type: {type(scene.all_sprites.sprites)}\n")
                    f.write(f"all_sprites.sprites length: {len(scene.all_sprites.sprites)}\n")
                    f.write(f"all_sprites.sprites content: {scene.all_sprites.sprites}\n")
            sprite_groups.append(scene.all_sprites)
        if hasattr(scene, 'solid_sprites'):
            # Check if it's not already in the list
            if not hasattr(scene, 'all_sprites') or scene.solid_sprites != scene.all_sprites:
                sprite_groups.append(scene.solid_sprites)

        # Collect unique sprites
        seen_sprites = set()
        sprite_instances = []

        for group in sprite_groups:
            if hasattr(group, 'sprites'):
                # sprites is a list, not a method
                sprite_list = group.sprites if isinstance(group.sprites, list) else group.sprites()
                for sprite in sprite_list:
                    if id(sprite) not in seen_sprites:
                        seen_sprites.add(id(sprite))
                        sprite_instances.append(sprite)

        # If no groups found, try to find sprites directly on scene
        if not sprite_instances:
            for attr_name in dir(scene):
                attr = getattr(scene, attr_name)
                # Check if it's a sprite-like object
                if hasattr(attr, 'position') and hasattr(attr, 'image'):
                    if id(attr) not in seen_sprites:
                        seen_sprites.add(id(attr))
                        sprite_instances.append(attr)

        # Extract data from sprites
        for sprite in sprite_instances:
            sprite_data = self._extract_sprite_data(sprite, scene)
            if sprite_data:
                sprites.append(sprite_data)

        return sprites

    def _extract_sprite_data(self, sprite, scene) -> dict:
        """
        Extract data from a single sprite.

        Args:
            sprite: Sprite instance
            scene: Parent scene

        Returns:
            Dictionary with sprite data
        """
        # Find the variable name for this sprite in the scene
        sprite_name = None
        for attr_name in dir(scene):
            if attr_name.startswith('_'):
                continue
            attr = getattr(scene, attr_name)
            if attr is sprite:
                sprite_name = f'self.{attr_name}'
                break

        if not sprite_name:
            sprite_name = f'sprite_{id(sprite)}'

        # Get sprite type
        sprite_type = type(sprite).__name__

        # Get position
        x, y = 0, 0
        if hasattr(sprite, 'position'):
            x = sprite.position.x
            y = sprite.position.y
        elif hasattr(sprite, 'rect'):
            x = sprite.rect.x
            y = sprite.rect.y

        # Get size
        width, height = 32, 32  # Default
        if hasattr(sprite, 'image'):
            width = sprite.image.get_width()
            height = sprite.image.get_height()
        elif hasattr(sprite, 'rect'):
            width = sprite.rect.width
            height = sprite.rect.height

        return {
            'name': sprite_name,
            'type': sprite_type,
            'properties': {
                'x': round(x, 2),
                'y': round(y, 2),
                'width': width,
                'height': height
            }
        }

    def start(self):
        """Start the inspector."""
        print(f"[SceneInspector] Initializing game from: {self.project_path}")

        # Initialize the game in headless mode
        self.game = Game(self.project_path)
        if not self.game.initialize():
            print(f"[SceneInspector] Failed to initialize game")
            return

        print(f"[SceneInspector] Game initialized successfully")
        print(f"[SceneInspector] Starting Flask API on port {self.port}")

        # Run Flask (blocking)
        self.app.run(
            host='127.0.0.1',
            port=self.port,
            debug=False,
            use_reloader=False,
            threaded=True
        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Scene Inspector for Scribe Engine V2')
    parser.add_argument('project_path', help='Path to the game project')
    parser.add_argument('--port', type=int, default=5555, help='API port (default: 5555)')

    args = parser.parse_args()

    inspector = SceneInspector(args.project_path, args.port)
    inspector.start()


if __name__ == '__main__':
    main()
