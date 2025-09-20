import PyInstaller.__main__
import os
import sys
import subprocess
from datetime import datetime

# Get version from single source of truth
from version_info import get_version
version = get_version()

print(f"Building Scribe Engine v{version}")

def update_version_info():
    """Update version_info.py with current version and build metadata."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_info_path = os.path.join(script_dir, 'version_info.py')

    # Get git commit hash if available
    commit_hash = None
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                               capture_output=True, text=True, cwd=script_dir)
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
    except Exception:
        pass

    # Read current version_info.py
    with open(version_info_path, 'r') as f:
        content = f.read()

    # Update version using regex to handle any existing version
    import re
    content = re.sub(r'__version__\s*=\s*["\'][^"\']*["\']', f'__version__ = "{version}"', content)

    # Update VERSION_INFO
    version_parts = version.split('.')
    major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
    build_date = datetime.now().isoformat()

    version_info_block = f'''VERSION_INFO = {{
    "major": {major},
    "minor": {minor},
    "patch": {patch},
    "version": "{version}",
    "build_date": "{build_date}",
    "commit_hash": {f'"{commit_hash}"' if commit_hash else 'None'},
}}'''

    # Replace VERSION_INFO block
    import re
    content = re.sub(r'VERSION_INFO = \{[^}]+\}', version_info_block, content, flags=re.DOTALL)

    # Write updated content
    with open(version_info_path, 'w') as f:
        f.write(content)

    print(f"Updated version_info.py: v{version} (commit: {commit_hash or 'unknown'})")

def ensure_scribe_player_exists():
    """Ensure ScribePlayer exists before building the engine."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check for ScribePlayer with correct platform extension
    if sys.platform.startswith('win'):
        player_name = 'ScribePlayer.exe'
    else:
        player_name = 'ScribePlayer'

    player_path = os.path.join(script_dir, 'dist_tools', player_name)

    if not os.path.exists(player_path):
        print(f"{player_name} not found. Building it first...")
        build_player_script = os.path.join(script_dir, 'build_player.py')

        if os.path.exists(build_player_script):
            try:
                result = subprocess.run([sys.executable, build_player_script],
                                      capture_output=True, text=True, cwd=script_dir)
                if result.returncode != 0:
                    print(f"Failed to build {player_name}: {result.stderr}")
                    return False
                print(f"{player_name} built successfully!")
            except Exception as e:
                print(f"Error building {player_name}: {e}")
                return False
        else:
            print(f"Error: build_player.py not found at {build_player_script}")
            return False
    else:
        print(f"{player_name} found, proceeding with engine build...")

    return True

def build_engine_executable():
    # Update version info before building
    update_version_info()

    # Ensure ScribePlayer.exe exists first
    if not ensure_scribe_player_exists():
        print("Cannot proceed with engine build without ScribePlayer.exe")
        return False

    # Determine platform for naming
    if sys.platform.startswith('linux'):
        platform_suffix = 'linux'
    elif sys.platform.startswith('win'):
        platform_suffix = 'windows'
    elif sys.platform.startswith('darwin'):  # macOS
        platform_suffix = 'macos'
    else:
        platform_suffix = 'unknown'

    # Determine the base directory of the project
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Check for command line argument to determine build type
    if len(sys.argv) > 1 and sys.argv[1] == 'gui':
        print("Building GUI Scribe Engine executable...")
        build_type = 'gui'
        main_script = 'gui_launcher.py'
        executable_name = f'scribe-engine-v{version}-{platform_suffix}'
        pyinstaller_options = ['--noconsole']
    else:
        print("Building CLI Scribe Engine executable...")
        build_type = 'cli'
        main_script = 'main_engine.py'
        executable_name = f'scribe-engine-cli-v{version}-{platform_suffix}'
        pyinstaller_options = []

    main_script_path = os.path.join(script_dir, main_script)

    # Define paths to include
    main_engine_path = os.path.join(script_dir, 'main_engine.py')
    gui_launcher_path = os.path.join(script_dir, 'gui_launcher.py')
    app_path = os.path.join(script_dir, 'app.py')
    engine_dir = os.path.join(script_dir, 'engine')
    templates_dir = os.path.join(script_dir, 'templates')
    static_dir = os.path.join(script_dir, 'static')
    game_server_path = os.path.join(script_dir, 'game_server.py')
    game_server_wrapper_path = os.path.join(script_dir, 'game_server_wrapper.py')
    config_manager_path = os.path.join(script_dir, 'config_manager.py')
    loading_window_path = os.path.join(script_dir, 'loading_window.py')
    version_info_path = os.path.join(script_dir, 'version_info.py')
    update_checker_path = os.path.join(script_dir, 'update_checker.py')

    # ScribePlayer path (to embed as resource)
    if sys.platform.startswith('win'):
        player_name = 'ScribePlayer.exe'
    else:
        player_name = 'ScribePlayer'
    scribe_player_path = os.path.join(script_dir, 'dist_tools', player_name)

    # PyInstaller arguments
    pyinstaller_args = [
        main_script_path,
        '--onefile',
        f'--name={executable_name}',
        f'--icon={script_dir}/SE_icon.png',

        # Add Python source files that are imported dynamically or needed
        f'--add-data={main_engine_path}{os.pathsep}.',
        f'--add-data={gui_launcher_path}{os.pathsep}.',
        f'--add-data={app_path}{os.pathsep}.',
        f'--add-data={game_server_path}{os.pathsep}.',
        f'--add-data={game_server_wrapper_path}{os.pathsep}.',
        f'--add-data={config_manager_path}{os.pathsep}.',
        f'--add-data={loading_window_path}{os.pathsep}.',
        f'--add-data={version_info_path}{os.pathsep}.',
        f'--add-data={update_checker_path}{os.pathsep}.',

        # Add directories
        f'--add-data={engine_dir}{os.pathsep}engine',
        f'--add-data={templates_dir}{os.pathsep}templates',
        f'--add-data={static_dir}{os.pathsep}static',

        # Embed ScribePlayer.exe as resource
        f'--add-data={scribe_player_path}{os.pathsep}resources',

        # Hidden imports for modules that PyInstaller might miss
        '--hidden-import=flask',
        '--hidden-import=jinja2',
        '--hidden-import=werkzeug',
        '--hidden-import=pywebview',
        '--hidden-import=pywebview.platforms.qt',
        '--hidden-import=qtpy',
        '--hidden-import=qtpy.QtCore',
        '--hidden-import=qtpy.QtGui',
        '--hidden-import=qtpy.QtWidgets',

        # Specify where to put the dist and build folders
        '--distpath=./dist_engine',
        '--workpath=./build_engine',
        '--specpath=./spec_engine',
    ]

    # Add conditional options (like --noconsole for GUI)
    pyinstaller_args.extend(pyinstaller_options)

    PyInstaller.__main__.run(pyinstaller_args)

    print(f"Scribe Engine {build_type} build completed. Executable can be found in the 'dist_engine' directory.")

if __name__ == '__main__':
    build_engine_executable()

