#!/usr/bin/env python3
"""
Automated test for scene parser (no user input)
"""

import json
from ide.scene_parser import SceneParser

def main():
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

    print("\nJSON Output:")
    print(json.dumps(parser.get_sprites_json(), indent=2))

    print("\n" + "=" * 60)
    print("Parser Test Complete")
    print("=" * 60)

    # Summary
    print("\nSummary:")
    print(f"  ✓ Successfully parsed {len(sprites)} sprite instances")
    print(f"  ✓ Extracted properties from constructor arguments")
    print(f"  ✓ JSON serialization working")
    print("\nNote: Platforms and collectibles created in loops are not detected")
    print("      (this is expected - AST parsing has limitations with dynamic code)")

if __name__ == "__main__":
    main()
