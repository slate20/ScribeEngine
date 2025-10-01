#!/usr/bin/env python3
"""
Scribe Engine V2 - Test Runner

Simple script to launch V2 games for testing during development.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from v2_engine.core.game import Game


def main():
    print("=" * 60)
    print("Scribe Engine V2 - Test Runner")
    print("=" * 60)

    # Try platformer demo first, fall back to minimal test
    demo_path = os.path.join(project_root, 'v2_engine', 'templates', 'platformer')

    if not os.path.exists(os.path.join(demo_path, '2d_project.json')):
        print(f"Platformer demo not found, using minimal test...")
        demo_path = os.path.join(project_root, 'v2_engine', 'templates', 'minimal_test')

        if not os.path.exists(os.path.join(demo_path, '2d_project.json')):
            print(f"Error: No test projects available")
            return 1

    print(f"Loading project: {demo_path}")
    print()

    # Create and run game
    game = Game(demo_path)

    if not game.initialize():
        print("Error: Failed to initialize game engine")
        return 1

    print("Starting game loop... (Press ESC or close window to quit)")
    print()
    game.run()

    print("\nGame ended. Goodbye!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
