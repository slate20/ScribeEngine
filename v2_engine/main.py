#!/usr/bin/env python3
"""
V2 Engine Game Launcher
"""
import sys
import os

# Add engine to path
engine_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(engine_root))

from v2_engine.core.game import Game

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <project_path> [scene_name]")
        sys.exit(1)

    project_path = sys.argv[1]
    scene_override = sys.argv[2] if len(sys.argv) > 2 else None

    game = Game(project_path, editor_mode=False)

    # Initialize engine systems
    if not game.initialize():
        print("[Game] Failed to initialize game engine")
        sys.exit(1)

    # Load scene (use override from command line if provided, otherwise entry scene)
    if scene_override:
        print(f"[Game] Loading scene from command line: {scene_override}")
        game.scene_manager.load_scene(scene_override)
    else:
        entry_scene = game.project_config.get('scenes', {}).get('entry_scene')
        if entry_scene:
            game.scene_manager.load_scene(entry_scene)

    # Run game loop
    game.run()
