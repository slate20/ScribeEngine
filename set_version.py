#!/usr/bin/env python3
"""
Simple version management for Scribe Engine.

Usage:
  python set_version.py 1.4.0    # Set new version
  python set_version.py          # Show current version
"""

import sys
import os
import re
from datetime import datetime

def get_current_version():
    """Get the current version from version_info.py."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        version_info_path = os.path.join(script_dir, 'version_info.py')

        with open(version_info_path, 'r') as f:
            content = f.read()

        match = re.search(r'__version__\s*=\s*["\']([^"\']*)["\']', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "unknown"

def set_version(new_version):
    """Set a new version in version_info.py."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_info_path = os.path.join(script_dir, 'version_info.py')

    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("   Expected format: major.minor.patch (e.g., 1.4.0)")
        return False

    try:
        # Read current file
        with open(version_info_path, 'r') as f:
            content = f.read()

        # Update version
        content = re.sub(r'__version__\s*=\s*["\'][^"\']*["\']',
                        f'__version__ = "{new_version}"', content)

        # Update VERSION_INFO
        parts = new_version.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        version_info_block = f'''VERSION_INFO = {{
    "major": {major},
    "minor": {minor},
    "patch": {patch},
    "version": "{new_version}",
    "build_date": None,
    "commit_hash": None,
}}'''

        content = re.sub(r'VERSION_INFO = \{[^}]+\}', version_info_block,
                        content, flags=re.DOTALL)

        # Write updated file
        with open(version_info_path, 'w') as f:
            f.write(content)

        print(f"✅ Version updated to {new_version}")
        return True

    except Exception as e:
        print(f"❌ Failed to update version: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        # Show current version
        current = get_current_version()
        print(f"Current Scribe Engine version: {current}")
    elif len(sys.argv) == 2:
        # Set new version
        new_version = sys.argv[1]
        old_version = get_current_version()

        if set_version(new_version):
            print(f"Version changed: {old_version} → {new_version}")
            print()
            print("Next steps:")
            print("1. Commit the version change")
            print("2. Run: python build_engine.py gui")
            print("3. Create GitHub release with the built executable")
    else:
        print("Usage:")
        print("  python set_version.py          # Show current version")
        print("  python set_version.py 1.4.0    # Set new version")

if __name__ == "__main__":
    main()