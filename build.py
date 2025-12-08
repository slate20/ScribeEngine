#!/usr/bin/env python3
"""
Build script for creating standalone ScribeEngine executables.

This script uses PyInstaller to create platform-specific binaries.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path


def get_platform_name():
    """Get a normalized platform name."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'


def clean_build_dirs():
    """Remove old build artifacts."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)


def build_executable():
    """Build the standalone executable using PyInstaller."""
    print("=" * 60)
    print("Building ScribeEngine Standalone Executable")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not installed")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Clean old builds
    clean_build_dirs()

    # Run PyInstaller
    print("\nRunning PyInstaller...")
    result = subprocess.run(
        ['pyinstaller', 'scribe.spec', '--clean'],
        check=True
    )

    if result.returncode != 0:
        print("ERROR: Build failed")
        sys.exit(1)

    # Get platform info
    platform_name = get_platform_name()
    exe_name = 'scribe.exe' if platform_name == 'windows' else 'scribe'

    # Check if build succeeded
    exe_path = Path('dist') / exe_name
    if not exe_path.exists():
        print(f"ERROR: Executable not found at {exe_path}")
        sys.exit(1)

    # Create release directory
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)

    # Copy executable to release with platform name
    release_name = f'scribe-{platform_name}'
    if platform_name == 'windows':
        release_name += '.exe'

    release_path = release_dir / release_name
    shutil.copy2(exe_path, release_path)

    # Get file size
    size_mb = os.path.getsize(release_path) / (1024 * 1024)

    print("\n" + "=" * 60)
    print("✓ Build Successful!")
    print("=" * 60)
    print(f"Platform: {platform_name}")
    print(f"Executable: {release_path}")
    print(f"Size: {size_mb:.1f} MB")
    print("\nTest it with:")
    print(f"  {release_path} --version")
    print(f"  {release_path} --help")
    print("=" * 60)


def test_executable():
    """Test the built executable."""
    platform_name = get_platform_name()
    exe_name = f'scribe-{platform_name}'
    if platform_name == 'windows':
        exe_name += '.exe'

    exe_path = Path('release') / exe_name

    if not exe_path.exists():
        print(f"ERROR: Executable not found at {exe_path}")
        sys.exit(1)

    print("\nTesting executable...")
    result = subprocess.run([str(exe_path), '--version'], capture_output=True, text=True)
    print(result.stdout)

    result = subprocess.run([str(exe_path), '--help'], capture_output=True, text=True)
    print(result.stdout)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build ScribeEngine executable')
    parser.add_argument('--test', action='store_true', help='Test the executable after building')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')

    args = parser.parse_args()

    if args.clean_only:
        clean_build_dirs()
        print("✓ Cleaned build directories")
    else:
        build_executable()

        if args.test:
            test_executable()
