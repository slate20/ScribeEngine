#!/usr/bin/env python3
"""
PyInstaller-based game building tool for Scribe Engine.
This works as a separate tool that can be called by the Nuitka-built engine,
solving the nested bundling issue while keeping the benefits of both tools.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import argparse
from datetime import datetime
from typing import Optional

def build_game_with_pyinstaller(project_name: str, project_root_dir: str, engine_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Build a game project using PyInstaller.

    Args:
        project_name: Name of the game project
        project_root_dir: Root directory containing game projects
        engine_path: Path to the engine directory (for assets)
        output_dir: Optional output directory (defaults to project/dist/)

    Returns:
        bool: True if build successful, False otherwise
    """

    project_path = os.path.join(project_root_dir, project_name)

    # Validate project structure
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")

    project_json_path = os.path.join(project_path, 'project.json')
    if not os.path.exists(project_json_path):
        raise Exception(f"No project.json found in {project_path}")

    # Load project configuration
    try:
        with open(project_json_path, 'r') as f:
            project_config = json.load(f)
    except Exception as e:
        raise Exception(f"Error reading project configuration: {e}")

    # Sanitize project name for executable
    raw_title = project_config.get('title', project_name)
    safe_name = sanitize_filename(raw_title)

    print(f"Building {raw_title} with PyInstaller...")

    # Set up output directory
    if output_dir is None:
        output_dir = os.path.join(project_path, 'dist')
    os.makedirs(output_dir, exist_ok=True)

    # Create temporary build directory
    with tempfile.TemporaryDirectory(prefix=f'scribe_build_{project_name}_') as temp_dir:

        print("Setting up build environment...")

        # Copy engine components to build directory
        engine_dirs = ['engine', 'templates', 'static']
        for dirname in engine_dirs:
            src_dir = os.path.join(engine_path, dirname)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(temp_dir, dirname)
                shutil.copytree(src_dir, dst_dir)

        # Copy game server file
        game_server_files = ['game_server.py', 'game_server_wrapper.py']
        for server_file in game_server_files:
            src_path = os.path.join(engine_path, server_file)
            if os.path.exists(src_path):
                dst_path = os.path.join(temp_dir, server_file)
                shutil.copy2(src_path, dst_path)

        print("Copying game project...")

        # Copy game project files
        game_dst = os.path.join(temp_dir, 'game_project')
        copy_project_files(project_path, game_dst)

        print("Creating game launcher...")

        # Create game launcher script
        launcher_path = create_game_launcher(temp_dir, project_config)

        print("Running PyInstaller...")

        # Build executable name
        executable_name = safe_name
        if sys.platform.startswith('win'):
            executable_name += '.exe'

        # PyInstaller command arguments
        pyinstaller_args = [
            sys.executable, '-m', 'PyInstaller',
            launcher_path,
            '--onefile',
            '--name', safe_name,
            '--distpath', output_dir,
            '--workpath', os.path.join(temp_dir, 'work'),
            '--specpath', os.path.join(temp_dir, 'spec'),
            '--clean',
            '--noconfirm',

            # Add data directories
            '--add-data', f'{os.path.join(temp_dir, "engine")}{os.pathsep}engine',
            '--add-data', f'{os.path.join(temp_dir, "templates")}{os.pathsep}templates',
            '--add-data', f'{os.path.join(temp_dir, "static")}{os.pathsep}static',
            '--add-data', f'{game_dst}{os.pathsep}game_project',

            # Hidden imports
            '--hidden-import=flask',
            '--hidden-import=jinja2',
            '--hidden-import=werkzeug',
        ]

        # Add game server files
        for server_file in game_server_files:
            server_path = os.path.join(temp_dir, server_file)
            if os.path.exists(server_path):
                pyinstaller_args.extend(['--add-data', f'{server_path}{os.pathsep}.'])

        # Add console/GUI options
        if not sys.platform.startswith('win'):
            pass  # Keep console on Linux/Mac for debugging
        else:
            pyinstaller_args.append('--noconsole')  # Hide console on Windows

        # Run PyInstaller
        result = subprocess.run(pyinstaller_args, capture_output=True, text=True, cwd=temp_dir)

        if result.returncode == 0:
            final_exe = os.path.join(output_dir, executable_name)
            if os.path.exists(final_exe):
                size_mb = os.path.getsize(final_exe) // (1024 * 1024)
                print(f"✓ Build completed successfully!")
                print(f"  Executable: {final_exe}")
                print(f"  Size: {size_mb} MB")
                return True
            else:
                print(f"✗ Expected executable not found: {final_exe}")
                return False
        else:
            print("✗ PyInstaller build failed!")
            print(f"STDERR: {result.stderr}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            return False

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for use as executable name."""
    return (filename
            .replace(' ', '_')
            .replace("'", '')
            .replace('"', '')
            .replace('&', 'and')
            .replace('/', '_')
            .replace('\\', '_')
            .replace(':', '_')
            .replace('*', '_')
            .replace('?', '_')
            .replace('<', '_')
            .replace('>', '_')
            .replace('|', '_'))

def copy_project_files(src_path: str, dst_path: str):
    """Copy project files excluding build artifacts."""
    os.makedirs(dst_path, exist_ok=True)

    exclude_patterns = {
        'temp_build', 'build', 'dist', 'spec', '__pycache__',
        '.git', '.vscode', '.idea', 'venv', 'env'
    }

    for item in os.listdir(src_path):
        if item not in exclude_patterns:
            src_item = os.path.join(src_path, item)
            dst_item = os.path.join(dst_path, item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item)
            else:
                shutil.copy2(src_item, dst_item)

def create_game_launcher(build_dir: str, project_config: dict) -> str:
    """Create the game launcher script."""

    game_title = project_config.get('title', 'Game')

    launcher_content = f'''#!/usr/bin/env python3
"""
Game launcher for {game_title}
Generated by Scribe Engine with PyInstaller
"""

import webview
import threading
import time
import os
import sys

# Get the directory where this executable is located
if getattr(sys, 'frozen', False):
    # Running from PyInstaller bundle
    base_dir = sys._MEIPASS
    executable_dir = os.path.dirname(sys.executable)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
    executable_dir = base_dir

# Add the base directory to Python path
sys.path.insert(0, base_dir)

def start_game_server():
    """Start the game server."""
    try:
        from game_server import app as game_app, set_game_project_path
        game_project_path = os.path.join(base_dir, 'game_project')
        set_game_project_path(game_project_path)
        game_app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Error starting game server: {{e}}")
        sys.exit(1)

def main():
    """Main entry point for the game."""
    print("Starting {game_title}...")

    # Start the game server in a separate thread
    server_thread = threading.Thread(target=start_game_server, daemon=True)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(2)

    # Create and start the webview window
    try:
        webview.create_window(
            "{game_title}",
            'http://127.0.0.1:5001',
            width=1024,
            height=768,
            resizable=True
        )
        webview.start()
    except Exception as e:
        print(f"Error starting game window: {{e}}")
        print("You can play the game by opening http://127.0.0.1:5001 in your web browser")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''

    launcher_path = os.path.join(build_dir, 'game_launcher.py')
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)

    return launcher_path

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Build Scribe Engine games with PyInstaller')
    parser.add_argument('project_name', help='Name of the project to build')
    parser.add_argument('--project-root', '-r', help='Root directory containing projects', required=True)
    parser.add_argument('--engine-path', '-e', help='Path to engine directory', required=True)
    parser.add_argument('--output', '-o', help='Output directory for executable')

    args = parser.parse_args()

    try:
        success = build_game_with_pyinstaller(
            args.project_name,
            args.project_root,
            args.engine_path,
            args.output
        )
        if success:
            print("\n🎉 Build completed successfully!")
        else:
            print("\n❌ Build failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()