#!/usr/bin/env python3
"""
Test script for scene_parser and scene_writer
"""

import sys
import json
from ide.scene_parser import SceneParser, parse_scene_file
from ide.scene_writer import SceneWriter

def test_parser():
    """Test the scene parser with platformer demo."""
    print("=" * 60)
    print("Testing SceneParser with level_01.py")
    print("=" * 60)

    scene_path = "v2_engine/templates/platformer/scenes/level_01.py"

    # Parse the scene
    parser = SceneParser(scene_path)
    sprites = parser.parse()

    print(f"\nFound {len(sprites)} sprites:\n")

    for sprite in sprites:
        print(f"  {sprite.name} ({sprite.sprite_type})")
        print(f"    Line: {sprite.line_number}")
        print(f"    Args: {sprite.constructor_args}")
        print(f"    Properties: {sprite.properties}")
        print(f"    Has metadata: {sprite.has_metadata}")
        print()

    # Get JSON representation
    print("\nJSON Output:")
    print(json.dumps(parser.get_sprites_json(), indent=2))

    return sprites

def test_writer_add_markers():
    """Test adding metadata markers to sprites."""
    print("\n" + "=" * 60)
    print("Testing SceneWriter - Adding Metadata Markers")
    print("=" * 60)

    scene_path = "v2_engine/templates/platformer/scenes/level_01.py"

    writer = SceneWriter(scene_path)

    # Add markers to all sprites
    count = writer.add_all_metadata_markers()

    print(f"\nAdded metadata markers to {count} sprites")

    # Re-parse to verify
    parser = SceneParser(scene_path)
    sprites = parser.parse()

    print("\nVerifying markers were added:")
    for sprite in sprites:
        status = "✓" if sprite.has_metadata else "✗"
        print(f"  {status} {sprite.name} - has_metadata: {sprite.has_metadata}")

def test_writer_update_properties():
    """Test updating sprite properties."""
    print("\n" + "=" * 60)
    print("Testing SceneWriter - Updating Properties")
    print("=" * 60)

    scene_path = "v2_engine/templates/platformer/scenes/level_01.py"

    writer = SceneWriter(scene_path)

    # Update player position
    print("\nUpdating self.player position to (200, 400)")
    success = writer.update_sprite_properties("self.player", {
        'x': 200,
        'y': 400
    })

    if success:
        print("✓ Update successful")

        # Re-parse to verify
        parser = SceneParser(scene_path)
        sprites = parser.parse()
        player = parser.get_sprite_by_name("self.player")

        if player:
            print(f"  New properties: {player.properties}")
    else:
        print("✗ Update failed")

if __name__ == "__main__":
    # Test parser
    sprites = test_parser()

    # Ask user if they want to test writer
    print("\n" + "=" * 60)
    response = input("Test writer? This will modify level_01.py (y/n): ")

    if response.lower() == 'y':
        # First add metadata markers
        test_writer_add_markers()

        # Then test property updates
        test_writer_update_properties()

        print("\n✓ Testing complete!")
        print("  Check v2_engine/templates/platformer/scenes/level_01.py to see changes")
    else:
        print("\nSkipping writer tests (no file modifications)")
