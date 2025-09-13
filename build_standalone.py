#!/usr/bin/env python3
"""
Standalone game building module for Scribe Engine.
This module provides the same API as build_nuitka.py but uses the standalone
ScribeBuilder executable to avoid nested bundling issues completely.
"""

import os
import sys
import subprocess
import threading
import tempfile
import shutil
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

def find_standalone_builder() -> str:
    """Find the standalone ScribeBuilder executable."""

    # Determine platform-specific executable name
    if sys.platform.startswith('linux'):
        builder_name = 'ScribeBuilder-linux'
    elif sys.platform.startswith('win'):
        builder_name = 'ScribeBuilder-windows.exe'
    elif sys.platform.startswith('darwin'):
        builder_name = 'ScribeBuilder-macos'
    else:
        builder_name = 'ScribeBuilder-unknown'

    # Look in several possible locations
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Check if bundled with engine (for standalone engine distributions)
    if getattr(sys, 'frozen', False):
        # Running from bundled executable - look in bundled data
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            bundled_path = os.path.join(sys._MEIPASS, 'tools', builder_name)
            if os.path.exists(bundled_path):
                return bundled_path

        # Could be Nuitka bundle - check relative to executable
        exe_dir = os.path.dirname(sys.executable)
        relative_path = os.path.join(exe_dir, 'tools', builder_name)
        if os.path.exists(relative_path):
            return relative_path

    # 2. Development mode - check local dist_tools directory
    local_path = os.path.join(script_dir, 'dist_tools', builder_name)
    if os.path.exists(local_path):
        return local_path

    # 3. Check system PATH
    try:
        result = subprocess.run(['which', builder_name], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass

    raise BuildError(f"Standalone builder not found: {builder_name}")

def build_game_with_standalone(project_name: str, project_root_dir: str, output_dir: Optional[str] = None) -> bool:
    """
    Build a game using the standalone ScribeBuilder executable.

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

    set_build_status(project_name, 'building', 'Locating standalone builder...')

    try:
        # Find the standalone builder executable
        builder_path = find_standalone_builder()

        set_build_status(project_name, 'building', 'Starting build process...')

        # Set up output directory
        if output_dir is None:
            output_dir = os.path.join(project_path, 'dist')

        # Build command arguments
        build_cmd = [builder_path, project_path]
        if output_dir:
            build_cmd.extend(['--output', output_dir])

        set_build_status(project_name, 'building', 'Running standalone builder...')

        # Run the standalone builder
        result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=project_root_dir)

        if result.returncode == 0:
            # Find the generated executable
            executable_path = find_built_executable(project_path, output_dir)

            set_build_status(project_name, 'completed', 'Build completed successfully', executable_path)
            return True
        else:
            error_msg = result.stderr or result.stdout or "Unknown build error"
            set_build_status(project_name, 'failed', f'Build failed: {error_msg}')
            raise BuildError(f"Standalone build failed: {error_msg}")

    except Exception as e:
        set_build_status(project_name, 'failed', f'Build failed: {str(e)}')
        raise BuildError(f"Build failed: {e}")

def find_built_executable(project_path: str, output_dir: str) -> Optional[str]:
    """Find the built executable in the output directory."""
    try:
        # Load project configuration to get title
        import json
        project_json_path = os.path.join(project_path, 'project.json')
        with open(project_json_path, 'r') as f:
            project_config = json.load(f)

        # Sanitize project name (same logic as in build_tool_standalone.py)
        raw_title = project_config.get('title', 'Game')
        safe_name = (raw_title
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

        # Check for executable
        executable_name = safe_name
        if sys.platform.startswith('win'):
            executable_name += '.exe'

        executable_path = os.path.join(output_dir, executable_name)
        if os.path.exists(executable_path):
            return executable_path

    except Exception:
        pass

    # Fallback: look for any executable in output dir
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                return file_path

    return None

def build_game_async(project_name: str, project_root_dir: str, output_dir: Optional[str] = None):
    """Build a game asynchronously in a separate thread."""

    def build_thread():
        try:
            build_game_with_standalone(project_name, project_root_dir, output_dir)
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

    parser = argparse.ArgumentParser(description='Build Scribe Engine games with standalone builder')
    parser.add_argument('project_name', help='Name of the project to build')
    parser.add_argument('--project-root', '-r', help='Root directory containing projects')
    parser.add_argument('--output', '-o', help='Output directory for executable')

    args = parser.parse_args()

    project_root = args.project_root or os.getcwd()

    try:
        result = build_game_with_standalone(args.project_name, project_root, args.output)
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