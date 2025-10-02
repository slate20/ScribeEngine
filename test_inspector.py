#!/usr/bin/env python3
"""
Test the scene inspector
"""
import time
import requests
from ide.scene_inspector_manager import SceneInspectorManager

project_path = "v2_engine/templates/platformer"

print("Creating inspector...")
inspector = SceneInspectorManager(project_path, port=5558)

print("Starting inspector...")
if inspector.start(timeout=15):
    print("✓ Inspector started successfully")

    print("\nLoading level_01...")
    if inspector.load_scene("level_01"):
        print("✓ Scene loaded")

        print("\nInspecting scene...")
        data = inspector.inspect_scene()
        if data:
            print(f"✓ Got scene data")
            print(f"  Scene: {data['scene_name']}")
            print(f"  Sprites: {len(data['sprites'])}")
            for sprite in data['sprites']:
                print(f"    - {sprite['name']} ({sprite['type']}) at ({sprite['properties']['x']}, {sprite['properties']['y']})")
        else:
            print("✗ Failed to inspect scene")
    else:
        print("✗ Failed to load scene")

    print("\nStopping inspector...")
    inspector.stop()
    print("✓ Stopped")
else:
    print("✗ Failed to start inspector")
