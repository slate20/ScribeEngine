#!/usr/bin/env python3
"""
Build script to create the Scribe Engine installer executable.
This creates the second file in our two-file distribution.
"""

import subprocess
import sys
import os

def build_installer():
    """Build the Scribe Engine installer executable."""

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Choose the right installer script based on platform
    if sys.platform.startswith('win'):
        installer_script = os.path.join(script_dir, 'installer_setup.py')
    else:
        installer_script = os.path.join(script_dir, 'installer_setup_linux.py')

    if not os.path.exists(installer_script):
        print(f"Error: {os.path.basename(installer_script)} not found")
        return False

    # Determine platform suffix
    if sys.platform.startswith('win'):
        platform_suffix = 'windows'
    elif sys.platform.startswith('linux'):
        platform_suffix = 'linux'
    elif sys.platform.startswith('darwin'):
        platform_suffix = 'macos'
    else:
        platform_suffix = 'unknown'

    executable_name = f'ScribeEngine-Setup-{platform_suffix}'
    if sys.platform.startswith('win'):
        executable_name += '.exe'

    # Create output directory
    output_dir = os.path.join(script_dir, 'dist_installer')
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Building Scribe Engine Installer")
    print("=" * 60)
    print(f"Platform: {platform_suffix}")
    print(f"Output: {executable_name}")
    print("=" * 60)

    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', executable_name.replace('.exe', ''),
        '--distpath', output_dir,
        '--workpath', os.path.join(script_dir, 'build_installer'),
        '--specpath', os.path.join(script_dir, 'spec_installer'),
        '--clean',
        '--noconfirm',
        installer_script
    ]

    # Add console/GUI options
    if sys.platform.startswith('win'):
        # Keep console for installer feedback
        pass

    print("Running PyInstaller...")
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        executable_path = os.path.join(output_dir, executable_name)
        size_mb = os.path.getsize(executable_path) // (1024 * 1024)

        print("[SUCCESS] Build completed successfully!")
        print(f"  Executable: {executable_path}")
        print(f"  Size: {size_mb} MB")
        print("=" * 60)
        print("Distribution Files:")
        print(f"  1. {executable_name} (dependency installer)")
        print(f"  2. ScribeEngine-GUI-{platform_suffix}.exe (main engine)")
        print("=" * 60)
        print("Usage:")
        print(f"  Run {executable_name} first to install dependencies")
        print(f"  Then run ScribeEngine-GUI-{platform_suffix}.exe")
        print("=" * 60)
        return True
    else:
        print("[ERROR] Build failed!")
        print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return False

if __name__ == "__main__":
    success = build_installer()
    sys.exit(0 if success else 1)