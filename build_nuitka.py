#!/usr/bin/env python3
"""
Integrated Nuitka-based game building module for Scribe Engine.
This module can be called from within the engine executable to build games,
solving the nested bundling issues that plagued the PyInstaller approach.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from typing import Optional, Dict, Any

# Global build state tracking
_build_status = {}
_build_lock = threading.Lock()

class BuildError(Exception):
    """Exception raised when build process fails."""
    pass

def get_build_status(project_name: str) -> Dict[str, Any]:
    """Get the current build status for a project."""
    with _build_lock:
        return _build_status.get(project_name, {
            'status': 'not_started',
            'progress': 'No build in progress',
            'start_time': None,
            'executable_path': None
        })

def set_build_status(project_name: str, status: str, progress: str, executable_path: str = None):
    """Update the build status for a project."""
    with _build_lock:
        if project_name not in _build_status:
            _build_status[project_name] = {}

        _build_status[project_name].update({
            'status': status,
            'progress': progress,
            'last_update': datetime.now().isoformat()
        })

        if status == 'building' and 'start_time' not in _build_status[project_name]:
            _build_status[project_name]['start_time'] = datetime.now().isoformat()

        if executable_path:
            _build_status[project_name]['executable_path'] = executable_path

def build_game_with_nuitka(project_name: str, project_root_dir: str, output_dir: Optional[str] = None) -> bool:
    """
    Build a game project using Nuitka. This function can be called from within
    the engine executable without nested bundling issues.

    Args:
        project_name: Name of the game project
        project_root_dir: Root directory containing game projects
        output_dir: Optional output directory (defaults to project/dist/)

    Returns:
        bool: True if build successful, False otherwise
    """

    project_path = os.path.join(project_root_dir, project_name)

    # Validate project structure
    if not os.path.exists(project_path):
        raise BuildError(f"Project path does not exist: {project_path}")

    project_json_path = os.path.join(project_path, 'project.json')
    if not os.path.exists(project_json_path):
        raise BuildError(f"No project.json found in {project_path}")

    # Load project configuration
    try:
        with open(project_json_path, 'r') as f:
            project_config = json.load(f)
    except Exception as e:
        raise BuildError(f"Error reading project configuration: {e}")

    # Sanitize project name for executable
    raw_title = project_config.get('title', project_name)
    safe_name = sanitize_filename(raw_title)

    set_build_status(project_name, 'building', f'Building {raw_title}...')

    try:
        # Set up output directory
        if output_dir is None:
            output_dir = os.path.join(project_path, 'dist')

        os.makedirs(output_dir, exist_ok=True)

        set_build_status(project_name, 'building', 'Setting up build environment...')

        # Create temporary build directory
        with tempfile.TemporaryDirectory(prefix=f'scribe_build_{project_name}_') as temp_dir:

            # Determine engine base directory
            # When running from Nuitka executable, assets are embedded and accessible
            engine_base = os.path.dirname(__file__)

            set_build_status(project_name, 'building', 'Copying engine files...')

            # Copy engine components to build directory
            engine_dirs = ['engine', 'templates', 'static']
            for dirname in engine_dirs:
                src_dir = os.path.join(engine_base, dirname)
                if os.path.exists(src_dir):
                    dst_dir = os.path.join(temp_dir, dirname)
                    shutil.copytree(src_dir, dst_dir)

            # Copy game server file
            game_server_src = os.path.join(engine_base, 'game_server.py')
            if os.path.exists(game_server_src):
                shutil.copy2(game_server_src, temp_dir)
            else:
                # Create a minimal game server if not found
                create_minimal_game_server(temp_dir)

            set_build_status(project_name, 'building', 'Copying game project...')

            # Copy game project files
            game_dst = os.path.join(temp_dir, 'game_project')
            copy_project_files(project_path, game_dst)

            set_build_status(project_name, 'building', 'Creating game launcher...')

            # Create game launcher script
            launcher_path = create_game_launcher(temp_dir, project_config)

            set_build_status(project_name, 'building', 'Compiling with Nuitka...')

            # Build with Nuitka
            executable_path = run_nuitka_build(
                launcher_path,
                temp_dir,
                output_dir,
                safe_name,
                project_config
            )

            set_build_status(project_name, 'completed', f'Build completed: {safe_name}', executable_path)
            return True

    except Exception as e:
        set_build_status(project_name, 'failed', f'Build failed: {str(e)}')
        raise BuildError(f"Build failed: {e}")

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

def create_game_launcher(build_dir: str, project_config: Dict[str, Any]) -> str:
    """Create the game launcher script."""

    game_title = project_config.get('title', 'Game')

    launcher_content = f'''#!/usr/bin/env python3
"""
Game launcher for {game_title}
Generated by Scribe Engine with Nuitka
"""

import webview
import threading
import time
import os
import sys

# Get the directory where this executable is located
if getattr(sys, 'frozen', False):
    # Running from Nuitka executable
    base_dir = os.path.dirname(sys.executable)
    # For Nuitka onefile, data is embedded and accessible via normal paths
    script_dir = os.path.dirname(__file__)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = base_dir

# Add the base directory to Python path
sys.path.insert(0, script_dir)

def start_game_server():
    """Start the game server."""
    try:
        from game_server import app as game_app, set_game_project_path
        game_project_path = os.path.join(script_dir, 'game_project')
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

def create_minimal_game_server(build_dir: str):
    """Create a minimal game server if the original is not found."""

    game_server_content = '''
from flask import Flask
import os

app = Flask(__name__)
_game_project_path = None

def set_game_project_path(path):
    global _game_project_path
    _game_project_path = path

@app.route('/')
def index():
    return "<h1>Game Server Running</h1><p>Minimal server created by Scribe Engine build process.</p>"

if __name__ == '__main__':
    app.run(debug=False)
'''

    with open(os.path.join(build_dir, 'game_server.py'), 'w') as f:
        f.write(game_server_content)

def run_nuitka_build(launcher_path: str, build_dir: str, output_dir: str,
                     executable_name: str, project_config: Dict[str, Any]) -> str:
    """Run the Nuitka compilation process."""

    # Nuitka command arguments
    nuitka_args = [
        'python', '-m', 'nuitka',
        launcher_path,
        '--standalone',
        '--onefile',
        f'--output-filename={executable_name}',
        f'--output-dir={output_dir}',

        # Enable PyWebview and PyQt6 plugins
        '--plugin-enable=pywebview',
        '--plugin-enable=pyqt6',

        # Include data directories
        f'--include-data-dir={os.path.join(build_dir, "engine")}=engine',
        f'--include-data-dir={os.path.join(build_dir, "templates")}=templates',
        f'--include-data-dir={os.path.join(build_dir, "static")}=static',
        f'--include-data-dir={os.path.join(build_dir, "game_project")}=game_project',

        # Performance and compatibility options
        '--assume-yes-for-downloads',
        '--disable-console',  # No console for game executables
        '--lto=yes',
    ]

    # Add game server to bundle
    game_server_path = os.path.join(build_dir, 'game_server.py')
    if os.path.exists(game_server_path):
        nuitka_args.extend(['--include-module=game_server'])

    # Run Nuitka
    result = subprocess.run(nuitka_args, capture_output=True, text=True, cwd=build_dir)

    if result.returncode != 0:
        raise BuildError(f"Nuitka compilation failed: {result.stderr}")

    # Determine final executable path
    final_exe = os.path.join(output_dir, executable_name)
    if sys.platform.startswith('win') and not final_exe.endswith('.exe'):
        final_exe += '.exe'

    if not os.path.exists(final_exe):
        raise BuildError(f"Expected executable not found: {final_exe}")

    return final_exe

def build_game_async(project_name: str, project_root_dir: str, output_dir: Optional[str] = None):
    """Build a game asynchronously in a separate thread."""

    def build_thread():
        try:
            build_game_with_nuitka(project_name, project_root_dir, output_dir)
        except Exception as e:
            set_build_status(project_name, 'failed', f'Build failed: {str(e)}')

    # Start build in background thread
    thread = threading.Thread(target=build_thread, daemon=True)
    thread.start()

    return thread

# Convenience function for CLI usage
def main():
    """CLI entry point for standalone usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Build Scribe Engine games with Nuitka')
    parser.add_argument('project_name', help='Name of the project to build')
    parser.add_argument('--project-root', '-r', help='Root directory containing projects')
    parser.add_argument('--output', '-o', help='Output directory for executable')

    args = parser.parse_args()

    project_root = args.project_root or os.getcwd()

    try:
        result = build_game_with_nuitka(args.project_name, project_root, args.output)
        if result:
            print("✓ Build completed successfully!")
        else:
            print("✗ Build failed!")
            sys.exit(1)
    except BuildError as e:
        print(f"✗ Build error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()